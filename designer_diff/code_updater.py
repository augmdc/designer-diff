import os
import logging
from file_operations import read_file, write_file
from code_analyzer import extract_initialize_methods
from code_generator import generate_autogen_content

logger = logging.getLogger(__name__)

class CodeUpdater:
    def __init__(self, teleai_root):
        self.teleai_root = teleai_root

    def update_autogen_file(self, relative_designer_file_path, init_mode=False):
        designer_file_path = os.path.join(self.teleai_root, relative_designer_file_path)
        
        designer_content = read_file(designer_file_path)
        if designer_content is None:
            logger.error(f"Failed to read {designer_file_path}")
            return False, f"Failed to read {designer_file_path}"

        initialize_methods = extract_initialize_methods(designer_content)
        updated_content = generate_autogen_content(designer_file_path, initialize_methods, self.teleai_root)

        autogen_file_path = self.get_autogen_path(designer_file_path)
        if write_file(autogen_file_path, updated_content):
            return True, f"Updated AutoGen file: {autogen_file_path}"
        else:
            logger.error(f"Failed to write AutoGen file: {autogen_file_path}")
            return False, f"Failed to write AutoGen file: {autogen_file_path}"

    def get_autogen_path(self, designer_file_path):
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path).replace('.Designer.cs', '.AutoGen.cs')
        return os.path.join(directory, filename)

    def process_designer_files(self, relative_designer_files, init_mode=False):
        results = []
        for relative_designer_file in relative_designer_files:
            success, message = self.update_autogen_file(relative_designer_file, init_mode)
            results.append((relative_designer_file, success, message))
        return results