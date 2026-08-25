from datetime import datetime
from pathlib import Path


def createBackup(config, actualStats):
  backupDir = Path(config['backupLocation'])
  backupName = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

  backupDir.mkdir(parents=True, exist_ok=True)
  actualStats.to_csv(backupDir / backupName, index=False)

  pruneBackups(config, backupDir)


def pruneBackups(config, backupDir):
  backups = [f for f in backupDir.iterdir() if f.is_file()]

  while len(backups) > config['numBackupsKept']:
    oldestBackup = min(backups, key=lambda f: f.stat().st_mtime)
    oldestBackup.unlink()
    backups.remove(oldestBackup)