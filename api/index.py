from fastapi import FastAPI
import asyncio
import logging
from .controllers.usercontroller import router as user_router
from .controllers.apicontroller import router as api_router
from .services.verify_emails import verify_emails
# from .services.google_sheets_utils import move_rows_based_on_email, remove_duplicate_rows
from .config import EMAIL_COLUMN, SHEETS_TO_CHECK

# Initialize the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(user_router)
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting the FastAPI application")
    asyncio.create_task(periodic_verification())
    # asyncio.create_task(sort_and_remove_duplicate())

async def periodic_verification():
    while True:
        logger.info("Starting periodic verification cycle")
        for sheet_name in SHEETS_TO_CHECK:
            logger.info(f"Checking sheet: {sheet_name}")
            try:
                await verify_emails(sheet_name)
            except Exception as e:
                logger.error(f"Error during verification for sheet {sheet_name}: {e}")
        logger.info("Completed periodic verification cycle")
        await asyncio.sleep(60)  # Run every 5 minutes

# async def sort_and_remove_duplicate():
#     while True:
#         logger.info("Starting sort and remove duplicate cycle")
#         try:
#             # Run in an executor to avoid blocking the event loop with synchronous code
#             await asyncio.to_thread(move_rows_based_on_email)
#             await asyncio.to_thread(remove_duplicate_rows)
#         except Exception as e:
#             logger.error(f"Error during sorting and removing duplicates: {e}")
#         logger.info("Completed sort and remove duplicate cycle")
#         await asyncio.sleep(60)  # Run every hour
