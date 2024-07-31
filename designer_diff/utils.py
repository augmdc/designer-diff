import os

def find_teleai_directory():
    common_locations = [
        os.path.expanduser("~"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/GitHub"),
        "C:/",
        "D:/",
    ]
    
    for location in common_locations:
        teleai_dir = search_directory(location)
        if teleai_dir:
            return teleai_dir
    
    for drive in ['C:', 'D:', 'E:', 'F:']:
        if os.path.exists(drive):
            teleai_dir = search_directory(drive)
            if teleai_dir:
                return teleai_dir
    
    return None

def search_directory(start_path):
    for root, dirs, files in os.walk(start_path):
        if 'teleai' in dirs:
            teleai_path = os.path.join(root, 'teleai')
            if is_valid_teleai_directory(teleai_path):
                return teleai_path
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ['windows', 'program files', 'program files (x86)']]
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