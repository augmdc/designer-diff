import os
import glob
import logging
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)

def find_teleai_directory():
    logger.info("Searching for teleai directory")
    common_locations = [
        os.path.expanduser("~"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/GitHub"),
        "C:/",
        "D:/",
    ]
    
    for location in common_locations:
        logger.debug(f"Searching in {location}")
        teleai_dir = search_directory(location)
        if teleai_dir:
            logger.info(f"Found teleai directory: {teleai_dir}")
            return teleai_dir
    
    for drive in ['C:', 'D:', 'E:', 'F:']:
        if os.path.exists(drive):
            logger.debug(f"Searching in drive {drive}")
            teleai_dir = search_directory(drive)
            if teleai_dir:
                logger.info(f"Found teleai directory: {teleai_dir}")
                return teleai_dir
    
    logger.warning("teleai directory not found")
    return None

def search_directory(start_path):
    logger.debug(f"Searching for teleai in {start_path}")
    for root, dirs, files in os.walk(start_path):
        if 'teleai' in dirs:
            teleai_path = os.path.join(root, 'teleai')
            if is_valid_teleai_directory(teleai_path):
                logger.info(f"Valid teleai directory found: {teleai_path}")
                return teleai_path
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['windows', 'program files', 'program files (x86)']]
    logger.debug(f"No valid teleai directory found in {start_path}")
    return None

def is_valid_teleai_directory(path):
    logger.debug(f"Checking if {path} is a valid teleai directory")
    expected_subdirs = ['client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 'DashboardLayouts']
    current_path = path
    for subdir in expected_subdirs:
        current_path = os.path.join(current_path, subdir)
        if not os.path.isdir(current_path):
            logger.debug(f"Missing expected subdirectory: {subdir}")
            return False
    logger.info(f"{path} is a valid teleai directory")
    return True

def get_current_branch(repo_path):
    logger.info(f"Getting current branch for repository: {repo_path}")
    try:
        repo = Repo(repo_path)
        current_branch = repo.active_branch.name
        logger.info(f"Current branch: {current_branch}")
        return current_branch
    except GitCommandError as e:
        logger.error(f"Git command error while getting current branch: {e}")
    except ValueError as e:
        logger.error(f"Invalid repository while getting current branch: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while getting current branch: {e}")
    return None

def find_changed_designer_files(repo_path, branch=None):
    logger.info(f"Finding changed Designer files")
    try:
        repo = Repo(repo_path)
        if branch is None:
            branch = repo.active_branch.name
        logger.info(f"Comparing against branch: {branch}")
        
        changed_files = repo.git.diff('--name-only', branch, '--', '*.Designer.cs').splitlines()
        
        designer_files = [file for file in changed_files if file.endswith('.Designer.cs')]
        
        if not designer_files:
            logger.info("No changed Designer files found")
        else:
            logger.info(f"Found {len(designer_files)} changed Designer files")
            for file in designer_files:
                logger.debug(f"Changed Designer file: {file}")
        
        return designer_files
    except GitCommandError as e:
        logger.error(f"Git command error: {e}")
    except ValueError as e:
        logger.error(f"Invalid repository: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in find_changed_designer_files: {e}")
    return []

def get_file_diff(file_path, branch='develop', teleai_dir=None):
    logger.info(f"Getting diff for {file_path} against {branch} branch")
    try:
        repo = Repo(teleai_dir or os.path.dirname(file_path), search_parent_directories=True)
        relative_path = os.path.relpath(file_path, repo.working_tree_dir)
        logger.debug(f"Relative path: {relative_path}")
        
        try:
            repo.git.ls_tree(branch, relative_path)
        except GitCommandError:
            logger.warning(f"File {relative_path} does not exist in branch {branch}")
            return None

        diff = repo.git.diff(branch, '--', relative_path, ignore_space_at_eol=True, ignore_space_change=True)
        if not diff:
            logger.info(f"No changes detected for {relative_path}")
        else:
            logger.info(f"Changes detected for {relative_path}")
            logger.debug(f"Diff content:\n{diff}")
        return diff
    except GitCommandError as e:
        logger.error(f"Git command error: {e}")
    except ValueError as e:
        logger.error(f"Invalid repository: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_file_diff: {e}")
    return None