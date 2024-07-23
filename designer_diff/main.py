import argparse
import sys
from designer_diff.git_operations import find_git_root, find_designer_files, get_develop_diff
from designer_diff.diff_handler import DiffHandler
from designer_diff.code_updater import CodeUpdater
from designer_diff.logging_config import logger
from designer_diff.config_manager import config_manager
from designer_diff.file_operations import backup_file, restore_from_backup

def main():
    parser = argparse.ArgumentParser(description="Designer Diff Tool (Develop Branch)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making changes")
    parser.add_argument("--config", help="Path to custom config file")
    parser.add_argument("--rollback", action="store_true", help="Rollback changes from the last run")
    args = parser.parse_args()

    if args.config:
        config_manager.config_file = args.config
        config_manager.load_config()

    git_root = find_git_root()
    if not git_root:
        logger.error("Not in a Git repository")
        sys.exit(1)

    designer_files = find_designer_files(git_root)
    if not designer_files:
        logger.error("No Designer files found")
        sys.exit(1)

    diff_handler = DiffHandler(
        relevant_properties=config_manager.get("relevant_properties"),
        ignored_properties=config_manager.get("ignored_properties")
    )
    code_updater = CodeUpdater(diff_handler)

    if args.rollback:
        rollback(designer_files)
    else:
        process_files(designer_files, args, diff_handler, code_updater)

def process_files(designer_files, args, diff_handler, code_updater):
    backups = []
    updated_files = []

    for file in designer_files:
        logger.info(f"Processing {file}")
        try:
            diff = get_develop_diff(file)
            if diff is None:
                logger.warning(f"No diff found for {file}")
                continue

            if args.dry_run:
                logger.info(f"Dry run: would process diff for {file}")
                logger.info(f"Diff content:\n{diff}")
            else:
                backup_path = backup_file(file)
                if backup_path:
                    backups.append(backup_path)
                    
                changes = diff_handler.analyze_diff(diff)
                if changes:
                    if code_updater.apply_changes_to_file(file, changes):
                        logger.info(f"Successfully updated {file}")
                        updated_files.append(file)
                    else:
                        logger.warning(f"Failed to apply changes to {file}")
                else:
                    logger.info(f"No relevant changes found for {file}")
        except Exception as e:
            logger.error(f"Error processing {file}: {str(e)}")

    if args.dry_run:
        logger.info("Dry run completed. No changes were made.")
    else:
        logger.info(f"All files processed. Updated files: {len(updated_files)}")
        logger.info(f"Backups created: {len(backups)}")

def rollback(designer_files):
    for file in designer_files:
        backup_path = f"{file}.bak"
        if restore_from_backup(backup_path):
            logger.info(f"Rolled back changes for {file}")
        else:
            logger.warning(f"No backup found or unable to rollback for {file}")

    logger.info("Rollback process completed.")

if __name__ == "__main__":
    main()