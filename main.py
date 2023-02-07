from model import engine
import pandas as pd
from config import *
from parsers import parsers
import logging
from pathlib import Path
from google.oauth2.service_account import Credentials
import gspread
import gspread_dataframe


def auth():
    service_keys = Path(__file__).parent.resolve() / 'google_keys.json'
    scopes = [
    'https://www.googleapis.com/auth/drive',
    ]
    return Credentials.from_service_account_file(str(service_keys), scopes=scopes)


def enable_logger(name):
    FORMATTER = logging.Formatter("[%(asctime)s][%(name)s] %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(FORMATTER)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(f'debug.log', 'a+', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
    return logger


def parse():
    for parser_class in parsers:
        try:
            parser = parser_class()
            logger = enable_logger(parser_class.__name__)
            parser.main()
        except Exception:
            logger.exception('CRITICAL')


def export():
    df = pd.read_sql(f'SELECT * FROM {EVENT_TABLE_NAME} '
                     f'ORDER BY event_date ASC, event_time ASC, site_link ASC, inner_id ASC', engine)
    credentials = auth()
    spread = gspread.authorize(credentials).open_by_key(SPREADSHEET_ID)
    sheet = spread.sheet1
    sheet.delete_rows(2, sheet.row_count)
    gspread_dataframe.set_with_dataframe(sheet, df, include_column_header=True, include_index=False)


if __name__ == '__main__':
    parse()
    export()
