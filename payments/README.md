# Serverless Function with HTTP API to Queue Integration

A Python AWS Lambda function built with FastAPI that can handle HTTP API Gateway events (v1 and v2) that are channeled through SQS to reduce risk of data loss. Meant for handling sensitive webhooks, like payment processing, inbound text messages, message delivery webhooks, or any other triggers from 3rd party services where robustness is important.

## Features

- **FastAPI Integration**: Modern, fast web framework for building APIs
- **Dual Event Support**: Handles both API Gateway and SQS events
- **API Gateway v1 & v2**: Supports both REST API and HTTP API formats
- **Package Management**: Uses `pip` with `requirements.txt` for dependency management
- **Docker Ready**: Containerized for easy deployment

## Endpoints

- `GET /` - Root endpoint with health status
- `GET /health` - Health check endpoint
- `POST /webhook` - Webhook example endpoint for processing events
- `GET /api/{path:path}` - Catch-all endpoint for API Gateway routes

## Event Handling

### POST Integration with FIFO Queue Processing

**Important**: There is a special POST integration configuration where API Gateway (both v1 and v2) does NOT call the Lambda function directly. Instead:

1. **POST requests** to API Gateway are automatically converted to SQS messages
2. **FIFO Queue Processing**: Messages are sent to a FIFO SQS queue to ensure webhooks are caught and processed in order
3. **Message Structure**: The SQS messages contain the original HTTP request data:
   - **API Gateway v1**: `{"source":"ApiGatewayV1SQSLambda","jsonPayload":<original_request>}`
   - **API Gateway v2**: `{"source":"HttpApiV2SQSLambda","MessageBody":<original_request>}`
4. **Lambda Processing**: When the Lambda function receives these SQS messages, it reconstructs the original HTTP request and processes it through FastAPI's TestClient

This architecture ensures that webhooks are reliably captured and processed even during high traffic or temporary Lambda cold starts.

### Generic HTTP Requests (API Gateway Events)
The function automatically detects and routes API Gateway events (both v1 and v2) to the FastAPI application using the Mangum adapter. It's possible to trigger the lambda by bypassing the queue.

### SQS Events
SQS events are processed separately, with each message logged and returned in the response. The function attempts to parse JSON message bodies and handles both JSON and text messages.


## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run locally (for testing FastAPI endpoints):
   ```bash
   cd src
   fastapi dev handler.py
   ```

## Deployment

The function is containerized and ready for deployment to AWS Lambda using the provided Dockerfile.

### Infrastructure Requirements

This service requires the following AWS infrastructure (deployed via CloudFormation):

- **VPC**: (optional) Network infrastructure
- **ECR Repository**: Container image storage for the custom lambda container
- **API Gateway**: HTTP API v2 or REST API v1 with IAM or JWT auth
- **Cognito User Pool**: User authentication
- **CodePipeline**: CICD pipeline
- **SSM Parameters**: Configuration storage

### Deployment Process

1. **Code Push**: Push code to the configured Git repository
2. **Build**: CodePipeline triggers CodeBuild to create Docker image
3. **Deploy**: Image is pushed to ECR and deployed to ECS
4. **Health Check**: Load balancer verifies service health

### Configuration

The service automatically configures itself using:
- **SSM Parameters**: Retrieved during startup
- **Environment Variables**: Set by CICD pipeline
- **Cognito Configuration**: Fetched from SSM parameters

## Infrastructure Integration

### SSM Parameters

The service retrieves configuration from SSM Parameter Store:

- `/{DEPLOYMENT_ID}/auth/user_pool_ref` - Cognito User Pool ID
- `/{DEPLOYMENT_ID}/cdn/{PIPELINE_ID}/auth_user_pool_client_id` - Cognito Client ID
- `/{DEPLOYMENT_ID}/ecs/{PIPELINE_ID}/albDnsName` - Load Balancer URL

### Cognito Integration

- **Token Verification**: Uses JWT verification with Cognito public keys
- **User Extraction**: Parses user information from verified tokens
- **Security**: Validates token signature, expiration, and audience

## Security

- **WAF Protection**: AWS WAF with managed rule sets
- **IAM Authentication**: API Gateway-level authentication
- **Token Verification**: JWT signature validation
- **Network Security**: VPC with private subnets
- **Secrets Management**: AWS Secrets Manager integration

## Monitoring

- **CloudWatch Logs**: Application logs with structured logging
- **Health Checks**: Load balancer health monitoring
- **Alarms**: CPU, memory, and error rate monitoring
- **Metrics**: Custom application metrics

## Dependencies

- FastAPI: Web framework
- Mangum: ASGI adapter for AWS Lambda
- awslambdaric: AWS Lambda runtime interface client
- httpx: HTTP client for FastAPI TestClient (used for processing API Gateway events from SQS)