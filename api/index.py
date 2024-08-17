# api/index.py
from fastapi import FastAPI
import asyncio
import logging
from .controllers.usercontroller import router as user_router
from .controllers.apicontroller import router as api_router
from .services.apiservice import verify_emails
from .services.externalfunction import get_sheet_data, update_sheet_data, delete_sheet_rows
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

async def periodic_verification():
    while True:
        logger.info("Starting periodic verification cycle")
        for sheet_name in SHEETS_TO_CHECK:
            logger.info(f"Checking sheet: {sheet_name}")
            await verify_emails(sheet_name, get_sheet_data, update_sheet_data, delete_sheet_rows)
        logger.info("Completed periodic verification cycle")
        await asyncio.sleep(60)  # Run every hour
