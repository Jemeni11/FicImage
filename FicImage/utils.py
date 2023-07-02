import os
import sys
from typing import Tuple
import json


def config_check(directory_path: str = None) -> Tuple[bool, str]:
	"""
	This function checks if ficimage.json exists in the given directory path
	and returns a tuple containing a boolean and a string (the directory path).
	If no directory path is given, FicImage checks the current directory and
	then the Operating System's home directory.
	:param directory_path: A string or None
	:return: A tuple containing a boolean and a string
	"""
	if directory_path is None:
		current_dir = os.getcwd()
		print(f"[Config File Check]: No directory was passed, checking current directory '{current_dir}'")
		
		file_path = os.path.join(current_dir, "ficimage.json")
		
		if os.path.isfile(file_path):
			print(f"[Config File Check]: ficimage.json found in current directory!")
			return True, current_dir
		
		directory_path = os.path.expanduser("~")
		print(f"[Config File Check]: ficimage.json not found in current directory, checking '{directory_path}'")
	
	file_path = os.path.join(directory_path, "ficimage.json")
	
	is_file = os.path.isfile(file_path)
	print(f"[Config File Check]: "
	      f"{'ficimage.json found!' if is_file else 'ficimage.json not found, using default config settings'}")
	
	return is_file, directory_path


def load_config_json(ficimage_path: str) -> dict:
	"""
	Loads ficimage.json. Calls `sys.exit` if there's a JSONDecodeError.
	:param ficimage_path: The path to ficimage.json.
	:return: A dict containing the data stored inside ficimage.json
	"""
	try:
		with open(os.path.join(ficimage_path, "ficimage.json"), 'r') as f:
			return json.load(f)
	except FileNotFoundError:
		sys.exit(f"[Loading Config JSON]: File not found. Are you sure there's a ficimage.json file in {ficimage_path}")
	except json.decoder.JSONDecodeError:
		sys.exit("[Loading Config JSON]: Invalid JSON in Config File")


def default_ficimage_settings() -> dict:
	"""
	Returns a dict containing the default config settings for ficimage.
	:return: A dict
	"""
	default_settings = {
		"compress_images": True,
		"default_image_format": "JPEG",
		"max_image_size": 100000
	}
	default_settings_str = '\n'.join([f"{key}: {value}" for key, value in default_settings.items()])
	print(f"\nDefault config settings:"
	      f"\n============================\n"
	      f"{default_settings_str}"
	      f"\n============================\n")
	return default_settings
