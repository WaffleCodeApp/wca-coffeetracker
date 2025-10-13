from typing import Any
import requests
from jose import jwt
from .user import User


class IdTokenWithJose:
    _aws_region: str | None = None
    _deployment_id: str | None = None
    _cognito_region: str | None = None
    _cognito_user_pool_id: str | None = None
    _cognito_client_id: str | None = None

    @classmethod
    def set_environment(
        cls,
        aws_region: str | None,
        deployment_id: str | None,
        cognito_region: str | None,
        cognito_user_pool_id: str | None,
        cognito_client_id: str | None,
    ) -> None:
        if aws_region is None:
            print("aws_region is None, probably an issue with the env vars")
            raise Exception("AWS region is None")
        cls._aws_region = aws_region
        if deployment_id is None:
            print("deployment_id is None, probably an issue with the env vars")
            raise Exception("deployment_id is None")
        cls._deployment_id = deployment_id
        if cognito_region is None:
            print("cognito_region is None, probably an issue with the env vars")
            raise Exception("cognito_region is None")
        cls._cognito_region = cognito_region
        if cognito_user_pool_id is None:
            print("cognito_user_pool_id is None, probably an issue with the env vars")
            raise Exception("cognito_user_pool_id is None")
        cls._cognito_user_pool_id = cognito_user_pool_id
        if cognito_client_id is None:
            print("cognito_client_id is None, probably an issue with the env vars")
            raise Exception("cognito_client_id is None")
        cls._cognito_client_id = cognito_client_id

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
        keys = cls.get_cognito_jwks()
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        if not kid:
            print("IdTokenWithJose::verify_id_token: no kid found in token header")
            raise ValueError("Invalid token: No key ID found in token header.")

        # Find the key matching the kid in the token header
        key = next((k for k in keys if k["kid"] == kid), None)
        if key is None:
            print(
                "IdTokenWithJose::verify_id_token: no key found in jwks.json for kid",
                kid,
            )
            raise ValueError("Public key not found in jwks.json for kid: " + kid)

        try:
            # This verifies the signature as well as checks expiration etc.
            claims = jwt.decode(
                id_token,
                key,
                algorithms=["RS256"],
                audience=cls._cognito_client_id,  # Remove or adjust if needed
                issuer=f"https://cognito-idp.{cls._cognito_region}.amazonaws.com/{cls._cognito_user_pool_id}",
                options={"verify_at_hash": False},  # Skip at_hash verification
            )
        except Exception as e:
            print("IdTokenWithJose::verify_id_token: error", e)
            raise ValueError("Token verification failed.") from e

        return claims

    @classmethod
    async def get_user(
        cls,
        cognito_id_token: str | None,
    ) -> User | None:
        if cognito_id_token:
            try:
                claims = cls.verify_id_token(cognito_id_token)
            except Exception as e:
                print("IdTokenWithJose::request_to_user: error verifying id token", e)
                return None

            if claims.get("token_use") != "id":
                return None

            return User(
                id=claims.get("sub", ""),
                email=claims.get("email", ""),
                name=claims.get("cognito:username", ""),
                role=claims.get("custom:role", ""),
                customer_id=claims.get("custom:organization", ""),
                picture=claims.get("picture", ""),
                phone_number=claims.get("phone_number", ""),
                enabled=claims.get("email_verified", False),
            )
