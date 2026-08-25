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
  # Write a dataframe of the entire player stat sheet
  # The reason we do that instead of targeting specific rows and columns is to save on API calls
  # This application uses gspread-dataframes, which can only read and write the entire sheet or blocks of the sheet
  # There is a batch_update function in base gspread which can write specific rows and columns in one API call, but it can't take dataframes
  # Also, the sheet we're working with is relatively small, so there's not a big issue with writing the entire thing. 
  set_with_dataframe(worksheet, stats, row=1, col=1)


def update_stats(config, worksheet):
  actual_stats = get_as_dataframe(worksheet)
  backup.create_backup(config, actual_stats)
  new_stats = stats.get_new_stats(config, actual_stats)
  # write_stats(worksheet, new_stats)


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
  root.geometry("500x275")
  root.columnconfigure(0, weight=1)
  root.columnconfigure(1, weight=0)
  root.columnconfigure(2, weight=0)
  root.columnconfigure(3, weight=0)
  root.columnconfigure(4, weight=1)

  title_label = tk.Label(root, text=config['appTitle'], font=("Arial", 14), pady=20, justify='left')
  explanatory_text_label = tk.Label(root, text=config['explanatoryText'], wraplength=300, font=("Arial", 12), pady=10, justify='left')
  title_label.grid(row=0, column=1, columnspan=3, sticky='w')
  explanatory_text_label.grid(row=1, column=1, columnspan=3, sticky='w')

  stat_button = tk.Button(
      root, 
      text="Record game stats", 
      command=lambda: update_stats(config, worksheet), 
      # bg="blue", 
      # fg="white", 
  )

  backup_button = tk.Button(
      root, 
      text="Restore backup", 
      command=lambda: restore_backup(worksheet), 
      # bg="blue", 
      # fg="white", 
  )

  quit_button = tk.Button(
      root, 
      text="Close application", 
      command=root.destroy, 
      # bg="blue", 
      # fg="white", 
  )

  stat_button.grid(row=2, column=1, padx=10, pady=10, sticky="s")
  backup_button.grid(row=2, column=2, padx=10, pady=10, sticky="s")
  quit_button.grid(row=2, column=3, padx=10, pady=10, sticky="s")

  root.mainloop()


if __name__ == '__main__': 
  main()