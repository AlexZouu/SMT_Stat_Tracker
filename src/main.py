import os
from dotenv import load_dotenv

load_dotenv()

from backup import backup
from cache import cache
from google.oauth2.service_account import Credentials
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import json
from pathlib import Path
import random
from stats import stats
import tkinter as tk
from tkinter import messagebox


def enable_save_button(save_button):
  save_button['state'] = tk.NORMAL


def update_url(save_button, new_url):
  save_button['state'] = tk.DISABLED
  cache.cache_url(new_url)


def get_worksheet(config, gc, url):
  sheet = gc.open_by_url(url) 
  return sheet.worksheet(config['targetStats']['sheetName'])


def get_success_title(config, unkownsExist=False):
  success_titles = config['successPopupTitles']
  if unkownsExist: success_titles += config['successPopupTitlesWithUnknowns']
  return random.choice(success_titles)


def get_error_title(config):
  error_titles = config['errorPopupTitles']
  return random.choice(error_titles)


def write_stats(worksheet, stats):
  # Write a dataframe of the entire player stat sheet
  # The reason we do that instead of targeting specific rows and columns is to save on API calls
  # This application uses gspread-dataframes, which can only read and write the entire sheet or blocks of the sheet
  # There is a batch_update function in base gspread which can write specific rows and columns in one API call, but it can't take dataframes
  # Also, the sheet we're working with is relatively small, so there's not a big issue with writing the entire thing. 
  set_with_dataframe(worksheet, stats, row=1, col=1)


def update_stats(config, src_dir, gc, root, url):
  try:
    worksheet = get_worksheet(config, gc, url)
    actual_stats = get_as_dataframe(worksheet)
    backup.create_backup(config, src_dir, actual_stats)
    new_stats, unknown_players = stats.get_stats_to_write(config, actual_stats)
    write_stats(worksheet, new_stats)
    unknown_player_string = unknown_players['Player-position'].str.cat(sep='\n')
    if len(unknown_players) != 0:
      title = get_success_title(config, True)
      messagebox.showinfo(title, f'Most of the stats have been written!\n\nHowever, a few players listed below could could not be found in the season stat sheet, please update their stats manually:\n\n{unknown_player_string}', parent=root)
    else:
      title = get_success_title(config)
      messagebox.showinfo('Success!', 'The stats have been written!', parent=root)
  except Exception as e:
    title = get_error_title(config)
    messagebox.showerror(title, f'An error has occured while updating the stats, and as such no changes have been made. Please try again, or contact Sluggers Stat Tracker tech support for help\n\nError: {e}', parent=root)


def restore_backup(config, gc, root, url):
  try:
    worksheet = get_worksheet(config, gc, url)
    backup_stats = backup.get_backup()
    write_stats(worksheet, backup_stats)
    title = get_success_title(config)
    messagebox.showinfo(title, 'The backup has been restored!', parent=root)
  except Exception as e:
    title = get_error_title(config)
    messagebox.showerror(title, f'An error has occured while restoring the backup, and as such no changes have been made. Please try again, or contact Sluggers Stat Tracker tech support for help\n\nError: {e}', parent=root)


def main():
  root = tk.Tk()

  credentials_env = os.getenv('GSPREAD_CREDENTIALS')
  credentials_json = json.loads(credentials_env)

  scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
  ]

  try:
    credentials = Credentials.from_service_account_info(credentials_json, scopes=scopes)
    gc = gspread.authorize(credentials)

    src_dir = Path(__file__).resolve().parent

    with open(f'{src_dir}/config.json', 'r') as config_file:    # Open the file
      config = json.load(config_file)    # Get the config

    url_str = cache.retrieve_url(src_dir)
    if not url_str: url_str = ''

    root.bind_all('<Button-1>', lambda event: event.widget.focus_set())
    root.resizable(False, False)
    root.title('Stat Tracker')
    root.geometry('500x365')
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=0)
    root.columnconfigure(2, weight=0)
    root.columnconfigure(3, weight=0)
    root.columnconfigure(4, weight=1)

    url = tk.StringVar(value=url_str)

    title_label = tk.Label(root, text=config['appTitle'], font=('Segoe UI', 16), justify='left')
    explanatory_text_label = tk.Label(root, text=config['explanatoryText'], wraplength=425, font=('Segoe UI', 12), justify='left')
    title_label.grid(row=0, column=1, columnspan=3, pady=(20, 10), sticky='w')
    explanatory_text_label.grid(row=1, column=1, columnspan=3, pady=(0, 10), sticky='w')

    stat_button = tk.Button(
        root, 
        text='Record game stats', 
        command=lambda: update_stats(config, src_dir, gc, root, url.get()), 
        font=('Segoe UI', 8)
    )

    backup_button = tk.Button(
        root, 
        text='Restore backup', 
        command=lambda: restore_backup(config, gc, root, url.get()), 
        font=('Segoe UI', 8)
    )

    quit_button = tk.Button(
        root, 
        text='Close application', 
        command=root.destroy, 
        font=('Segoe UI', 8)
    )

    stat_button.grid(row=2, column=1, padx=10, pady=10, sticky='s')
    backup_button.grid(row=2, column=2, padx=10, pady=10, sticky='s')
    quit_button.grid(row=2, column=3, padx=10, pady=10, sticky='s')

    url_entry_label = tk.Label(root, text=config['urlEntryLabel'], font=('Segoe UI', 8), padx=5)
    url_entry_label.grid(row=3, column=1, columnspan=1, sticky='e')

    url.trace_add('write', lambda *args: enable_save_button(save_button))
    sheet_url_entry = tk.Entry(root, textvariable=url, font=('Segoe UI', 8), width=40)
    sheet_url_entry.grid(row=3, column=2, columnspan=2, pady=10, ipadx=2, ipady=2, sticky='w')

    save_button = tk.Button(
        root, 
        text='Save URL', 
        command=lambda: update_url(save_button, url.get()), 
        font=('Segoe UI', 8),
        state=tk.DISABLED
    )
    save_button.grid(row=4, column=2)

    root.mainloop()
  except Exception as e:
    messagebox.showerror('Something really went wrong', f'You shouldn\'t see this error too much. Maybe the API key expired? Or maybe the Google Drive or Google Sheets API\'s are down. Or possibly there\'s an edge case I missed! Either way, good luck!\n\nError: {e}', parent=root)


if __name__ == '__main__': 
  main()