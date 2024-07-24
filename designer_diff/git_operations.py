import os
from git import Repo, GitCommandError

def find_git_root(path='.'):
    try:
        repo = Repo(path, search_parent_directories=True)
        return repo.working_tree_dir
    except GitCommandError:
        return None

def find_designer_files(git_root):
    pattern = os.path.join(git_root, 'teleai', 'client', 'TeleAiClient', 'UI2', 'VehicleUIControls', 
                           'DashboardLayouts', '*', 'Dash*.Designer.cs')
    return [p for p in glob.glob(pattern)]

def get_file_diff(file_path, branch='develop'):
    try:
        repo = Repo(find_git_root(file_path))
        return repo.git.diff(branch, '--', file_path)
    except GitCommandError as e:
        print(f"Error getting diff: {e}")
        return None