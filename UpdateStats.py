from datetime import datetime
import gspread
from gspread_dataframe import get_as_dataframe
import json
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


def readNewStats(generalConfig, pitchingConfig): 
  statSheet = filedialog.askopenfilename(title="Select a File")   # Prompt the user to select the sheet with the stats

  if not statSheet: raise Exception('No file selected.')
  if not statSheet.endswith('.xlsx'): raise Exception('You must select a valid xlsx file.')

  generalStats = pd.read_excel(statSheet, sheet_name=generalConfig['sheet'])    # Get the second sheet with the general player stats
  generalStats = generalStats.drop(generalConfig['rowsToDrop'])   # Drop the rows with the team summary
  generalStats = generalStats.drop(columns=generalConfig['statsToDrop'])    # Drop any stats we don't want
  generalStats = generalStats.rename(columns=generalConfig['statMapping'])    # Rename the stats so they match the actual stat sheet
  # This next statement gets rid of any positions that aren't the player's starting position
  # For example if Luigi started as pitcher and swapped to catcher, his position would be P, C
  # The statement could get rid of everything other than the P
  generalStats['position'] = generalStats['position'].apply(lambda x: x if x.find(',') == -1 else x[0:x.find(',')])

  pitchingStats = pd.read_excel(statSheet, sheet_name=pitchingConfig['sheet'])    # Get the third sheet with the pitching stats
  pitchingStats = pitchingStats.drop(columns=pitchingConfig['statsToDrop']).iloc[:len(pitchingStats) - 2]    # Drop stats we don't want and team summary (last two rows)
  pitchingStats = pitchingStats.rename(columns=pitchingConfig['statMapping'])   # Rename the stats so they match the actual stat sheet

  # Note: We have the rename the stats before combining the general and pitching stats as there are duplicate stat names

  combinedStats = pd.merge(generalStats, pitchingStats, on='Player', how='left')    # Merge the pitching stats into the general stats based on the player
  combinedStats = combinedStats.fillna(0)   # Fill the pitching stats that are NaN with 0

  # split = len(combinedStats) // 2   # Split it in half for team 1 and team 2

  # team1 = combinedStats.iloc[:split]
  # team2 = combinedStats.iloc[split:len(combinedStats)]

  # team1['Team'] = team1.iat[0, 0]   # Set the team for each player to the correct team
  # team2['Team'] = team2.iat[0, 0]

  return combinedStats


def readActualStats(config):    # TODO: Maybe don't prune so we can use set_with_dataframe
  gc = gspread.service_account(filename='credentials.json')
  sheet = gc.open_by_url(config['statSheetURL']) 
  worksheet = sheet.worksheet(config['sheetName'])
  actualStats = get_as_dataframe(worksheet)
  actualStats = actualStats.drop(columns=config['statsToDrop'])

  return actualStats


def createBackup(config, actualStats):
  backupDir = Path(config['backupLocation'])
  backupName = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

  backupDir.mkdir(parents=True, exist_ok=True)
  actualStats.to_csv(backupDir / backupName, index=False)


def updateActualStats(newStats, actualStats):
  actualStats = actualStats[actualStats['Player'].isin(newStats['Player'])]

  print(newStats[~newStats['Player'].isin(actualStats['Player'])])

  # TODO: Update games played manually


def main():
  with open('config.json', 'r') as configFile:    # Open the file
    config = json.load(configFile)    # Get the config

  newStats = None

  while 1:
    try:
      newStats = readNewStats(config["generalStats"], config["pitchingStats"])    # Get the stats 
      actualStats = readActualStats(config["actualStats"])
      createBackup(config, actualStats)
      updateActualStats(newStats, actualStats)
      break
    except Exception as e:
      raise e   # TODO: Remove this once done
      choice = messagebox.askyesno(
        title="ERROR", 
        message=f'{e}\n\nWould you like to try again?',
        icon='error'
      )
      if not choice: return


if __name__ == '__main__':
  main()