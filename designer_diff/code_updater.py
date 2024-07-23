import re
from designer_diff.file_operations import read_file, write_file
from designer_diff.logging_config import logger

class CodeUpdater:
    def __init__(self, diff_handler):
        self.diff_handler = diff_handler

    def apply_changes_to_file(self, file_path, changes):
        """
        Apply changes directly to a file.

        :param file_path: Path to the file to be updated
        :param changes: Dictionary of changes to apply
        :return: True if the file was updated, False otherwise
        """
        try:
            file_content = read_file(file_path)
            if file_content is None:
                logger.error(f"Failed to read file: {file_path}")
                return False

            updated_content = self.apply_changes(file_content, changes)
            if updated_content == file_content:
                logger.info(f"No changes were necessary for {file_path}")
                return False

            if write_file(file_path, updated_content):
                logger.info(f"Successfully updated {file_path}")
                return True
            else:
                logger.error(f"Failed to write updated content to {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error applying changes to file {file_path}: {str(e)}")
            return False

    def apply_changes(self, content, changes):
        """
        Apply the identified changes to the file content.

        :param content: The original file content
        :param changes: Dictionary of changes to apply
        :return: Updated file content
        """
        lines = content.split('\n')
        for component, properties in changes.items():
            for prop, value in properties.items():
                pattern = rf'(this\.{component}\.{prop}\s*=\s*).*;'
                replacement = rf'\1{value};'
                new_lines = []
                for line in lines:
                    new_line = re.sub(pattern, replacement, line)
                    if new_line != line:
                        logger.debug(f"Changed line: '{line}' to '{new_line}'")
                    new_lines.append(new_line)
                lines = new_lines
        
        return '\n'.join(lines)

    def update_autogen_file(self, designer_file_path, autogen_file_path, changes):
        """
        Update an AutoGen file based on changes in a Designer file.

        :param designer_file_path: Path to the Designer file
        :param autogen_file_path: Path to the AutoGen file to be updated
        :param changes: Dictionary of changes to apply
        :return: True if the AutoGen file was updated, False otherwise
        """
        try:
            autogen_content = read_file(autogen_file_path)
            if autogen_content is None:
                logger.error(f"Failed to read AutoGen file: {autogen_file_path}")
                return False

            updated_content = self.apply_autogen_changes(autogen_content, changes)
            if updated_content == autogen_content:
                logger.info(f"No changes were necessary for AutoGen file: {autogen_file_path}")
                return False

            if write_file(autogen_file_path, updated_content):
                logger.info(f"Successfully updated AutoGen file: {autogen_file_path}")
                return True
            else:
                logger.error(f"Failed to write updated content to AutoGen file: {autogen_file_path}")
                return False
        except Exception as e:
            logger.error(f"Error updating AutoGen file {autogen_file_path}: {str(e)}")
            return False

    def apply_autogen_changes(self, content, changes):
        """
        Apply changes to an AutoGen file.

        :param content: The original AutoGen file content
        :param changes: Dictionary of changes to apply
        :return: Updated AutoGen file content
        """
        lines = content.split('\n')
        for component, properties in changes.items():
            for prop, value in properties.items():
                pattern = rf'(this\.{component}\.{prop}\s*=\s*).*;'
                replacement = rf'\1{value};'
                comment_pattern = rf'//\s*{component}\.{prop}:'
                comment_replacement = f'// {component}.{prop}: {value}'
                new_lines = []
                for line in lines:
                    new_line = re.sub(pattern, replacement, line)
                    new_line = re.sub(comment_pattern, comment_replacement, new_line)
                    if new_line != line:
                        logger.debug(f"Changed AutoGen line: '{line}' to '{new_line}'")
                    new_lines.append(new_line)
                lines = new_lines
        
        return '\n'.join(lines)