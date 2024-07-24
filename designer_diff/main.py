import os
from git_operations import find_git_root, find_designer_files, get_file_diff
from diff_handler import DiffHandler
from code_updater import CodeUpdater

def main():
    git_root = find_git_root()
    if not git_root:
        print("Error: Not in a Git repository")
        return

    designer_files = find_designer_files(git_root)
    if not designer_files:
        print("Error: No Designer files found")
        return

    diff_handler = DiffHandler()
    code_updater = CodeUpdater(diff_handler)

    for file in designer_files:
        print(f"Processing {file}")
        relative_path = os.path.relpath(file, git_root)
        diff = get_file_diff(relative_path, 'develop')
        if diff:
            changes = diff_handler.process_diff(diff)
            if changes:
                if code_updater.update_autogen_file(file, changes):
                    print(f"Updated AutoGen file for {file}")
                else:
                    print(f"Failed to update AutoGen file for {file}")
            else:
                print(f"No relevant changes in {file}")
        else:
            print(f"No diff found for {file}")

    print("All files processed.")

if __name__ == "__main__":
    main()