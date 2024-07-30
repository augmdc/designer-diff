import os
import logging
import argparse
from git_operations import find_teleai_directory, find_designer_files, get_file_diff
from diff_handler import DiffHandler
from code_updater import CodeUpdater

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def find_teleai_root(teleai_dir):
    """Find the teleai root directory based on the teleai directory."""
    current_dir = teleai_dir
    while current_dir != os.path.dirname(current_dir):  # Stop at the root directory
        if os.path.basename(current_dir).lower() == 'teleai':
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return teleai_dir  # If no 'teleai' directory found, return the original directory

def main():
    parser = argparse.ArgumentParser(description='Update AutoGen files based on Designer file changes.')
    parser.add_argument('--teleai-dir', help='Path to the teleai directory for finding Designer files')
    parser.add_argument('--teleai-root', help='Path to the teleai root directory for namespace generation')
    parser.add_argument('--branch', default='develop', help='Git branch to compare against (default: develop)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Find teleai directory
    teleai_dir = args.teleai_dir or find_teleai_directory()
    if not teleai_dir:
        logger.error("Error: teleai directory not found.")
        logger.info("The script searched common locations and drives but couldn't find the teleai directory.")
        logger.info("Please ensure the teleai directory exists in your project structure or specify it using --teleai-dir.")
        return

    logger.info(f"Using teleai directory for finding Designer files: {teleai_dir}")

    # Find teleai root directory
    teleai_root = args.teleai_root or find_teleai_root(teleai_dir)
    logger.info(f"Using teleai root directory for namespace generation: {teleai_root}")

    designer_files = find_designer_files(teleai_dir)
    if not designer_files:
        logger.error("No Designer files found")
        return

    logger.info(f"Found {len(designer_files)} Designer files.")
    for file in designer_files:
        logger.debug(f"Designer file: {file}")

    diff_handler = DiffHandler()
    code_updater = CodeUpdater(diff_handler, teleai_root)

    for file in designer_files:
        logger.info(f"Processing {file}")
        diff = get_file_diff(file, args.branch, teleai_dir)
        changes = {}
        if diff is not None:
            logger.debug(f"Diff found for {file}:\n{diff}")
            changes = diff_handler.process_diff(diff)
            logger.debug(f"Processed changes: {changes}")

        success, content = code_updater.update_autogen_file(file, changes)
        if success:
            logger.info(f"Updated AutoGen file for {file}")
            logger.info(f"Full content of updated AutoGen file:\n{content}")
        else:
            logger.warning(f"Failed to update AutoGen file for {file}")

    logger.info("All files processed.")

if __name__ == "__main__":
    main()