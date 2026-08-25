import os
from dotenv import load_dotenv

load_dotenv()

from backup import backup
from google.oauth2.service_account import Credentials
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json
from stats import stats
import tkinter as tk


def write_stats(worksheet, stats):
  set_with_dataframe(worksheet, stats, row=1, col=1)


def update_stats(config, worksheet):
  actual_stats = get_as_dataframe(worksheet)
  backup.create_backup(config, actual_stats)


def restore_backup(worksheet):
  backup_stats = backup.get_backup()
  write_stats(worksheet, backup_stats)


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

  root = tk.Tk()
  root.title("Stat Tracker")
  root.geometry("500x150")
  root.columnconfigure(0, weight=1)
  root.columnconfigure(1, weight=1)
  root.columnconfigure(2, weight=1)

  label = tk.Label(root, text="Slugger Stat Tracker", font=("Arial", 14), pady=20)
  label.grid(row=0, column=0, columnspan=3)

  stat_button = tk.Button(
      root, 
      text="Record game stats", 
      command=lambda: update_stats(config, worksheet), 
      bg="blue", 
      fg="white", 
  )

  backup_button = tk.Button(
      root, 
      text="Restore backup", 
      command=lambda: restore_backup(worksheet), 
      bg="blue", 
      fg="white", 
  )

  quit_button = tk.Button(
      root, 
      text="Close application", 
      command=root.destroy, 
      bg="blue", 
      fg="white", 
  )

  stat_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
  backup_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
  quit_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

  root.mainloop()


if __name__ == '__main__': 
  main()