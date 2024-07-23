import os
from pathlib import Path
import shutil
from designer_diff.logging_config import logger

def read_file(file_path):
    """
    Read the contents of a file.

    :param file_path: Path to the file to be read
    :return: The contents of the file as a string, or None if an error occurs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    """
    Write content to a file.

    :param file_path: Path to the file to be written
    :param content: Content to write to the file
    :return: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"Successfully wrote to file {file_path}")
        return True
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False

def sort_file_contents(file_path):
    """
    Sort the contents of a file alphabetically.

    :param file_path: Path to the file to be sorted
    :return: True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        sorted_lines = sorted(lines, key=str.lower)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(sorted_lines)
        logger.info(f"Successfully sorted contents of file {file_path}")
        return True
    except IOError as e:
        logger.error(f"Error sorting file {file_path}: {e}")
        return False

def get_relative_path(path, start):
    """
    Get the relative path from start to path.

    :param path: The target path
    :param start: The starting path
    :return: The relative path as a string
    """
    return os.path.relpath(path, start)

def ensure_dir(directory):
    """
    Ensure that a directory exists, creating it if necessary.

    :param directory: The directory path to ensure
    :return: True if the directory exists or was created, False otherwise
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")
        return True
    except OSError as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

def backup_file(file_path):
    """
    Create a backup of the specified file.

    :param file_path: Path to the file to be backed up
    :return: Path to the backup file if successful, None otherwise
    """
    try:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup of {file_path} at {backup_path}")
        return backup_path
    except IOError as e:
        logger.error(f"Error creating backup of file {file_path}: {e}")
        return None

def restore_from_backup(backup_path):
    """
    Restore a file from its backup.

    :param backup_path: Path to the backup file
    :return: True if successful, False otherwise
    """
    try:
        original_path = backup_path[:-4]  # Remove '.bak'
        shutil.move(backup_path, original_path)
        logger.info(f"Restored {original_path} from backup {backup_path}")
        return True
    except IOError as e:
        logger.error(f"Error restoring from backup {backup_path}: {e}")
        return False