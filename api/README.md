# Serverless Function with HTTP API

A Python AWS Lambda function built with FastAPI that handles HTTP API Gateway events (v1 and v2).

## Features

- **FastAPI Integration**: Modern, fast web framework for building APIs
- **API Gateway v1 & v2**: Supports both REST API and HTTP API formats
- **Package Management**: Uses `pip` with `requirements.txt` for dependency management
- **Docker Ready**: Containerized for easy deployment

## Endpoints

- `GET /` - Root endpoint with health status
- `GET /health` - Health check endpoint
- `GET /api/{path:path}` - Catch-all endpoint for API Gateway routes

## Event Handling

### API Gateway Events
The function automatically detects and routes API Gateway events (both v1 and v2) to the FastAPI application using the Mangum adapter.

This architecture ensures that HTTP requests are reliably processed and routed to the appropriate FastAPI endpoints.

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