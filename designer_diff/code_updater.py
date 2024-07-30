import os
import logging

class CodeUpdater:
    def __init__(self, diff_handler, teleai_root):
        self.diff_handler = diff_handler
        self.teleai_root = teleai_root
        self.logger = logging.getLogger(__name__)

    def update_autogen_file(self, designer_file_path, changes):
        try:
            self.logger.debug(f"Starting update process for {designer_file_path}")
            autogen_file_path = self._get_autogen_path(designer_file_path)
            self.logger.debug(f"AutoGen file path: {autogen_file_path}")
            
            if not os.path.exists(autogen_file_path):
                self.logger.info(f"AutoGen file not found. Creating: {autogen_file_path}")
                self._create_autogen_file(designer_file_path, autogen_file_path)
            else:
                self.logger.debug(f"AutoGen file already exists: {autogen_file_path}")

            with open(autogen_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            self.logger.debug(f"Current content of {autogen_file_path}:\n{content}")

            updated_content = self._apply_changes(content, changes)

            self.logger.debug(f"Updated content for {autogen_file_path}:\n{updated_content}")

            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            self.logger.info(f"Successfully updated AutoGen file: {autogen_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            return False

    def _get_autogen_path(self, designer_file_path):
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path)
        autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
        return os.path.join(directory, autogen_filename)

    def _create_autogen_file(self, designer_file_path, autogen_file_path):
        try:
            class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
            
            relative_path = os.path.relpath(os.path.dirname(designer_file_path), self.teleai_root)
            namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))
            
            content = f"""using System;
using System.Windows.Forms;
using System.Drawing;

namespace {namespace}
{{
    public partial class {class_name}
    {{
        protected override void InitializeLayoutOptions()
        {{
            // Auto-generated code will be inserted here
        }}
    }}
}}
"""
            self.logger.debug(f"Creating new AutoGen file with content:\n{content}")
            
            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.logger.info(f"Successfully created AutoGen file: {autogen_file_path}")
        except Exception as e:
            self.logger.error(f"Error creating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            raise

    def _apply_changes(self, content, changes):
        lines = content.split('\n')
        insert_index = self._find_insert_index(lines)

        new_lines = []
        for layout, components in changes.items():
            for component, value in components.items():
                new_line = f"            {layout}[{component}] = new ControlLayoutOptions(new Point({value}));"
                new_lines.append(new_line)
                self.logger.debug(f"Adding line: {new_line}")

        lines[insert_index:insert_index] = new_lines
        return '\n'.join(lines)

    def _find_insert_index(self, lines):
        for i, line in enumerate(lines):
            if "Auto-generated code will be inserted here" in line:
                return i + 1  # Insert after the comment
        return len(lines) - 2  # If comment not found, insert at the end of the class