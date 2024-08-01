import os
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

def get_current_branch(repo_path):
    try:
        repo = Repo(repo_path)
        return repo.active_branch.name
    except Exception as e:
        logger.error(f"Error getting current branch: {e}")
    return None

def find_changed_designer_files(repo_path, branch=None):
    try:
        repo = Repo(repo_path)
        if branch is None:
            branch = repo.active_branch.name
        
        logger.debug(f"Comparing changes with branch: {branch}")
        
        # Get changed Designer files
        changed_files = repo.git.diff('--name-only', branch, '--', '*.Designer.cs').splitlines()
        logger.debug(f"All changed Designer files: {changed_files}")
        
        # Define the correct directory path
        dashboard_layouts_dir = os.path.normpath('client/TeleAiClient/UI2/VehicleUIControls/DashboardLayouts')
        logger.debug(f"Looking for files in directory: {dashboard_layouts_dir}")
        
        # Filter files
        filtered_files = []
        for file in changed_files:
            normalized_file = os.path.normpath(file)
            logger.debug(f"Checking file: {normalized_file}")
            if normalized_file.startswith(dashboard_layouts_dir):
                logger.debug(f"File is in correct directory")
                filtered_files.append(file)
            else:
                logger.debug(f"File is not in correct directory")
        
        logger.info(f"Found {len(filtered_files)} changed Designer files in the DashboardLayouts directory or its subdirectories")
        for file in filtered_files:
            logger.info(f"Changed Designer file: {file}")
        
        return filtered_files
    except Exception as e:
        logger.error(f"Error finding changed Designer files: {e}")
        logger.exception(e)  # This will log the full stack trace
    return []

def get_file_diff(file_path, branch='develop', teleai_dir=None):
    try:
        repo = Repo(teleai_dir or os.path.dirname(file_path), search_parent_directories=True)
        relative_path = os.path.relpath(file_path, repo.working_tree_dir)
        
        try:
            repo.git.ls_tree(branch, relative_path)
        except GitCommandError:
            return None

        return repo.git.diff(branch, '--', relative_path, ignore_space_at_eol=True, ignore_space_change=True)
    except Exception as e:
        logger.error(f"Error getting file diff: {e}")
    return None