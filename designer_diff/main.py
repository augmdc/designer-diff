import os
import logging
import argparse
from git_operations import find_teleai_directory, find_designer_files, get_file_diff
from diff_handler import DiffHandler
from code_updater import CodeUpdater

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Update AutoGen files based on Designer file changes.')
    parser.add_argument('--teleai-dir', help='Path to the teleai directory')
    parser.add_argument('--branch', default='develop', help='Git branch to compare against (default: develop)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    teleai_dir = args.teleai_dir or find_teleai_directory()
    if not teleai_dir:
        logger.error("Error: teleai directory not found.")
        logger.info("The script searched common locations and drives but couldn't find the teleai directory.")
        logger.info("Please ensure the teleai directory exists in your project structure or specify it using --teleai-dir.")
        return

    logger.info(f"Using teleai directory: {teleai_dir}")

    designer_files = find_designer_files(teleai_dir)
    if not designer_files:
        logger.error("No Designer files found")
        return

    logger.info(f"Found {len(designer_files)} Designer files.")

    diff_handler = DiffHandler()
    code_updater = CodeUpdater(diff_handler)

    for file in designer_files:
        logger.info(f"Processing {file}")
        diff = get_file_diff(file, args.branch, teleai_dir)
        if diff is not None:
            changes = diff_handler.process_diff(diff)
            if changes:
                if code_updater.update_autogen_file(file, changes):
                    logger.info(f"Updated AutoGen file for {file}")
                else:
                    logger.warning(f"Failed to update AutoGen file for {file}")
            else:
                logger.info(f"No relevant changes in {file}")
        else:
            logger.info(f"No diff found for {file}")

    logger.info("All files processed.")

if __name__ == "__main__":
    main()