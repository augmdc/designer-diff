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
    dashboard_layouts_dir = os.path.join(teleai_dir, 'client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 'DashboardLayouts')
    
    logger.debug(f"Looking for DashboardLayouts directory: {dashboard_layouts_dir}")
    if not os.path.exists(dashboard_layouts_dir):
        logger.error(f"DashboardLayouts directory not found: {dashboard_layouts_dir}")
        return []

    pattern = 'Dash*.Designer.cs'
    logger.debug(f"Using search pattern: {pattern}")
    
    all_files = []
    for root, dirs, files in os.walk(dashboard_layouts_dir):
        for file in files:
            if file.startswith('Dash') and file.endswith('.Designer.cs'):
                full_path = os.path.join(root, file)
                all_files.append(full_path)
                logger.debug(f"Found Designer file: {full_path}")

    logger.debug(f"Found {len(all_files)} files matching the pattern")
    
    # Convert absolute paths to relative paths
    relative_files = [os.path.relpath(file, teleai_dir) for file in all_files]
    
    logger.info(f"Found {len(relative_files)} Dashboard Designer files")
    for file in relative_files:
        logger.debug(f"Relative path of Dashboard Designer file: {file}")
    
    return relative_files