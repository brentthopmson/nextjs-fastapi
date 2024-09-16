from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Google Sheets and API configuration
SPREADSHEET_ID = '1y7_yT1OEdkTEeEEk_JCLbAEtPAVH9RKTXiQclkE6ugU'
SERVICE_ACCOUNT_FILE = 'api/credentials.json'
EMAIL_COLUMN_INDEX = 18  # 19th column, 0-based index
VERIFIED_SHEET_NAME = 'VERIFIED'
SHEETS_TO_CHECK = ["OFFICE", "GMAIL", "AOL", "OUTLOOK", "HOTMAIL"]
MOVE_AND_REMOVE_SHEETS_TO_CHECK = ["VERIFIED", "GMAIL", "OUTLOOK", "HOTMAIL", "AOL", "EARTHLINK", "MAIL", "COX", "YAHOO", "PREMIUM"]
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    return service

def get_sheet_id(sheet_name):
    service = get_sheets_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get('sheets', [])
    for sheet in sheets:
        if sheet['properties']['title'] == sheet_name:
            return sheet['properties']['sheetId']
    return None

def get_sheet_data(sheet_name):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=f"{sheet_name}!A:Z").execute()
    return result.get('values', [])

def update_sheet_data(sheet_name, values):
    service = get_sheets_service()
    body = {'values': values}
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A1",
        valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()
    return result

def delete_sheet_rows(sheet_name, row_indices):
    try:
        service = get_sheets_service()
        sheet_id = get_sheet_id(sheet_name)
        if sheet_id is None:
            logger.error(f"Sheet ID not found for sheet: {sheet_name}")
            return
        
        sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_info = next(sheet for sheet in sheet_metadata['sheets'] if sheet['properties']['title'] == sheet_name)
        total_rows = sheet_info['properties']['gridProperties']['rowCount']
        
        # If all rows are to be deleted, first insert an empty row
        if len(row_indices) >= total_rows - 1:
            # Insert an empty row at the end of the sheet (valid index range)
            insert_row_request = {
                "insertDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": total_rows - 1,  # Insert at the last valid index
                        "endIndex": total_rows
                    }
                }
            }
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={"requests": [insert_row_request]}).execute()
            logger.info(f"Inserted an empty row at the end of {sheet_name} before deletion.")
        
        # Proceed to delete the specified rows
        requests = [{"deleteDimension": {"range": {
            "sheetId": sheet_id, "dimension": "ROWS", "startIndex": idx, "endIndex": idx + 1}}} for idx in row_indices]
        
        if requests:
            batch_update_request = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=batch_update_request).execute()
            logger.info(f"Deleted {len(row_indices)} rows from {sheet_name}.")
        else:
            logger.info(f"No rows to delete in {sheet_name}.")
            
    except Exception as e:
        logger.error(f"Error deleting rows from sheet {sheet_name}: {str(e)}")

# def get_email_domain(email):
#     """Extracts the domain from an email address."""
#     return email.split('@')[-1].lower()

# def get_mx_record(domain):
#     """Fetches the MX record for a given domain."""
#     try:
#         answers = dns.resolver.resolve(domain, 'MX')
#         mx_records = [r.exchange.to_text() for r in answers]
#         logger.debug(f"MX records for domain {domain}: {mx_records}")
#         return mx_records
#     except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout) as e:
#         logger.warning(f"Could not fetch MX records for domain {domain}: {str(e)}")
#         return []

# def get_destination_sheet_name(domain):
#     """Maps an email domain to the corresponding sheet name or performs an MX lookup."""
#     domain_to_sheet = {
#         "gmail.com": "GMAIL",
#         "aol.com": "AOL",
#         "outlook.com": "OUTLOOK",
#         "hotmail.com": "HOTMAIL",
#         "earthlink.net": "EARTHLINK",
#         "mail.com": "MAIL",
#         "cox.net": "COX",
#         "yahoo.com": "YAHOO",
#     }
    
#     # Check if domain matches any predefined sheets
#     if domain in domain_to_sheet:
#         logger.debug(f"Domain {domain} mapped directly to sheet {domain_to_sheet[domain]}")
#         return domain_to_sheet[domain]
    
