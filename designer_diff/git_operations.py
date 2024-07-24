import os
import glob
import logging
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)

def find_teleai_directory():
    common_locations = [
        os.path.expanduser("~"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/GitHub"),
        "C:/",
        "D:/",
    ]
    
    for location in common_locations:
        teleai_dir = search_directory(location)
        if teleai_dir:
            return teleai_dir
    
    for drive in ['C:', 'D:', 'E:', 'F:']:
        if os.path.exists(drive):
            teleai_dir = search_directory(drive)
            if teleai_dir:
                return teleai_dir
    
    return None

def search_directory(start_path):
    for root, dirs, files in os.walk(start_path):
        if 'teleai' in dirs:
            teleai_path = os.path.join(root, 'teleai')
            if is_valid_teleai_directory(teleai_path):
                return teleai_path
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['windows', 'program files', 'program files (x86)']]
    return None

def is_valid_teleai_directory(path):
    expected_subdirs = ['client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 'DashboardLayouts']
    current_path = path
    for subdir in expected_subdirs:
        current_path = os.path.join(current_path, subdir)
        if not os.path.isdir(current_path):
            return False
    return True

def find_designer_files(teleai_dir):
    pattern = os.path.join(teleai_dir, 'client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 
                           'DashboardLayouts', '*', 'Dash*.Designer.cs')
    files = glob.glob(pattern)
    if not files:
        logger.warning(f"No Designer files found in {pattern}")
    return files

def get_file_diff(file_path, branch='develop', teleai_dir=None):
    try:
        repo = Repo(teleai_dir or os.path.dirname(file_path), search_parent_directories=True)
        relative_path = os.path.relpath(file_path, repo.working_tree_dir)
        
        # Check if the file exists in the specified branch
        try:
            repo.git.ls_tree(branch, relative_path)
        except GitCommandError:
            logger.warning(f"File {relative_path} does not exist in branch {branch}")
            return None

        diff = repo.git.diff(branch, '--', relative_path)
        if not diff:
            logger.info(f"No changes detected for {relative_path}")
        return diff
    except GitCommandError as e:
        logger.error(f"Git command error: {e}")
    except ValueError as e:
        logger.error(f"Invalid repository: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_file_diff: {e}")
    return None