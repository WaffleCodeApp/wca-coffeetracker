from fastapi import FastAPI, Request
from infrastructure.id_token import IdTokenWithJose

# Create FastAPI application
app = FastAPI(
    title="HTTP API Queue Trigger",
    description="AWS Lambda function with FastAPI for HTTP API Queue Trigger",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from FastAPI Lambda!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

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

@app.get("/api/{path:path}")
async def api_catch_all(path: str, request: Request):
    """Catch-all endpoint for API Gateway routes"""
    user = await IdTokenWithJose.get_user(request.headers.get("Authorization"))
    return {
        "message": f"API endpoint: /{path}",
        "method": request.method,
        "query_params": dict(request.query_params),
        "path": path,
        "user": user
    }
