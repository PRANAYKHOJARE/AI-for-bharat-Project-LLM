from typing import Any
from strands.types.tools import ToolResult, ToolUse
import boto3
import uuid

TOOL_SPEC = {
    "name": "create_booking",
    "description": "Create a new booking at restaurant_name",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
                "hour": {"type": "string"},
                "restaurant_name": {"type": "string"},
                "guest_name": {"type": "string"},
                "num_guests": {"type": "integer"}
            },
            "required": ["date","hour","restaurant_name","guest_name","num_guests"]
        }
    }
}

def create_booking(tool: ToolUse, **kwargs: Any) -> ToolResult:
    kb_name = 'restaurant-assistant'
    dynamodb = boto3.resource('dynamodb')
    smm_client = boto3.client('ssm')
    table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)
    table = dynamodb.Table(table_name["Parameter"]["Value"])

    tool_use_id = tool["toolUseId"]
    date = tool["input"]["date"]
    hour = tool["input"]["hour"]
    restaurant_name = tool["input"]["restaurant_name"]
    guest_name = tool["input"]["guest_name"]
    num_guests = tool["input"]["num_guests"]

    try:
        booking_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'booking_id': booking_id,
                'restaurant_name': restaurant_name,
                'date': date,
                'name': guest_name,
                'hour': hour,
                'num_guests': num_guests
            }
        )
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f"Reservation created with booking id: {booking_id}"}]
        }
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": str(e)}]
        }
