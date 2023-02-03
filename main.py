from model import engine
import pandas as pd
from google_workers import GoogleSheetWorker
from config import *

if __name__ == '__main__':
    df = pd.read_sql(f'SELECT * FROM {DB_SCHEMA}.{EVENT_TABLE_NAME} '
                     f'ORDER BY event_date ASC, event_time ASC, site_link ASC, inner_id ASC', engine)

    gsw = GoogleSheetWorker(spread_id=SPREADSHEET_ID)
    gsw.clear_worksheet()
    gsw.set_headers(list(df.columns))
    gsw.upload_dataframe(df)
    gsw.format_table()