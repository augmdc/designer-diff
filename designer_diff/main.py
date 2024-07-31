import argparse
import logging
from file_operations import find_designer_files
from code_updater import CodeUpdater
from utils import find_teleai_directory

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
    parser.add_argument('--teleai-dir', help='Path to the teleai directory for finding Designer files')
    parser.add_argument('--teleai-root', help='Path to the teleai root directory for namespace generation')
    parser.add_argument('--init', action='store_true', help='Initialize AutoGen files for all Designer files')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='Increase output verbosity (e.g., -v, -vv, -vvv)')
    args = parser.parse_args()

    # Configure logging based on verbosity argument
    configure_logging(args.verbosity)

    # Log the start of the program
    logging.info("Starting AutoGen file update process")

    # Find teleai directory
    teleai_dir = args.teleai_dir or find_teleai_directory()
    if not teleai_dir:
        logging.error("Error: teleai directory not found.")
        return

    logging.info(f"Using teleai directory: {teleai_dir}")

    # Find teleai root directory (assuming it's the same as teleai_dir for now)
    teleai_root = args.teleai_root or teleai_dir
    logging.info(f"Using teleai root directory: {teleai_root}")

    # Find Designer files
    designer_files = find_designer_files(teleai_dir)

    # TESTING - USE ONLY DashHigway Designer file
    test_file_name = [item for item in designer_files if item == 'C:\\Users\\achabris\\source\\repos\\teleai\\client\\TeleAiClient\\UI2\\VehicleUIControls\\DashboardLayouts\\Truck\\DashHighway.Designer.cs']

    if not designer_files:
        logging.warning("No Designer files found")
        return

    logging.info(f"Found {len(designer_files)} Designer files")

    # Create CodeUpdater instance
    updater = CodeUpdater(teleai_root)

    # Process each Designer file
    #results = updater.process_designer_files(designer_files, init_mode=args.init)

    # TESTING
    results = updater.process_designer_files(test_file_name, init_mode=args.init)

    # Print results
    for designer_file, success, message in results:
        if success:
            logging.info(f"{designer_file}: Success - {message}")
        else:
            logging.error(f"{designer_file}: Failure - {message}")

    logging.info("All files processed.")

if __name__ == "__main__":
    main()