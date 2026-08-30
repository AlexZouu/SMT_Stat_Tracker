import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


def get_source_sheet():
  source_sheet = filedialog.askopenfilename(title="Select a File")   # Prompt the user to select the sheet with the stats

  if not source_sheet: raise Exception('No file selected.')
  if not source_sheet.endswith('.xlsx'): raise Exception('You must select a valid xlsx file.')

  return source_sheet


def get_general_stats(general_config, source_sheet):
  general_stats = pd.read_excel(source_sheet, sheet_name=general_config['sheet'])    # Get the second sheet with the general player stats
  general_stats = general_stats.drop(general_config['rowsToDrop'])   # Drop the rows with the team summary
  general_stats = general_stats.drop(columns=general_config['statsToDrop'])    # Drop any stats we don't want
  general_stats = general_stats.rename(columns=general_config['statMapping'])    # Rename the stats so they match the actual stat sheet
  # This next statement gets rid of any positions that aren't the player's starting position
  # For example if Luigi started as pitcher and swapped to catcher, his position would be tracked as P, C
  # This gets rid of everything other than the P
  general_stats['position'] = general_stats['position'].apply(lambda x: x if x.find(',') == -1 else x[0:x.find(',')])

  return general_stats


def get_pitching_stats(pitching_config, source_sheet):
  pitching_stats = pd.read_excel(source_sheet, sheet_name=pitching_config['sheet'])    # Get the third sheet with the pitching stats
  pitching_stats = pitching_stats.drop(columns=pitching_config['statsToDrop']).iloc[:len(pitching_stats) - 2]    # Drop stats we don't want and team summary (last two rows)
  pitching_stats = pitching_stats.rename(columns=pitching_config['statMapping'])   # Rename the stats so they match the actual stat sheet

  return pitching_stats


def combine_stats(config, target_stats, general_stats, pitching_stats):
  target_stats_config = config['targetStats']

  player_name_map = target_stats_config['playerNameMap']    # Mapping of player names 
  stats_not_of_int_type = target_stats_config['statsNotOfIntType']

  general_stats['Player'] = general_stats['Player'].replace(player_name_map)    # Replace the names of everyone in the source sheet with the corresponding name in the target sheet
  pitching_stats['Player'] = pitching_stats['Player'].replace(player_name_map)    # Replace the names of everyone in the source sheet with the corresponding name in the target sheet

  unknown_general_stats = general_stats[~general_stats['Player'].isin(target_stats['Player'])]    # General stats of players who aren't in the target sheet
  # Add a column for 'player - position'
  unknown_general_stats['Player-position'] = unknown_general_stats['Player'].astype(str) + ' - ' + unknown_general_stats['position'].astype(str)
  unknown_pitching_stats = pitching_stats[~pitching_stats['Player'].isin(target_stats['Player'])]    # Pitching stats of players who aren't in the target sheet
  
  general_stats = general_stats[general_stats['Player'].isin(target_stats['Player'])]    # General stats of players who aren't in the target sheet
  pitching_stats = pitching_stats[pitching_stats['Player'].isin(target_stats['Player'])]    # Pitching stats of players who aren't in the target sheet

  combined_stats = pd.merge(general_stats, pitching_stats, on='Player', how='left')    # Merge the pitching stats into the general stats based on the player
  combined_stats = combined_stats.fillna(0)   # Fill the pitching stats that are NaN with 0
  type_mapping = {stat: int for stat in combined_stats.columns if stat not in stats_not_of_int_type}
  combined_stats = combined_stats.astype(type_mapping)
  combined_stats['gp'] = 1

  # TODO: 
  # If there ARE NOT duplicate names in general:
    # If player is just in general:
      # Ask who it is, update general
    # If player is in both general and pitching:
      # Ask who it is, update general and pitching
  # If there ARE duplicate names in general:
    # If neither are in pitching:
      # Ask who they are, update general
    # If one of them is in pitching and one of them is position of pitcher
      # Ask who they are, update general
    # If both of them are in pitching and one of them is position of pitcher
      # Ask who they are, update general
    # If one of them is in pitching and neither of them is position of pitcher
      # BAD - Must update manually
    # If both of them are in pitching and neither of them is position of pitcher
      # BAD - Must update manually

  return combined_stats, unknown_general_stats, unknown_pitching_stats


def update_target_stats(config, target_stats, source_stats):
  target_stats = target_stats.set_index('Player', drop=False)
  source_stats = source_stats.set_index('Player')

  target_stats.update(source_stats['position'])
  source_stats = source_stats.drop(columns=['position'])

  stats_of_string_type = config['targetStats']['statsOfStringType']

  target_stats = pd.concat([target_stats, source_stats])
  target_stats = target_stats.fillna({stat: 0 for stat in target_stats.columns if stat not in stats_of_string_type})
  target_stats = target_stats.groupby(level=0, sort=False).sum()

  return target_stats


def get_stats_to_write(config, target_stats):
  source_sheet = get_source_sheet()
  general_stats = get_general_stats(config['generalStats'], source_sheet)
  pitching_stats = get_pitching_stats(config['pitchingStats'], source_sheet)
  source_stats, unknown_general_stats, unknown_pitching_stats = combine_stats(config, target_stats, general_stats, pitching_stats)
  new_target_stats = update_target_stats(config, target_stats, source_stats)

  return new_target_stats, unknown_general_stats
