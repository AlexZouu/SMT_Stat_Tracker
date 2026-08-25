import gspread
from gspread_dataframe import get_as_dataframe
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

from src.backup.backups import create_backup, restore_backup


def read_new_stats(general_config, pitching_config): 
  stat_sheet = filedialog.askopenfilename(title="Select a File")   # Prompt the user to select the sheet with the stats

  if not stat_sheet: raise Exception('No file selected.')
  if not stat_sheet.endswith('.xlsx'): raise Exception('You must select a valid xlsx file.')

  general_stats = pd.read_excel(stat_sheet, sheet_name=general_config['sheet'])    # Get the second sheet with the general player stats
  general_stats = general_stats.drop(general_config['rowsToDrop'])   # Drop the rows with the team summary
  general_stats = general_stats.drop(columns=general_config['statsToDrop'])    # Drop any stats we don't want
  general_stats = general_stats.rename(columns=general_config['statMapping'])    # Rename the stats so they match the actual stat sheet
  # This next statement gets rid of any positions that aren't the player's starting position
  # For example if Luigi started as pitcher and swapped to catcher, his position would be P, C
  # The statement could get rid of everything other than the P
  general_stats['position'] = general_stats['position'].apply(lambda x: x if x.find(',') == -1 else x[0:x.find(',')])

  pitching_stats = pd.read_excel(stat_sheet, sheet_name=pitching_config['sheet'])    # Get the third sheet with the pitching stats
  pitching_stats = pitching_stats.drop(columns=pitching_config['statsToDrop']).iloc[:len(pitching_stats) - 2]    # Drop stats we don't want and team summary (last two rows)
  pitching_stats = pitching_stats.rename(columns=pitching_config['statMapping'])   # Rename the stats so they match the actual stat sheet

  # Note: We have the rename the stats before combining the general and pitching stats as there are duplicate stat names

  combined_stats = pd.merge(general_stats, pitching_stats, on='Player', how='left')    # Merge the pitching stats into the general stats based on the player
  combined_stats = combined_stats.fillna(0)   # Fill the pitching stats that are NaN with 0

  return combined_stats


def read_actual_stats(actual_stats_config):    # TODO: Maybe don't prune so we can use set_with_dataframe
  gc = gspread.service_account(filename='credentials.json')
  sheet = gc.open_by_url(actual_stats_config['stat_sheetURL']) 
  worksheet = sheet.worksheet(actual_stats_config['sheetName'])
  actual_stats = get_as_dataframe(worksheet)
  actual_stats = actual_stats.drop(columns=actual_stats_config['statsToDrop'])

  return actual_stats


def update_actual_stats(new_stats, actual_stats):
  actual_stats = actual_stats[actual_stats['Player'].isin(new_stats['Player'])]

  print(new_stats[~new_stats['Player'].isin(actual_stats['Player'])])

  # TODO: Update games played manually


def main():
  with open('config.json', 'r') as config_file:    # Open the file
    config = json.load(config_file)    # Get the config

  restore_backup(config["actual_stats"])

  # new_stats = None

  # while 1:
  #   try:
  #     new_stats = read_new_stats(config["general_stats"], config["pitching_stats"])    # Get the stats 
  #     actual_stats = read_actual_stats(config["actual_stats"])
  #     create_backup(config, actual_stats)
  #     update_actual_stats(new_stats, actual_stats)
  #     break
  #   except Exception as e:
  #     raise e   # TODO: Remove this once done
  #     choice = messagebox.askyesno(
  #       title="ERROR", 
  #       message=f'{e}\n\nWould you like to try again?',
  #       icon='error'
  #     )
  #     if not choice: return


if __name__ == '__main__':
  main()