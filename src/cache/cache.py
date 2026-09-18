import json
import os
from pathlib import Path


def cache_parameter(key, value):
  src_dir = os.getenv('SRC_DIR')
  try:
    with open(f'{src_dir}/cache/cache.json', 'r') as cache_file:
      cache = json.load(cache_file)

    cache[key] = value

    with open(f'{src_dir}/cache/cache.json', 'w') as cache_file:
      json.dump(cache, cache_file)
  except (FileNotFoundError, json.JSONDecodeError):   # If the file doesn't exist or is empty, write the value
    with open(f'{src_dir}/cache/cache.json', 'w') as cache_file:
      json.dump({key: value}, cache_file)


def retrieve_parameter(key):
  src_dir = os.getenv('SRC_DIR')
  try:
    with open(f'{src_dir}/cache/cache.json', 'r') as cache_file:
      cache = json.load(cache_file)
    return cache.get(key)
  except (FileNotFoundError, json.JSONDecodeError):   # If the file doesn't exist or is empty, write the value
    with open('cache/cache.json', 'w') as cache_file:
      json.dump({}, cache_file)
      return None


def cache_url(url):
  cache_parameter('statSheetURL', url)


def cache_default_source_sheet_path(path):
  cache_parameter('defaultSourceSheetPath', path)


def cache_default_backup_path(path):
  cache_parameter('defaultBackupPath', path)


def retrieve_url():
  return retrieve_parameter('statSheetURL')


def retrieve_default_source_sheet_path():
  return retrieve_parameter('defaultSourceSheetPath')


def retrieve_default_backup_path():
  return retrieve_parameter('defaultBackupPath')