#     # If no match, check the MX record for the domain
#     mx_records = get_mx_record(domain)
#     for mx in mx_records:
#         if "google" in mx or "gmail" in mx:
#             logger.debug(f"Domain {domain} has MX record {mx}, sending to GSUITE")
#             return "GSUITE"
#         elif "outlook" in mx:
#             logger.debug(f"Domain {domain} has MX record {mx}, sending to OFFICE")
#             return "OFFICE"
    
#     # Default to PREMIUM if no specific sheet or MX record match
#     logger.debug(f"Domain {domain} does not match any predefined sheets or MX records, sending to PREMIUM")
#     return "PREMIUM"

# def append_row_to_sheet(sheet_name, row_data):
#     """Appends a row to a specific sheet."""
#     update_sheet_data(sheet_name, [row_data])

# def delete_sheet_row(sheet_name, row_index):
#     """Deletes a specific row from a sheet."""
#     delete_sheet_rows(sheet_name, [row_index])

# def move_rows_based_on_email():
#     """Moves rows from the PROCESSOR sheet to the appropriate sheet based on email domain and MX records."""
#     data = get_sheet_data("PROCESSOR")
#     if len(data) < 2:
#         logger.info("No data to process or only header found in PROCESSOR sheet.")
#         return
    
#     header = data[0]
#     rows_to_delete = []
    
#     for i, row in enumerate(data[1:], start=1):  # Start from the second row (index 1)
#         if len(row) > EMAIL_COLUMN_INDEX:
#             email = row[EMAIL_COLUMN_INDEX].strip()
#             domain = get_email_domain(email)
#             destination_sheet = get_destination_sheet_name(domain)
            
#             if destination_sheet:
#                 logger.info(f"Moving email {email} to sheet {destination_sheet}")
#                 append_row_to_sheet(destination_sheet, row)
#                 rows_to_delete.append(i)
    
#     if rows_to_delete:
#         delete_sheet_rows("PROCESSOR", sorted(rows_to_delete, reverse=True))

# def is_valid_email(email):
#     """Validates an email address using a regex."""
#     email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
#     return re.match(email_regex, email) is not None

# def remove_duplicate_rows():
#     """Removes duplicate or invalid email rows from specified sheets in a single batch request."""
#     service = get_sheets_service()
    
#     for sheet_name in MOVE_AND_REMOVE_SHEETS_TO_CHECK:
#         sheet_data = get_sheet_data(sheet_name)
#         if len(sheet_data) <= 1:
#             # Either no data or only header row, no duplicates to remove
#             logger.info(f"No data or only header row in sheet: {sheet_name}. Skipping deletion.")
#             continue

#         seen = set()
#         rows_to_delete = []

#         for i, row in enumerate(sheet_data[1:], start=1):  # Adjust index to account for zero-based indexing
#             if len(row) > EMAIL_COLUMN_INDEX:
#                 email = row[EMAIL_COLUMN_INDEX].strip().lower()

#                 if not is_valid_email(email) or email in seen:
#                     rows_to_delete.append(i)
#                 else:
#                     seen.add(email)
        
#         if len(sheet_data) - len(rows_to_delete) == 1:
#             logger.info(f"Only the header row would remain in sheet: {sheet_name}. Proceeding with deletion of all data rows.")
#         elif len(rows_to_delete) == 0:
#             logger.info(f"No duplicates found in sheet: {sheet_name}. Skipping deletion.")
#             continue

#         # Construct a single batch request to delete all identified rows
#         requests = [{
#             'deleteDimension': {
#                 'range': {
#                     'sheetId': get_sheet_id(sheet_name),
#                     'dimension': 'ROWS',
#                     'startIndex': row_index,
#                     'endIndex': row_index + 1
#                 }
#             }
#         } for row_index in sorted(rows_to_delete, reverse=True)]

#         if requests:
#             try:
#                 service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={'requests': requests}).execute()
#                 logger.info(f"Deleted {len(rows_to_delete)} duplicate rows from {sheet_name} in a single batch request.")
#             except Exception as e:
#                 logger.error(f"Error deleting rows in batch from sheet {sheet_name}: {str(e)}")
#         else:
#             logger.info(f"No rows to delete in {sheet_name}.")
