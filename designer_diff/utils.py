import os
from git import Repo, InvalidGitRepositoryError

def find_teleai_directory():
    try:
        # Find the Git repository root
        repo = Repo(os.getcwd(), search_parent_directories=True)
        git_root = repo.git.rev_parse("--show-toplevel")
        
        # Check if this is a valid teleai directory
        if is_valid_teleai_directory(git_root):
            return git_root
        else:
            return None
    except InvalidGitRepositoryError:
        print("Error: Not inside a Git repository.")
        return None

def is_valid_teleai_directory(path):
    expected_subdirs = ['client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 'DashboardLayouts']
    current_path = path
    for subdir in expected_subdirs:
        current_path = os.path.join(current_path, subdir)
        if not os.path.isdir(current_path):
            return False
    return True

def get_relative_path(path, start):
    return os.path.relpath(path, start)

def get_autogen_path(designer_file_path):
    directory = os.path.dirname(designer_file_path)
    filename = os.path.basename(designer_file_path)
    autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
    return os.path.join(directory, autogen_filename)