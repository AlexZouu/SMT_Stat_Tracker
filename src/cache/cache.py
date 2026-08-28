import json
from pathlib import Path


def cache_parameter(src_dir, key, value):
  try:
    with open('cache/cache.json', 'r') as cache_file:
      cache = json.load(cache_file)

    cache[key] = value

    with open(f'{src_dir}cache/cache.json', 'w') as cache_file:
      json.dump(cache, cache_file)
  except (FileNotFoundError, json.JSONDecodeError):   # If the file doesn't exist or is empty, write the value
    with open('cache/cache.json', 'w') as cache_file:
      json.dump({key: value}, cache_file)


def retrieve_parameter(src_dir, key):
  try:
    with open(f'{src_dir}/cache/cache.json', 'r') as cache_file:
      cache = json.load(cache_file)

    return cache.get(key)
  except (FileNotFoundError, json.JSONDecodeError):   # If the file doesn't exist or is empty, write the value
    with open('cache/cache.json', 'w') as cache_file:
      json.dump({}, cache_file)
      return None


def cache_url(src_dir, url):
  cache_parameter('statSheetURL', url)


def cache_default_stat_sheet_path(path):
  cache_parameter('defaultStatSheetPath', path)


def cache_default_backup_path(path):
  cache_parameter('defaultBackupPath', path)


def retrieve_url(src_dir):
  return retrieve_parameter(src_dir, 'statSheetURL')


def retrieve_default_stat_sheet_path():
  return retrieve_parameter('defaultStatSheetPath')


def retrieve_default_backup_path():
  return retrieve_parameter('defaultBackupPath')