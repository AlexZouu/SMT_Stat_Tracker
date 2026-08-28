import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


def read_new_stats(config): 
  stat_sheet = filedialog.askopenfilename(title="Select a File")   # Prompt the user to select the sheet with the stats

  if not stat_sheet: raise Exception('No file selected.')
  if not stat_sheet.endswith('.xlsx'): raise Exception('You must select a valid xlsx file.')

  general_config = config['generalStats']
  pitching_config = config['pitchingStats']
  actual_stats_config = config['targetStats']

  general_stats = pd.read_excel(stat_sheet, sheet_name=general_config['sheet'])    # Get the second sheet with the general player stats
  general_stats = general_stats.drop(general_config['rowsToDrop'])   # Drop the rows with the team summary
  general_stats = general_stats.drop(columns=general_config['statsToDrop'])    # Drop any stats we don't want
  general_stats = general_stats.rename(columns=general_config['statMapping'])    # Rename the stats so they match the actual stat sheet
  # This next statement gets rid of any positions that aren't the player's starting position
  # For example if Luigi started as pitcher and swapped to catcher, his position would be P, C
  # This gets rid of everything other than the P
  general_stats['position'] = general_stats['position'].apply(lambda x: x if x.find(',') == -1 else x[0:x.find(',')])

  pitching_stats = pd.read_excel(stat_sheet, sheet_name=pitching_config['sheet'])    # Get the third sheet with the pitching stats
  pitching_stats = pitching_stats.drop(columns=pitching_config['statsToDrop']).iloc[:len(pitching_stats) - 2]    # Drop stats we don't want and team summary (last two rows)
  pitching_stats = pitching_stats.rename(columns=pitching_config['statMapping'])   # Rename the stats so they match the actual stat sheet

  # Note: We have the rename the stats before combining the general and pitching stats as there are duplicate stat names

  player_name_map = actual_stats_config['playerNameMap']
  stats_not_of_int_type = actual_stats_config['statsNotOfIntType']

  combined_stats = pd.merge(general_stats, pitching_stats, on='Player', how='left')    # Merge the pitching stats into the general stats based on the player
  combined_stats['Player'] = combined_stats['Player'].replace(player_name_map)
  combined_stats = combined_stats.fillna(0)   # Fill the pitching stats that are NaN with 0
  type_mapping = {stat: int for stat in combined_stats.columns if stat not in stats_not_of_int_type}
  combined_stats = combined_stats.astype(type_mapping)
  combined_stats['gp'] = 1

  return combined_stats
  

def update_actual_stats(config, new_stats, actual_stats):
  base_stats = actual_stats[actual_stats['Player'].isin(new_stats['Player'])]
  players_not_updated = new_stats[~new_stats['Player'].isin(base_stats['Player'])]['Player']
  stats_to_add = new_stats[new_stats['Player'].isin(base_stats['Player'])]

  base_stats['position'] = base_stats['Player'].map(stats_to_add.set_index('Player')['position'])
  stats_to_add = stats_to_add.drop(columns=['position'])

  base_stats = base_stats.set_index('Player', drop=False)
  stats_to_add = stats_to_add.set_index('Player')

  stats_of_string_type = config['targetStats']['statsOfStringType']

  combined_stats = pd.concat([base_stats, stats_to_add])
  combined_stats = combined_stats.fillna({stat: 0 for stat in combined_stats.columns if stat not in stats_of_string_type})
  combined_stats = combined_stats.groupby(level=0).sum()

  actual_stats = actual_stats.fillna({stat: 0 for stat in actual_stats.columns if stat not in stats_of_string_type})

  actual_stats = actual_stats.set_index('Player', drop=False)
  actual_stats.update(combined_stats)

  return actual_stats, players_not_updated


# ======================================================================================================================================================


def get_source_sheet():
  source_sheet = filedialog.askopenfilename(title="Select a File")   # Prompt the user to select the sheet with the stats

  if not source_sheet: raise Exception('No file selected.')
  if not source_sheet.endswith('.xlsx'): raise Exception('You must select a valid xlsx file.')

  return source_sheet


def get_general_stats(config, source_sheet, target_stats):
  general_config = config['generalStats']
  target_stats_config = config['targetStats']
  general_stats = pd.read_excel(source_sheet, sheet_name=general_config['sheet'])    # Get the second sheet with the general player stats
  general_stats = general_stats.drop(general_config['rowsToDrop'])   # Drop the rows with the team summary
  general_stats = general_stats.drop(columns=general_config['statsToDrop'])    # Drop any stats we don't want
  general_stats = general_stats.rename(columns=general_config['statMapping'])    # Rename the stats so they match the actual stat sheet
  # This next statement gets rid of any positions that aren't the player's starting position
  # For example if Luigi started as pitcher and swapped to catcher, his position would be P, C
  # This gets rid of everything other than the P
  general_stats['position'] = general_stats['position'].apply(lambda x: x if x.find(',') == -1 else x[0:x.find(',')])

  player_name_map = target_stats_config['playerNameMap']
  general_stats['Player'] = general_stats['Player'].replace(player_name_map)

  players_not_in_target_stats = general_stats[~general_stats['Player'].isin(target_stats['Player'])]
  players_not_in_target_stats['Player'] = players_not_in_target_stats['Player'].astype(str) + '_' + players_not_in_target_stats['position'].astype(str)

  print(players_not_in_target_stats)

  return general_stats


def get_pitching_stats(pitching_config, source_sheet):
  pitching_stats = pd.read_excel(source_sheet, sheet_name=pitching_config['sheet'])    # Get the third sheet with the pitching stats
  pitching_stats = pitching_stats.drop(columns=pitching_config['statsToDrop']).iloc[:len(pitching_stats) - 2]    # Drop stats we don't want and team summary (last two rows)
  pitching_stats = pitching_stats.rename(columns=pitching_config['statMapping'])   # Rename the stats so they match the actual stat sheet

  return pitching_stats


def combine_stats(config, general_stats, pitching_stats):
  pass


def update_target_stats(config, target_stats, source_stats):
  pass


def get_stats_to_write(config, target_stats):
  # new_stats = read_new_stats(config)    # Get the stats 
  # stats_to_write = update_actual_stats(config, new_stats, target_stats)

  # ===========================================================================

  source_sheet = get_source_sheet()
  general_stats = get_general_stats(config, source_sheet, target_stats)
  pitching_stats = get_pitching_stats(config, source_sheet)
  source_stats = combine_stats(general_stats, pitching_stats)
  new_target_stats = update_target_stats(target_stats, source_stats)

  # return stats_to_write, players_not_updated
    # except Exception as e:
    #   raise e   # TODO: Remove this once done
    #   choice = messagebox.askyesno(
    #     title="ERROR", 
    #     message=f'{e}\n\nWould you like to try again?',
    #     icon='error'
    #   )
    #   if not choice: return