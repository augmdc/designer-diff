import argparse
import logging
from git_operations import find_changed_designer_files, get_current_branch
from code_updater import CodeUpdater
from utils import find_teleai_directory
from file_operations import find_designer_files

def configure_logging(verbosity):
    log_levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    logging.basicConfig(level=log_levels.get(verbosity, logging.DEBUG),
                        format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    parser = argparse.ArgumentParser(description='Update AutoGen files based on Designer file changes.')
    parser.add_argument('--teleai-root', help='Path to the teleai root directory for namespace generation')
    parser.add_argument('--init', action='store_true', help='Initialize AutoGen files for all Designer files')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity (e.g., -v, -vv, -vvv)')
    parser.add_argument('--branch', help='Git branch to compare against (default: develop)')
    args = parser.parse_args()

    configure_logging(args.verbosity)

    teleai_dir = find_teleai_directory()
    if not teleai_dir:
        logging.error("Error: Not inside a Git repository or teleai directory not found.")
        return

    teleai_root = args.teleai_root or teleai_dir

    if args.init:
        designer_files = find_designer_files(teleai_dir)
    else:
        branch = args.branch or 'develop'  # Default to 'develop' if not specified
        logging.info(f"Comparing changes against branch: {branch}")
        designer_files = find_changed_designer_files(teleai_root, branch)

    if not designer_files:
        logging.warning("No Designer files found or changed")
        return

    logging.info(f"Processing the following Designer files:")
    for file in designer_files:
        logging.info(f"  - {file}")

    updater = CodeUpdater(teleai_root)
    results = updater.process_designer_files(designer_files, init_mode=args.init)

    for designer_file, success, message in results:
        if success:
            logging.info(f"{designer_file}: Success - {message}")
        else:
            logging.error(f"{designer_file}: Failure - {message}")

if __name__ == "__main__":
    main()