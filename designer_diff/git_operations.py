import os
from git import Repo, GitCommandError
from pathlib import Path
import glob
from designer_diff.logging_config import logger

def find_git_root(path='.'):
    """
    Find the root directory of the Git repository containing the given path.
    
    :param path: Path to start searching from (default is current directory)
    :return: Absolute path to the Git root directory, or None if not found
    """
    try:
        repo = Repo(path, search_parent_directories=True)
        return repo.git.rev_parse("--show-toplevel")
    except GitCommandError:
        return None

def get_develop_diff(file_path):
    """
    Get the diff between the current branch and the develop branch for a file.
    
    :param file_path: Path to the file, relative to the repository root
    :return: A string containing the diff, or None if there's an error
    """
    try:
        repo = Repo(find_git_root(file_path))
        current_branch = repo.active_branch.name
        if current_branch == 'develop':
            logger.warning("Current branch is already develop. No diff available.")
            return None
        return repo.git.diff('develop', current_branch, '--', file_path)
    except GitCommandError as e:
        logger.error(f"Error getting diff against develop branch: {e}")
        return None

def find_designer_files(git_root):
    """
    Find all Designer files matching the specified pattern.
    
    :param git_root: The root directory of the Git repository
    :return: A list of paths to Designer files
    """
    pattern = os.path.join(git_root, 'teleai', 'client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 
                           'DashboardLayouts', '*', 'Dash*.Designer.cs')
    designer_files = [str(p) for p in glob.glob(pattern)]
    logger.info(f"Found {len(designer_files)} Designer files")
    return designer_files

def ensure_develop_branch_exists():
    """
    Ensure that the develop branch exists in the repository.
    
    :return: True if the develop branch exists or was created, False otherwise
    """
    try:
        repo = Repo(find_git_root())
        if 'develop' not in repo.branches:
            logger.warning("Develop branch not found. Creating it...")
            repo.git.branch('develop')
            logger.info("Develop branch created successfully")
        return True
    except GitCommandError as e:
        logger.error(f"Error ensuring develop branch exists: {e}")
        return False