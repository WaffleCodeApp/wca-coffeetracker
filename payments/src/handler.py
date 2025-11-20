import asyncio
import json
import os
from typing import Dict, Any
from api_gateway_handler import is_api_gateway_event, handle_api_gateway_event
from sqs_handler import handle_sqs_event
from infrastructure import initialize


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    # Initialize infrastructure components
    loop.run_until_complete(initialize())


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler function for HTTP API Queue Trigger
    
    This function can handle:
    - API Gateway v1 events (REST API)
    - API Gateway v2 events (HTTP API)
    - SQS queue events
    
    Args:
        event: The event data from the trigger
        context: The Lambda context object
        
    Returns:
        dict: Response object with status code and body
    """
    try:
        # Log the incoming event for debugging
        print(f"Received event: {json.dumps(event, default=str)}")
        
        # Check if this is an SQS event
        if 'Records' in event and event.get('Records'):
            return handle_sqs_event(event, context)
        
        # Check if this is an API Gateway event (v1 or v2)
        if is_api_gateway_event(event):
            print("Processing API Gateway event")
            return handle_api_gateway_event(event, context)
        
        # If it's neither SQS nor API Gateway, log and return error
        print(f"Unknown event type: {event.keys()}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Unknown event type',
                'event_keys': list(event.keys())
            })
        }
        
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

