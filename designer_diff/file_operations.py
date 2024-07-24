import os
from pathlib import Path

def read_file(file_path):
    """
    Read the contents of a file.

    :param file_path: Path to the file to be read
    :return: The contents of the file as a string, or None if an error occurs
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    """
    Write content to a file.

    :param file_path: Path to the file to be written
    :param content: Content to write to the file
    :return: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def ensure_dir(directory):
    """
    Ensure that a directory exists, creating it if necessary.

    :param directory: The directory path to ensure
    :return: True if the directory exists or was created, False otherwise
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory {directory}: {e}")
        return False

def get_relative_path(path, start):
    """
    Get the relative path from start to path.

    :param path: The target path
    :param start: The starting path
    :return: The relative path as a string
    """
    return os.path.relpath(path, start)