import os
import logging
import re

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
                content = self._create_autogen_file(designer_file_path, autogen_file_path)
            else:
                self.logger.debug(f"AutoGen file already exists: {autogen_file_path}")
                with open(autogen_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                content = self._check_and_fix_format(content, designer_file_path)

            self.logger.debug(f"Current content of {autogen_file_path}:\n{content}")

            designer_content = self._read_designer_file(designer_file_path)
            initialize_layout_content = self._extract_initialize_layout(designer_content)
            
            updated_content = self._apply_changes(content, changes, initialize_layout_content)

            self.logger.debug(f"Updated content for {autogen_file_path}:\n{updated_content}")

            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)

            self.logger.info(f"Successfully updated AutoGen file: {autogen_file_path}")
            return True, updated_content
        except Exception as e:
            self.logger.error(f"Error updating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            return False, None

    def _check_and_fix_format(self, content, designer_file_path):
        class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
        relative_path = os.path.relpath(os.path.dirname(designer_file_path), self.teleai_root)
        namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))

        expected_structure = f"""using System;
using System.Windows.Forms;
using System.Drawing;

namespace {namespace}
{{
    public partial class {class_name}
    {{
        protected override void InitializeLayoutOptions()
        {{
"""

        if not content.startswith(expected_structure):
            self.logger.info(f"AutoGen file format is incorrect. Fixing the format.")
            fixed_content = expected_structure
            
            # Extract existing InitializeLayoutOptions content if present
            match = re.search(r'protected override void InitializeLayoutOptions\(\)\s*{([^}]*)}', content, re.DOTALL)
            if match:
                fixed_content += match.group(1).strip() + "\n"
            
            fixed_content += "        }\n    }\n}"
            return fixed_content

        # Check if all braces are closed
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces > close_braces:
            self.logger.info(f"AutoGen file has unclosed braces. Adding missing closing braces.")
            content += "}" * (open_braces - close_braces)

        return content

    def _read_designer_file(self, designer_file_path):
        with open(designer_file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _extract_initialize_layout(self, designer_content):
        match = re.search(r'private void InitializeLayoutOptions\(\)\s*{([^}]*)}', designer_content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

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
            return content
        except Exception as e:
            self.logger.error(f"Error creating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            raise

    def _apply_changes(self, content, changes, initialize_layout_content):
        lines = content.split('\n')
        insert_index = self._find_insert_index(lines)

        # Remove existing auto-generated code
        end_index = self._find_end_index(lines, insert_index)
        existing_content = '\n'.join(lines[insert_index:end_index])

        new_lines = []

        # Insert initialize_layout_content
        for line in initialize_layout_content.split('\n'):
            if line.strip():
                new_lines.append(f"            {line.strip()}")

        # Apply changes
        for layout, components in changes.items():
            for component, value in components.items():
                new_line = f"            {layout}[{component}] = new ControlLayoutOptions(new Point({value}));"
                if new_line not in existing_content and new_line not in new_lines:
                    new_lines.append(new_line)
                    self.logger.debug(f"Adding line: {new_line}")

        # Merge new lines with existing content
        merged_lines = []
        for line in new_lines + existing_content.split('\n'):
            if line.strip() and line not in merged_lines:
                merged_lines.append(line)

        lines[insert_index:end_index] = merged_lines

        return '\n'.join(lines)

    def _find_insert_index(self, lines):
        for i, line in enumerate(lines):
            if "InitializeLayoutOptions()" in line:
                return i + 2  # Insert after the opening brace
        return len(lines) - 2  # If method not found, insert at the end of the class

    def _find_end_index(self, lines, start_index):
        brace_count = 1
        for i, line in enumerate(lines[start_index:], start=start_index):
            if '{' in line:
                brace_count += 1
            if '}' in line:
                brace_count -= 1
                if brace_count == 0:
                    return i
        return len(lines) - 1  # If closing brace not found, return the last line