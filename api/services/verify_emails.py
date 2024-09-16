import httpx
import asyncio
import logging
from api.config import EMAIL_COLUMN, VERIFIED_SHEET_NAME
from api.services.google_sheets_utils import get_sheet_data, update_sheet_data, delete_sheet_rows

# Configure logging
logger = logging.getLogger(__name__)

async def verify_emails(sheet_name: str):
    logger.info(f"Starting verification for sheet: {sheet_name}")
    
    data = get_sheet_data(sheet_name)
    if not data:
        logger.warning(f"No data found in sheet: {sheet_name}")
        return

    headers = data[0]
    email_col_index = headers.index(EMAIL_COLUMN) if EMAIL_COLUMN in headers else None

    if email_col_index is None:
        logger.error(f"No column with header '{EMAIL_COLUMN}' found in sheet: {sheet_name}")
        return

    rows_to_move = []
    rows_to_delete = []

    rows = data[1:]  # Remove header row
    batch_size = 100

    logger.info(f"Processing {len(rows)} rows in batches of {batch_size}")

    timeout = httpx.Timeout(30.0)  # 30 seconds timeout
    async with httpx.AsyncClient(timeout=timeout) as client:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            requests_list = [f"https://headless-webfix.vercel.app/verify-email?email={row[email_col_index]}" for row in batch if row[email_col_index]]

            try:
                responses = await asyncio.gather(*(client.get(url) for url in requests_list))
                logger.info(f"Batch {i // batch_size + 1} of {len(rows) // batch_size + 1} processed.")
            except httpx.RequestError as e:
                logger.error(f"Error during batch processing: {e}")
                continue  # Skip the current batch and move to the next

            for index, response in enumerate(responses):
                try:
                    logger.debug(f"Response from URL {requests_list[index]}: {response.text}")
                    email_data = response.json()
                    exists = email_data.get("account_exists", False)
                    if exists:
                        rows_to_move.append(batch[index])
                    # Use 'i + 1 + index' to account for header and zero-based indexing
                    rows_to_delete.append(i + 1 + index)
                except ValueError as e:
                    logger.error(f"Error parsing response for URL {requests_list[index]}: {e}")

    if rows_to_move:
        update_sheet_data(VERIFIED_SHEET_NAME, rows_to_move)
        logger.info(f"Moved {len(rows_to_move)} rows to {VERIFIED_SHEET_NAME}.")

    # Delete all processed rows from the original sheet
    if rows_to_delete:
        delete_sheet_rows(sheet_name, sorted(rows_to_delete, reverse=True))
        logger.info(f"Deleted {len(rows_to_delete)} rows from {sheet_name}.")
