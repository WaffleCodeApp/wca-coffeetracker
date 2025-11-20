import os
import json
import logging
from typing import Any
from .parameters import ParametersWithSSM
from .id_token import IdTokenWithJose

logger = logging.getLogger(__name__)


async def initialize() -> None:
    # Set environment (synchronous method, don't await)
    try:
        ParametersWithSSM.set_environment(
            aws_region=os.getenv("AWS_REGION"), deployment_id=os.getenv("DEPLOYMENT_ID")
        )
    except Exception as e:
        logger.warning(f"⚠️ Error setting ParametersWithSSM environment: {e}")
        # Continue anyway - some operations might still work
    
    # Initialize SSM client
    try:
        await ParametersWithSSM.initialize()
    except Exception as e:
        logger.warning(f"⚠️ Error initializing SSM client: {e}")
        logger.warning("⚠️ SSM parameter lookups will fail, but server will continue")
        # Continue anyway - we'll handle None values later
    
    # Fetch Cognito user pool ID from SSM
    cognito_user_pool_id = None
    try:
        cognito_user_pool_id = await ParametersWithSSM.get_congito_user_pool_id()
        if not cognito_user_pool_id:
            logger.warning("⚠️ Could not retrieve cognito_user_pool_id from SSM")
    except Exception as e:
        logger.warning(f"⚠️ Error retrieving cognito_user_pool_id: {e}")
    
    # Cognito region is typically the same as AWS region
    cognito_region = os.getenv("AWS_REGION")
    
    # Parse INFRASTRUCTURE_CONFIG_JSON to find frontend services with auth enabled
    infrastructure_config_json = os.getenv("INFRASTRUCTURE_CONFIG_JSON")
    cognito_client_ids: list[str] = []
    
    logger.info("=" * 80)
    logger.info("INFRASTRUCTURE_CONFIG_JSON parsing:")
    logger.info(f"  INFRASTRUCTURE_CONFIG_JSON is set: {infrastructure_config_json is not None}")
    if infrastructure_config_json:
        logger.info(f"  INFRASTRUCTURE_CONFIG_JSON length: {len(infrastructure_config_json)}")
        logger.info(f"  INFRASTRUCTURE_CONFIG_JSON preview (first 500 chars): {infrastructure_config_json[:500]}")
    logger.info("=" * 80)
    
    if infrastructure_config_json:
        try:
            logger.info("Parsing INFRASTRUCTURE_CONFIG_JSON to find frontend services with auth enabled...")
            config: dict[str, Any] = json.loads(infrastructure_config_json)
            
            logger.info(f"Parsed JSON keys: {list(config.keys())}")
            
            # The structure is directly envFeatures and services at top level (not wrapped in "resources")
            # This matches the frontend's VITE_BUILD_ENV_VARS_JSON structure
            services = config.get("services", {})
            env_features = config.get("envFeatures", {})
            
            logger.info(f"Found {len(services)} services in infrastructure config")
            logger.info(f"Service names: {list(services.keys())}")
            
            # Log all services for debugging
            for service_name, service in services.items():
                logger.info(f"  Service '{service_name}': stackType={service.get('stackType')}, auth={service.get('auth')}")
            
            # Find all STATIC_FRONTEND services with auth enabled
            frontend_services: list[str] = []
            for service_name, service in services.items():
                stack_type = service.get("stackType")
                logger.info(f"Checking service '{service_name}': stackType={stack_type}")
                
                if stack_type == "STATIC_FRONTEND":
                    auth = service.get("auth", {})
                    auth_enabled = auth and (auth.get("enabled") is not False)
                    logger.info(f"  Service '{service_name}' is STATIC_FRONTEND, auth={auth}, auth_enabled={auth_enabled}")
                    
                    # Check if auth is enabled (can be explicit True or just present)
                    if auth_enabled:
                        frontend_services.append(service_name)
                        logger.info(f"✅ Found frontend service with auth enabled: {service_name}")
                    else:
                        logger.info(f"  Service '{service_name}' has auth disabled or missing")
                else:
                    logger.debug(f"  Service '{service_name}' is not STATIC_FRONTEND (it's {stack_type})")
            
            logger.info(f"Found {len(frontend_services)} frontend service(s) with auth enabled: {frontend_services}")
            
            # Get cognito_client_id for each frontend service
            for service_name in frontend_services:
                try:
                    logger.info(f"Fetching client_id for frontend service '{service_name}'...")
                    client_id = await ParametersWithSSM.get_cognito_client_id(service_name)
                    if client_id:
                        cognito_client_ids.append(client_id)
                        logger.info(f"✅ Retrieved client_id for service '{service_name}': {client_id}")
                    else:
                        logger.warning(f"⚠️ Could not retrieve client_id for service '{service_name}' (returned None)")
                except Exception as e:
                    logger.error(f"❌ Error retrieving client_id for service '{service_name}': {e}", exc_info=True)
            
            if not cognito_client_ids:
                logger.warning("⚠️ No cognito_client_ids found from frontend services")
            else:
                logger.info(f"✅ Successfully retrieved {len(cognito_client_ids)} client ID(s): {cognito_client_ids}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error parsing INFRASTRUCTURE_CONFIG_JSON: {e}", exc_info=True)
            logger.error(f"  INFRASTRUCTURE_CONFIG_JSON content: {infrastructure_config_json[:1000] if infrastructure_config_json else 'None'}")
            logger.warning("Falling back to single client_id lookup")
        except Exception as e:
            logger.error(f"❌ Error parsing INFRASTRUCTURE_CONFIG_JSON: {e}", exc_info=True)
            logger.warning("Falling back to single client_id lookup")
    else:
        logger.warning("⚠️ INFRASTRUCTURE_CONFIG_JSON not set, cannot find frontend services")
    
    # Fallback: if no client IDs found, try to get one using PIPELINE_ID
    if not cognito_client_ids:
        pipeline_id = os.getenv("PIPELINE_ID")
        if pipeline_id:
            logger.info(f"Fallback: trying to get client_id for PIPELINE_ID: {pipeline_id}")
            try:
                client_id = await ParametersWithSSM.get_cognito_client_id(pipeline_id)
                if client_id:
                    cognito_client_ids.append(client_id)
                    logger.info(f"Retrieved client_id for PIPELINE_ID '{pipeline_id}': {client_id}")
            except Exception as e:
                logger.error(f"Error retrieving client_id for PIPELINE_ID '{pipeline_id}': {e}", exc_info=True)
    
    if not cognito_client_ids:
        logger.warning("⚠️ No cognito_client_ids found! Token verification will fail.")
        logger.warning("⚠️ Check INFRASTRUCTURE_CONFIG_JSON and SSM parameters. Server will continue to boot.")
    
    # Set environment for IdTokenWithJose (synchronous method, don't await)
    # This will log warnings but not raise exceptions
    try:
        IdTokenWithJose.set_environment(
            aws_region=os.getenv("AWS_REGION"),
            deployment_id=os.getenv("DEPLOYMENT_ID"),
            cognito_region=cognito_region,
            cognito_user_pool_id=cognito_user_pool_id,
            cognito_client_ids=cognito_client_ids,
        )
    except Exception as e:
        logger.error(f"❌ Error setting IdTokenWithJose environment: {e}", exc_info=True)
        logger.error("⚠️ Server will continue, but token verification will fail")
