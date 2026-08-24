import gspread
import json
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def readNewStats(): 
  statSheet = filedialog.askopenfilename(title="Select a File")

  if not statSheet or not statSheet.endswith('.xlsx'): return None, None
  
  generalStats = pd.read_excel(statSheet, sheet_name=1)
  pitchingStats = pd.read_excel(statSheet, sheet_name=2)

  pitchingStats = pitchingStats.drop('Team', axis=1).iloc[:len(pitchingStats) - 2]

  combinedStats = pd.merge(generalStats, pitchingStats, on='Player', how='left')

  combinedStats = combinedStats.set_index('Player')

  split = len(combinedStats) // 2

  team1 = combinedStats.iloc[:split - 1]
  team2 = combinedStats.iloc[split:len(combinedStats) - 1]

  return team1, team2


def main():
  with open('config.json', 'r') as config_file:
    config = json.load(config_file)

  team1, team2 = readNewStats()

  if not team1 or not team2: 
    print('Please select a valid file')
    return

  print(team1)
  print(team2)

  # gc = gspread.service_account(filename='credentials.json')

  # sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1vjeD0yJj0-T-sQ5uCXtmwkisrzmnMArj/edit?gid=1986828901#gid=1986828901') 

  # worksheet = sheet.sheet1

  # all_rows = worksheet.get_all_values()
  # print('All values:', all_rows)


if __name__ == '__main__':
  main()