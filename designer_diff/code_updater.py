import os
import logging

class CodeUpdater:
    def __init__(self, diff_handler):
        self.diff_handler = diff_handler
        self.logger = logging.getLogger(__name__)

    def update_autogen_file(self, designer_file_path, changes):
        try:
            autogen_file_path = self._get_autogen_path(designer_file_path)
            
            if not os.path.exists(autogen_file_path):
                self.logger.info(f"AutoGen file not found. Creating: {autogen_file_path}")
                self._create_autogen_file(designer_file_path, autogen_file_path)

            with open(autogen_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            updated_content = self._apply_changes(content, changes)

            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            self.logger.info(f"Successfully updated AutoGen file: {autogen_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating AutoGen file {autogen_file_path}: {str(e)}")
            return False

    def _get_autogen_path(self, designer_file_path):
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path)
        autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
        return os.path.join(directory, autogen_filename)

    def _create_autogen_file(self, designer_file_path, autogen_file_path):
        class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
        
        teleai_root = self._find_teleai_root(designer_file_path)
        if not teleai_root:
            raise ValueError(f"Could not find teleai root directory for {designer_file_path}")
        
        relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
        namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))
        
        content = f"""using System;
using System.Windows.Forms;

namespace {namespace}
{{
    public partial class {class_name}
    {{
        // Auto-generated code will be inserted here
    }}
}}
"""
        with open(autogen_file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def _find_teleai_root(self, path):
        current = os.path.dirname(path)
        while current != os.path.dirname(current):  # Stop at the root
            if 'teleai' in os.listdir(current):
                return os.path.join(current, 'teleai')
            current = os.path.dirname(current)
        return None  # If teleai root is not found

    def _apply_changes(self, content, changes):
        lines = content.split('\n')
        insert_index = self._find_insert_index(lines)

        new_lines = []
        for component, properties in changes.items():
            for prop, value in properties.items():
                new_line = f"        this.{component}.{prop} = {value};"
                new_lines.append(new_line)
                self.logger.debug(f"Adding line: {new_line}")

        lines[insert_index:insert_index] = new_lines
        return '\n'.join(lines)

    def _find_insert_index(self, lines):
        for i, line in enumerate(lines):
            if "Auto-generated code will be inserted here" in line:
                return i + 1  # Insert after the comment
        return len(lines) - 2  # If comment not found, insert at the end of the class