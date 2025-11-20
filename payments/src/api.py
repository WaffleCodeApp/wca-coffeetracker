import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.id_token import IdTokenWithJose

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="My Function API",
    description="AWS Lambda function with FastAPI for HTTP API Queue Trigger",
    version="0.1.0",
    root_path=f"/Prod/{os.getenv('PIPELINE_ID')}",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins for better security
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhook")
async def webhook(request: Request):
    """Webhook example endpoint for processing various events"""
    import json
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {"raw_body": body.decode('utf-8')}
    
    return {
        "message": "Webhook received",
        "data": data,
        "headers": dict(request.headers)
    }

@app.get("/hello_world")
async def get_hello_world(request: Request) -> str:
    logger.info("\n" + "=" * 80)
    logger.info("/hello_world endpoint called")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Frontend sends:
    # - Authorization: Bearer <access_token> (for API authorization, not used here)
    # - X-IdToken: <id_token> (for user identification, this is what we need)
    id_token = request.headers.get("X-IdToken")
    
    if not id_token:
        logger.error("No ID token provided in X-IdToken header")
        logger.error(f"Available headers: {list(request.headers.keys())}")
        raise HTTPException(status_code=401, detail="No ID token provided. Expected X-IdToken header.")
    
    logger.info(f"ID token received (length: {len(id_token)})")
    logger.info(f"ID token preview: {id_token[:50]}...{id_token[-20:] if len(id_token) > 70 else ''}")
    
    # Log Cognito configuration
    logger.info("Cognito configuration:")
    logger.info(f"  _cognito_region: {IdTokenWithJose._cognito_region}")
    logger.info(f"  _cognito_user_pool_id: {IdTokenWithJose._cognito_user_pool_id}")
    logger.info(f"  _cognito_client_ids: {IdTokenWithJose._cognito_client_ids}")
    logger.info(f"  _aws_region: {IdTokenWithJose._aws_region}")
    logger.info(f"  _deployment_id: {IdTokenWithJose._deployment_id}")
    
    try:
        logger.info("Attempting to verify ID token...")
        user = await IdTokenWithJose.get_user(id_token)
        
        if not user:
            logger.error("get_user() returned None")
            logger.error("This could mean:")
            logger.error("  - Token verification failed (check logs above)")
            logger.error("  - token_use is not 'id'")
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired token. Check server logs for details."
            )
        
        logger.info(f"Successfully authenticated user: {user.email} (id: {user.id})")
        logger.info("=" * 80 + "\n")
        return f"Hello, {user.email}"
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during authentication: {str(e)}"
        )
