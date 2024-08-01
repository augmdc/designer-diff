import os
from git import Repo, InvalidGitRepositoryError

def find_teleai_directory():
    try:
        # Start from the current directory and search upwards
        repo = Repo(os.getcwd(), search_parent_directories=True)
        return repo.working_tree_dir
    except InvalidGitRepositoryError:
        print("Error: Not inside a Git repository.")
        return None

def get_relative_path(path, start):
    return os.path.relpath(path, start)

def get_autogen_path(designer_file_path):
    directory = os.path.dirname(designer_file_path)
    filename = os.path.basename(designer_file_path)
    autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
    return os.path.join(directory, autogen_filename)