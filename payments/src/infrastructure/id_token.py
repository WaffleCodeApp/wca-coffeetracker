from typing import Any
import logging
import requests
from jose import jwt
from .user import User

logger = logging.getLogger(__name__)


class IdTokenWithJose:
    _aws_region: str | None = None
    _deployment_id: str | None = None
    _cognito_region: str | None = None
    _cognito_user_pool_id: str | None = None
    _cognito_client_ids: list[str] = []

    @classmethod
    def set_environment(
        cls,
        aws_region: str | None,
        deployment_id: str | None,
        cognito_region: str | None,
        cognito_user_pool_id: str | None,
        cognito_client_ids: list[str] | None = None,
    ) -> None:
        logger.info("\n" + "=" * 80)
        logger.info("Setting environment:")
        logger.info(f"  aws_region: {aws_region}")
        logger.info(f"  deployment_id: {deployment_id}")
        logger.info(f"  cognito_region: {cognito_region}")
        logger.info(f"  cognito_user_pool_id: {cognito_user_pool_id}")
        logger.info(f"  cognito_client_ids: {cognito_client_ids}")
        logger.info("=" * 80 + "\n")
        
        # Set values with warnings instead of exceptions to allow server to boot
        if aws_region is None:
            logger.warning("⚠️ aws_region is None, using default 'us-east-1'")
            cls._aws_region = "us-east-1"
        else:
            cls._aws_region = aws_region
            
        if deployment_id is None:
            logger.warning("⚠️ deployment_id is None, using empty string")
            cls._deployment_id = ""
        else:
            cls._deployment_id = deployment_id
            
        if cognito_region is None:
            logger.warning("⚠️ cognito_region is None, using AWS_REGION or default 'us-east-1'")
            cls._cognito_region = aws_region or "us-east-1"
        else:
            cls._cognito_region = cognito_region
            
        if cognito_user_pool_id is None:
            logger.warning("⚠️ cognito_user_pool_id is None - token verification will fail")
            cls._cognito_user_pool_id = None
        else:
            cls._cognito_user_pool_id = cognito_user_pool_id
            
        if not cognito_client_ids or len(cognito_client_ids) == 0:
            logger.warning("⚠️ cognito_client_ids is empty - token verification will fail. Check RUNTIME_JSON and SSM parameters.")
            cls._cognito_client_ids = []
        else:
            cls._cognito_client_ids = cognito_client_ids
            logger.info(f"✅ Environment set successfully with {len(cognito_client_ids)} client ID(s)\n")

    @classmethod
    def get_cognito_jwks(cls):
        url = f"https://cognito-idp.{cls._cognito_region}.amazonaws.com/{cls._cognito_user_pool_id}/.well-known/jwks.json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["keys"]

    @classmethod
    def verify_id_token(cls, id_token: str) -> dict[str, Any]:
        """
        Verifies a Cognito IdToken using the public keys available from Cognito.

        Returns the token's claims if verification succeeds, otherwise raises a ValueError.
        """
        logger.info("verify_id_token: Starting verification...")
        
        # Check if configuration is valid
        if not cls._cognito_user_pool_id:
            raise ValueError("Cognito user pool ID is not configured. Check server logs for initialization errors.")
        
        if not cls._cognito_client_ids or len(cls._cognito_client_ids) == 0:
            raise ValueError("No Cognito client IDs configured. Check RUNTIME_JSON and SSM parameters. See server logs for details.")
        
        # Decode token header to get kid
        try:
            header = jwt.get_unverified_header(id_token)
            logger.info(f"Token header: {header}")
            kid = header.get("kid")
            if not kid:
                logger.error("No 'kid' found in token header")
                raise ValueError("Invalid token: No key ID found in token header.")
            logger.info(f"Token key ID (kid): {kid}")
        except Exception as e:
            logger.error(f"Error decoding token header: {e}", exc_info=True)
            raise ValueError(f"Invalid token: Cannot decode header. {str(e)}") from e

        # Get JWKS from Cognito
        try:
            logger.info("Fetching JWKS from Cognito...")
            keys = cls.get_cognito_jwks()
            logger.info(f"Retrieved {len(keys)} keys from JWKS")
        except Exception as e:
            logger.error(f"Error fetching JWKS: {e}", exc_info=True)
            raise ValueError(f"Cannot fetch JWKS from Cognito: {str(e)}") from e

        # Find the key matching the kid in the token header
        key = next((k for k in keys if k["kid"] == kid), None)
        if key is None:
            available_kids = [k.get("kid") for k in keys]
            logger.error(f"No key found in jwks.json for kid: {kid}")
            logger.error(f"Available kids in JWKS: {available_kids}")
            raise ValueError(f"Public key not found in jwks.json for kid: {kid}")

        # Verify token - try all client IDs
        expected_issuer = f"https://cognito-idp.{cls._cognito_region}.amazonaws.com/{cls._cognito_user_pool_id}"
        logger.info("Verifying token with:")
        logger.info(f"  possible audiences (client_ids): {cls._cognito_client_ids}")
        logger.info(f"  issuer: {expected_issuer}")
        
        # Try each client ID until one works
        last_error: Exception | None = None
        for client_id in cls._cognito_client_ids:
            try:
                logger.info(f"Trying to verify with client_id: {client_id}")
                # This verifies the signature as well as checks expiration etc.
                claims = jwt.decode(
                    id_token,
                    key,
                    algorithms=["RS256"],
                    audience=client_id,
                    issuer=expected_issuer,
                    options={"verify_at_hash": False},  # Skip at_hash verification
                )
                logger.info(f"Token verified successfully with client_id: {client_id}")
                logger.info(f"Token claims: token_use={claims.get('token_use')}, sub={claims.get('sub')}, aud={claims.get('aud')}")
                return claims
            except jwt.ExpiredSignatureError as e:
                logger.error(f"Token expired: {e}")
                raise ValueError("Token has expired.") from e
            except jwt.InvalidAudienceError as e:
                logger.debug(f"Token audience mismatch for client_id {client_id}, trying next...")
                last_error = e
                continue  # Try next client ID
            except jwt.InvalidIssuerError as e:
                logger.error(f"Invalid issuer: {e}")
                logger.error(f"Expected issuer: {expected_issuer}")
                raise ValueError(f"Token issuer mismatch. Expected: {expected_issuer}") from e
            except Exception as e:
                logger.error(f"Token verification error with client_id {client_id}: {type(e).__name__}: {e}", exc_info=True)
                last_error = e
                continue  # Try next client ID
        
        # If we get here, none of the client IDs worked
        logger.error(f"Token verification failed for all {len(cls._cognito_client_ids)} client ID(s)")
        # Try to get token audience for debugging (decode without verification)
        try:
            # Decode without verification to get claims for debugging
            # jose requires a key even when not verifying, so we use the key we already have
            unverified_claims = jwt.decode(
                id_token,
                key,  # Key is still needed for decode, but we disable verification
                algorithms=["RS256"],
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False,
                    "verify_iss": False
                }
            )
            token_aud = unverified_claims.get('aud')
            logger.error(f"Token audience: {token_aud}")
            logger.error(f"Expected audiences: {cls._cognito_client_ids}")
        except Exception as decode_error:
            logger.error(f"Token audience: unknown (could not decode: {decode_error})")
        
        if last_error:
            raise ValueError(f"Token audience mismatch. Token audience does not match any of: {cls._cognito_client_ids}") from last_error
        else:
            raise ValueError(f"Token verification failed for all client IDs: {cls._cognito_client_ids}")

    @classmethod
    async def get_user(
        cls,
        cognito_id_token: str | None,
    ) -> User | None:
        if not cognito_id_token:
            logger.warning("get_user: No token provided")
            return None
            
        try:
            claims = cls.verify_id_token(cognito_id_token)
        except Exception as e:
            logger.error(f"get_user: Error verifying id token: {type(e).__name__}: {e}", exc_info=True)
            return None

        token_use = claims.get("token_use")
        logger.info(f"Token use: {token_use}")
        if token_use != "id":
            logger.error(f"get_user: token_use is '{token_use}', expected 'id'")
            return None

        user = User(
            id=claims.get("sub", ""),
            email=claims.get("email", ""),
            name=claims.get("cognito:username", ""),
            role=claims.get("custom:role", ""),
            customer_id=claims.get("custom:organization", ""),
            picture=claims.get("picture", ""),
            phone_number=claims.get("phone_number", ""),
            enabled=claims.get("email_verified", False),
        )
        logger.info(f"get_user: Created user object for {user.name}")
        return user
