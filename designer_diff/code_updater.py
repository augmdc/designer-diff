import os
import subprocess
from file_operations import read_file, write_file
from code_analyzer import extract_initialize_methods
from code_generator import generate_autogen_content

class CodeUpdater:
    def __init__(self, teleai_root):
        self.teleai_root = teleai_root

    def update_autogen_file(self, designer_file_path, init_mode=False):
        if not init_mode and not self.has_file_changed(designer_file_path):
            return True, f"No changes detected in {designer_file_path}"

        designer_content = read_file(designer_file_path)
        if designer_content is None:
            return False, f"Failed to read {designer_file_path}"

        initialize_methods = extract_initialize_methods(designer_content)

        autogen_content = generate_autogen_content(designer_file_path, initialize_methods, self.teleai_root)

        autogen_file_path = self.get_autogen_path(designer_file_path)
        if write_file(autogen_file_path, autogen_content):
            return True, f"Updated AutoGen file: {autogen_file_path}"
        else:
            return False, f"Failed to write AutoGen file: {autogen_file_path}"

    def has_file_changed(self, file_path):
        try:
            result = subprocess.run(['git', 'diff', '--exit-code', 'HEAD', file_path], 
                                    cwd=self.teleai_root, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            return result.returncode != 0
        except subprocess.CalledProcessError:
            return True

    def get_autogen_path(self, designer_file_path):
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path).replace('.Designer.cs', '.AutoGen.cs')
        return os.path.join(directory, filename)

    def process_designer_files(self, designer_files, init_mode=False):
        results = []
        for designer_file in designer_files:
            success, message = self.update_autogen_file(designer_file, init_mode)
            results.append((designer_file, success, message))
        return results