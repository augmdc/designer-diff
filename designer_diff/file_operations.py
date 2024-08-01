import os
import logging

logger = logging.getLogger(__name__)

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False

def find_designer_files(teleai_dir):
    dashboard_layouts_dir = os.path.join(teleai_dir, 'client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 'DashboardLayouts')
    
    if not os.path.exists(dashboard_layouts_dir):
        logger.error(f"DashboardLayouts directory not found: {dashboard_layouts_dir}")
        return []

    all_files = []
    for root, dirs, files in os.walk(dashboard_layouts_dir):
        for file in files:
            if file.endswith('.Designer.cs'):
                full_path = os.path.join(root, file)
                all_files.append(full_path)

    relative_files = [os.path.relpath(file, teleai_dir) for file in all_files]
    
    logger.info(f"Found {len(relative_files)} Designer files in the DashboardLayouts directory and its subdirectories")
    for file in relative_files:
        logger.debug(f"Designer file: {file}")
    
    return relative_files