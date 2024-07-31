import argparse
from file_operations import find_designer_files
from code_updater import CodeUpdater
from utils import find_teleai_directory

def main():
    parser = argparse.ArgumentParser(description='Update AutoGen files based on Designer file changes.')
    parser.add_argument('--teleai-dir', help='Path to the teleai directory for finding Designer files')
    parser.add_argument('--teleai-root', help='Path to the teleai root directory for namespace generation')
    parser.add_argument('--init', action='store_true', help='Initialize AutoGen files for all Designer files')
    args = parser.parse_args()

    # Find teleai directory
    teleai_dir = args.teleai_dir or find_teleai_directory()
    if not teleai_dir:
        print("Error: teleai directory not found.")
        return

    # Find teleai root directory (assuming it's the same as teleai_dir for now)
    teleai_root = args.teleai_root or teleai_dir

    # Find Designer files
    designer_files = find_designer_files(teleai_dir)
    if not designer_files:
        print("No Designer files found")
        return

    # Create CodeUpdater instance
    updater = CodeUpdater(teleai_root)

    # Process each Designer file
    results = updater.process_designer_files(designer_files, init_mode=args.init)

    # Print results
    for designer_file, success, message in results:
        print(f"{designer_file}: {'Success' if success else 'Failure'} - {message}")

    print("All files processed.")

if __name__ == "__main__":
    main()