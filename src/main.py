import os
from dotenv import load_dotenv

load_dotenv()

from google.oauth2.service_account import Credentials
import gspread
from gspread_dataframe import get_as_dataframe
import json


def main():
  credentials_env = os.getenv("GSPREAD_CREDENTIALS")
  stat_sheet_url = os.getenv("STAT_SHEET_URL")

  credentials_json = json.loads(credentials_env)
  scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
  ]

  credentials = Credentials.from_service_account_info(credentials_json, scopes=scopes)
  gc = gspread.authorize(credentials)

  with open('config.json', 'r') as config_file:    # Open the file
    config = json.load(config_file)    # Get the config

  actual_stats_config = config["actualStats"]
  
  sheet = gc.open_by_url(stat_sheet_url) 
  worksheet = sheet.worksheet(actual_stats_config['sheetName'])
  actual_stats = get_as_dataframe(worksheet)

  print(actual_stats)


if __name__ == '__main__': 
  main()