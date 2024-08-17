from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Google Sheets and API configuration
SPREADSHEET_ID = '1y7_yT1OEdkTEeEEk_JCLbAEtPAVH9RKTXiQclkE6ugU'
SERVICE_ACCOUNT_FILE = 'api/credentials.json'
EMAIL_COLUMN = 'email_addr'
VERIFIED_SHEET_NAME = 'VERIFIED'
SHEETS_TO_CHECK = ["GMAIL", "AOL", "OUTLOOK", "HOTMAIL"]
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
    service = get_sheets_service()
    sheet_id = get_sheet_id(sheet_name)
    if sheet_id is None:
        logger.error(f"Sheet ID not found for sheet: {sheet_name}")
        return

    requests = [{"deleteDimension": {"range": {
        "sheetId": sheet_id, "dimension": "ROWS", "startIndex": idx, "endIndex": idx + 1}}} for idx in row_indices]
    batch_update_request = {"requests": requests}
    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                       body=batch_update_request).execute()
