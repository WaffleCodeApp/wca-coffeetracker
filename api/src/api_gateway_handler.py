import os
from typing import Dict, Any
from mangum import Mangum
from .api import app

# Create Mangum adapter for AWS Lambda
handler = Mangum(
    app,
    lifespan="off",
    api_gateway_base_path=f"/{os.getenv('PIPELINE_ID') or ''}",
)


def is_api_gateway_event(event: Dict[str, Any]) -> bool:
    """
    Check if the event is from API Gateway (v1 or v2)
    
    Args:
        event: The event data
        
    Returns:
        bool: True if it's an API Gateway event
    """
    # API Gateway v1 (REST API) has 'httpMethod' and 'path'
    if 'httpMethod' in event and 'path' in event:
        return True
    
    # API Gateway v2 (HTTP API) has 'requestContext' with 'http'
    if 'requestContext' in event and 'http' in event.get('requestContext', {}):
        return True
    
    # API Gateway v2 (HTTP API) can also have 'version' and 'routeKey'
    if 'version' in event and 'routeKey' in event:
        return True
    
    return False

def handle_api_gateway_event(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle API Gateway events (v1 or v2)
    
    Args:
        event: The API Gateway event data
        context: The Lambda context object
        
    Returns:
        dict: Response object
    """
    print("Processing API Gateway event")
    return handler(event, context)
