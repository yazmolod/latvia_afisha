from pathlib import Path
Path('output').mkdir(exist_ok=True)

DB_URI = 'sqlite:///output/db.sqlite3'
EVENT_TABLE_NAME = 'event'
SPREADSHEET_ID = '14CZDfVHinBGG7s47Y5VmUo0kjP1vuiOTadX-JOzHDVc'