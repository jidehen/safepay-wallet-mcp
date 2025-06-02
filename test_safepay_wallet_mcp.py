import asyncio
import logging
from model.payment_method_request import PaymentMethodRequest
from server.safepay_wallet_mcp_server import get_payment_methods

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_get_payment_methods():
    """Test getting payment methods for different users."""
    # Test valid user
    request = PaymentMethodRequest(user_id="user1")
    response = await get_payment_methods(request)
    logger.info(f"Payment methods for user1: {response}")
    
    # Test invalid user
    request = PaymentMethodRequest(user_id="invalid_user")
    response = await get_payment_methods(request)
    logger.info(f"Payment methods for invalid user: {response}")

async def main():
    """Run all tests."""
    logger.info("Starting SafePayWallet MCP tests")
    
    try:
        await test_get_payment_methods()
        logger.info("All tests completed successfully")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 