import json
import base64
from typing import Dict, Any
from fastapi.testclient import TestClient
from .api import app

def handle_sqs_event(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handle SQS queue events
    
    This function processes SQS messages that may contain:
    1. Regular SQS messages
    2. API Gateway v1 events (from POST integration)
    3. API Gateway v2 events (from POST integration)
    
    Args:
        event: The SQS event data
        context: The Lambda context object
        
    Returns:
        dict: Response object
    """
    print("Processing SQS event")
    
    processed_messages = []
    
    for record in event.get('Records', []):
        if record.get('eventSource') == 'aws:sqs':
            message_body = record.get('body', '')
            message_id = record.get('messageId', 'unknown')
            
            print(f"Processing SQS message {message_id}: {message_body}")
            
            # Try to parse JSON message body
            try:
                parsed_body = json.loads(message_body)
                
                # Check if this is an API Gateway to SQS message
                if is_api_gateway_sqs_message(parsed_body):
                    print(f"Detected API Gateway to SQS message: {parsed_body.get('source', 'unknown')}")
                    result = process_api_gateway_sqs_message(parsed_body, message_id)
                    processed_messages.append(result)
                else:
                    # Regular SQS message
                    processed_messages.append({
                        'messageId': message_id,
                        'body': parsed_body,
                        'status': 'processed'
                    })
                    
            except json.JSONDecodeError:
                processed_messages.append({
                    'messageId': message_id,
                    'body': message_body,
                    'status': 'processed_as_text'
                })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'SQS messages processed successfully',
            'processed_count': len(processed_messages),
            'messages': processed_messages,
            'request_id': context.aws_request_id
        })
    }

def is_api_gateway_sqs_message(message_body: Dict[str, Any]) -> bool:
    """
    Check if the SQS message is from API Gateway integration
    
    Args:
        message_body: Parsed SQS message body
        
    Returns:
        bool: True if it's an API Gateway to SQS message
    """
    return (
        isinstance(message_body, dict) and 
        'source' in message_body and 
        message_body['source'] in ['ApiGatewayV1SQSLambda', 'HttpApiV2SQSLambda']
    )

def process_api_gateway_sqs_message(message_body: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Process API Gateway to SQS message by reconstructing the HTTP request
    and processing it through FastAPI TestClient
    
    Args:
        message_body: Parsed SQS message body
        message_id: SQS message ID
        
    Returns:
        dict: Processing result
    """
    source = message_body.get('source', 'unknown')
    
    try:
        if source == 'ApiGatewayV1SQSLambda':
            return process_api_gateway_v1_sqs_message(message_body, message_id)
        elif source == 'HttpApiV2SQSLambda':
            return process_api_gateway_v2_sqs_message(message_body, message_id)
        else:
            return {
                'messageId': message_id,
                'body': message_body,
                'status': 'unknown_source',
                'source': source
            }
    except Exception as e:
        print(f"Error processing API Gateway SQS message {message_id}: {str(e)}")
        return {
            'messageId': message_id,
            'body': message_body,
            'status': 'error',
            'error': str(e)
        }

def process_api_gateway_v1_sqs_message(message_body: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Process API Gateway v1 to SQS message
    
    Args:
        message_body: Parsed SQS message body
        message_id: SQS message ID
        
    Returns:
        dict: Processing result
    """
    print(f"Processing API Gateway v1 SQS message: {message_id}")
    
    # Extract the original request data
    json_payload = message_body.get('jsonPayload', {})
    base64_payload = message_body.get('base64payload')
    content_type = message_body.get('contentType', 'application/json')
    
    # Determine the request body
    if base64_payload:
        # Decode base64 payload
        try:
            request_body = base64.b64decode(base64_payload).decode('utf-8')
        except Exception as e:
            print(f"Error decoding base64 payload: {e}")
            request_body = base64_payload
    else:
        # Use JSON payload
        request_body = json.dumps(json_payload) if json_payload else ""
    
    # Create TestClient and make the request
    with TestClient(app) as client:
        try:
            # Make POST request to webhook endpoint
            response = client.post(
                "/webhook",
                content=request_body,
                headers={"Content-Type": content_type}
            )
            
            return {
                'messageId': message_id,
                'body': message_body,
                'status': 'processed_via_fastapi',
                'source': 'ApiGatewayV1SQSLambda',
                'response_status': response.status_code,
                'response_body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            print(f"Error making FastAPI request: {e}")
            return {
                'messageId': message_id,
                'body': message_body,
                'status': 'fastapi_error',
                'source': 'ApiGatewayV1SQSLambda',
                'error': str(e)
            }

def process_api_gateway_v2_sqs_message(message_body: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Process API Gateway v2 to SQS message
    
    Args:
        message_body: Parsed SQS message body
        message_id: SQS message ID
        
    Returns:
        dict: Processing result
    """
    print(f"Processing API Gateway v2 SQS message: {message_id}")
    
    # Extract the original request data
    request_body = message_body.get('MessageBody', '')
    
    # Create TestClient and make the request
    with TestClient(app) as client:
        try:
            # Make POST request to webhook endpoint
            response = client.post(
                "/webhook",
                content=request_body,
                headers={"Content-Type": "application/json"}
            )
            
            return {
                'messageId': message_id,
                'body': message_body,
                'status': 'processed_via_fastapi',
                'source': 'HttpApiV2SQSLambda',
                'response_status': response.status_code,
                'response_body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            print(f"Error making FastAPI request: {e}")
            return {
                'messageId': message_id,
                'body': message_body,
                'status': 'fastapi_error',
                'source': 'HttpApiV2SQSLambda',
                'error': str(e)
            }
