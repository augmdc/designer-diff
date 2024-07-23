"""
designer_diff

A tool for analyzing and updating Designer files based on Git diffs against the develop branch.
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__license__ = "MIT"

from .git_operations import find_git_root, find_designer_files, get_develop_diff, ensure_develop_branch_exists
from .diff_handler import DiffHandler
from .code_updater import CodeUpdater
from .logging_config import logger
from .config_manager import config_manager

# Initialize logging
logger.info(f"Initializing designer_diff version {__version__}")

# Ensure the configuration is loaded
config_manager.load_config()

__all__ = [
    "find_git_root",
    "find_designer_files",
    "get_develop_diff",
    "ensure_develop_branch_exists",
    "DiffHandler",
    "CodeUpdater",
    "logger",
    "config_manager",
]

def initialize():
    """
    Perform any necessary initialization for the package.
    This function can be called explicitly if needed.
    """
    logger.info("Performing designer_diff initialization")
    if ensure_develop_branch_exists():
        logger.info("Develop branch is ready for use")
    else:
        logger.warning("Failed to ensure develop branch exists. Some operations may fail.")

# Call initialize function when the package is imported
initialize()