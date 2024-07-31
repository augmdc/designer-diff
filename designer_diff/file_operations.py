import os
import glob

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_file(file_path, content):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")
        return False

def find_designer_files(teleai_dir):
    patterns = [
        os.path.join(teleai_dir, '**', '*Dashboard*.Designer.cs'),
        os.path.join(teleai_dir, '**', 'Dash*.Designer.cs'),
        os.path.join(teleai_dir, '**', '*Loader*.Designer.cs')
    ]
    
    all_files = []
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        all_files.extend(files)
    
    return list(set(all_files))