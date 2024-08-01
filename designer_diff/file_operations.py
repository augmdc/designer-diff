import os
import glob
import logging

logger = logging.getLogger(__name__)

def read_file(file_path):
    logger.info(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.debug(f"Successfully read file: {file_path}")
        return content
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    logger.info(f"Writing to file: {file_path}")
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.debug(f"Successfully wrote to file: {file_path}")
        return True
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False

def find_designer_files(teleai_dir):
    logger.info(f"Finding Designer files in: {teleai_dir}")
    patterns = [
        os.path.join(teleai_dir, '**', '*Dashboard*.Designer.cs'),
        os.path.join(teleai_dir, '**', 'Dash*.Designer.cs'),
        os.path.join(teleai_dir, '**', '*Loader*.Designer.cs')
    ]
    
    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
    
    # Convert absolute paths to relative paths
    relative_files = [os.path.relpath(file, teleai_dir) for file in all_files]
    
    logger.info(f"Found {len(relative_files)} Designer files")
    for file in relative_files:
        logger.debug(f"Found Designer file: {file}")
    
    return relative_files