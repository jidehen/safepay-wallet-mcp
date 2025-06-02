import logging
from typing import List, Dict, Any
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.payment_method_request import PaymentMethodRequest
from model.payment_method_response import PaymentMethodResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock user data with their payment methods
MOCK_USERS = {
    "user1": {
        "name": "John Doe",
        "payment_methods": [
            {
                "card_id": "card_001",
                "type": "credit",
                "brand": "Chase Freedom",
                "last4": "1234",
                "nickname": "Freedom Card"
            },
            {
                "card_id": "card_002",
                "type": "credit",
                "brand": "Chase Sapphire Preferred",
                "last4": "5678",
                "nickname": "Sapphire Card"
            }
        ]
    },
    "user2": {
        "name": "Jane Smith",
        "payment_methods": [
            {
                "card_id": "card_003",
                "type": "credit",
                "brand": "Chase Freedom Unlimited",
                "last4": "9012",
                "nickname": "Freedom Unlimited"
            }
        ]
    },
    "user3": {
        "name": "Bob Wilson",
        "payment_methods": [
            {
                "card_id": "card_004",
                "type": "credit",
                "brand": "Chase Sapphire Reserve",
                "last4": "3456",
                "nickname": "Reserve Card"
            },
            {
                "card_id": "card_005",
                "type": "credit",
                "brand": "Chase Freedom",
                "last4": "7890",
                "nickname": "Freedom Card"
            }
        ]
    }
}

# Initialize FastMCP server
mcp = FastMCP("SafePayWallet")

class PaymentMethodError(Exception):
    """Custom exception for payment method errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def get_user_payment_methods(user_id: str) -> List[Dict[str, Any]]:
    """
    Get payment methods for a specific user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        List[Dict[str, Any]]: List of payment methods
        
    Raises:
        PaymentMethodError: If user_id is not found or other errors occur
    """
    logger.info(f"Processing request for user ID: {user_id}")
    
    if not user_id:
        raise PaymentMethodError(
            "No user ID provided",
            "MISSING_USER_ID",
            {"required": "A valid user ID must be provided"}
        )
    
    if user_id not in MOCK_USERS:
        raise PaymentMethodError(
            f"User {user_id} not found",
            "USER_NOT_FOUND",
            {
                "invalid_user_id": user_id,
                "valid_user_ids": list(MOCK_USERS.keys())
            }
        )
    
    methods = MOCK_USERS[user_id]["payment_methods"]
    logger.info(f"Found {len(methods)} payment methods for user {user_id}")
    return methods

async def get_payment_methods(request: PaymentMethodRequest) -> List[PaymentMethodResponse]:
    """
    Get all payment methods for a user.
    
    Args:
        request: The payment method request containing the user ID
        
    Returns:
        List[PaymentMethodResponse]: List of payment methods
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Received request for payment methods: user_id={request.user_id}")
    
    try:
        methods = get_user_payment_methods(request.user_id)
        
        response_methods = [
            PaymentMethodResponse(
                card_id=method["card_id"],
                type=method["type"],
                brand=method["brand"],
                last4=method["last4"],
                nickname=method["nickname"]
            )
            for method in methods
        ]
        
        logger.info(f"[{request_id}] Successfully processed request. Found {len(response_methods)} payment methods")
        return response_methods
        
    except PaymentMethodError as e:
        logger.error(f"[{request_id}] Payment method error: {str(e)}", exc_info=True)
        raise PaymentMethodError(
            e.message,
            e.error_code,
            {
                **e.details,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise PaymentMethodError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# Register MCP tool
@mcp.tool()
async def get_payment_methods_tool(request: PaymentMethodRequest) -> List[PaymentMethodResponse]:
    """MCP tool for getting payment methods."""
    return await get_payment_methods(request)

if __name__ == "__main__":
    logger.info("Starting SafePayWallet MCP server")
    mcp.run() 