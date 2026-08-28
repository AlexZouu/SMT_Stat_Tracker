from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
from pathlib import Path
from tkinter import filedialog


def create_backup(config, src_dir, actual_stats):
  backup_dir = Path(f'{src_dir}/backup/backups')
  backup_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

  backup_dir.mkdir(parents=True, exist_ok=True)
  actual_stats.to_csv(backup_dir / backup_name, index=False)

  prune_backups(config, backup_dir)


def prune_backups(config, backup_dir):
  backups = [f for f in backup_dir.iterdir() if f.is_file()]

  while len(backups) > config['numBackupsKept']:
    oldest_backup = min(backups, key=lambda f: f.stat().st_mtime)
    oldest_backup.unlink()
    backups.remove(oldest_backup)


def get_backup():
  backup_csv = filedialog.askopenfilename(title="Select a Backup")   # Prompt the user to select the sheet with the stats

  if not backup_csv: raise Exception('No file selected.')
  if not backup_csv.endswith('.csv'): raise Exception('You must select a valid xlsx file.')

  return pd.read_csv(backup_csv)