import os
import logging
import re
import difflib

class CodeUpdater:
    def __init__(self, diff_handler, teleai_root):
        self.diff_handler = diff_handler
        self.teleai_root = teleai_root
        self.logger = logging.getLogger(__name__)

    def update_autogen_file(self, designer_file_path, changes, init_mode=False):
        try:
            self.logger.info(f"Starting update process for {designer_file_path}")
            self.logger.info(f"Changes: {changes}, Init mode: {init_mode}")
            autogen_file_path = self._get_autogen_path(designer_file_path)
            self.logger.info(f"AutoGen file path: {autogen_file_path}")
            
            designer_content = self._read_designer_file(designer_file_path)
            self.logger.debug(f"Designer file content length: {len(designer_content)} characters")
            
            initialize_component_content = self._extract_initialize_component(designer_content)
            self.logger.info(f"Extracted InitializeComponent content length: {len(initialize_component_content)} characters")
            
            if not os.path.exists(autogen_file_path) or init_mode:
                action = 'Creating' if not os.path.exists(autogen_file_path) else 'Reinitializing'
                self.logger.info(f"{action} AutoGen file: {autogen_file_path}")
                content = self._create_autogen_file(designer_file_path, autogen_file_path, initialize_component_content)
            else:
                self.logger.info(f"AutoGen file already exists: {autogen_file_path}")
                with open(autogen_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.logger.debug(f"Existing AutoGen file content length: {len(content)} characters")

                if changes:
                    self.logger.info("Applying changes to existing AutoGen file")
                    new_content = self._apply_changes(content, changes)
                    self._log_content_diff(content, new_content)
                    content = new_content
                else:
                    self.logger.info("No changes to apply")

            self.logger.info(f"Writing final content to AutoGen file: {autogen_file_path}")
            self.logger.debug(f"Final content length: {len(content)} characters")

            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.logger.info(f"Successfully updated AutoGen file: {autogen_file_path}")

            return True, content
        except Exception as e:
            self.logger.error(f"Error updating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            return False, None

    def _create_autogen_file(self, designer_file_path, autogen_file_path, initialize_component_content):
        try:
            self.logger.info(f"Creating new AutoGen file: {autogen_file_path}")
            content = self._generate_autogen_content(designer_file_path, initialize_component_content)
            
            self.logger.debug(f"Generated AutoGen file content length: {len(content)} characters")
            
            os.makedirs(os.path.dirname(autogen_file_path), exist_ok=True)
            self.logger.info(f"Ensured directory exists: {os.path.dirname(autogen_file_path)}")
            
            with open(autogen_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.logger.info(f"Successfully created AutoGen file: {autogen_file_path}")
            return content
        except Exception as e:
            self.logger.error(f"Error creating AutoGen file {autogen_file_path}: {str(e)}")
            self.logger.exception("Detailed error information:")
            raise

    def _generate_autogen_content(self, designer_file_path, initialize_component_content):
        self.logger.info(f"Generating AutoGen content for {designer_file_path}")
        class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
        relative_path = os.path.relpath(os.path.dirname(designer_file_path), self.teleai_root)
        namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))

        self.logger.debug(f"Class name: {class_name}")
        self.logger.debug(f"Relative path: {relative_path}")
        self.logger.debug(f"Namespace: {namespace}")

        content = f"""using System;
using System.Windows.Forms;
using System.Drawing;

namespace {namespace}
{{
    public partial class {class_name}
    {{
        private void InitializeComponent()
        {{
{initialize_component_content}
        }}
    }}
}}
"""
        self.logger.debug(f"Generated AutoGen content length: {len(content)} characters")
        return content

    def _read_designer_file(self, designer_file_path):
        self.logger.info(f"Reading Designer file: {designer_file_path}")
        try:
            with open(designer_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.logger.debug(f"Designer file content length: {len(content)} characters")
            return content
        except Exception as e:
            self.logger.error(f"Error reading Designer file {designer_file_path}: {str(e)}")
            raise

    def _extract_initialize_component(self, content):
        self.logger.info("Extracting InitializeComponent content")
        
        self.logger.debug(f"Searched Designer file content (length: {len(content)} characters)")
        
        # Find the InitializeComponent method
        method_match = re.search(r'private void InitializeComponent\(\)\s*{(.*?)}', content, re.DOTALL)
        
        if method_match:
            extracted_content = method_match.group(1).strip()
            formatted_content = '\n'.join(f"            {line.strip()}" for line in extracted_content.split('\n') if line.strip())
            self.logger.debug(f"Extracted and formatted InitializeComponent content length: {len(formatted_content)} characters")
            return formatted_content
        else:
            self.logger.warning("InitializeComponent method not found in the Designer file")
        
        return ""

    def _get_autogen_path(self, designer_file_path):
        self.logger.info(f"Getting AutoGen path for {designer_file_path}")
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path)
        autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
        autogen_path = os.path.join(directory, autogen_filename)
        self.logger.info(f"AutoGen path: {autogen_path}")
        return autogen_path

    def _apply_changes(self, content, changes):
        self.logger.info("Applying changes to AutoGen content")
        lines = content.split('\n')
        
        # Find the start and end of the InitializeComponent method
        start_index = next((i for i, line in enumerate(lines) if "private void InitializeComponent()" in line), -1)
        if start_index == -1:
            self.logger.error("InitializeComponent() method not found in AutoGen file")
            return content

        end_index = next((i for i, line in enumerate(lines[start_index:], start=start_index) if line.strip() == '}'), -1)
        if end_index == -1:
            self.logger.error("Closing brace for InitializeComponent() not found in AutoGen file")
            return content

        self.logger.debug(f"InitializeComponent found from line {start_index} to {end_index}")

        # Extract the method content
        method_lines = lines[start_index+1:end_index]
        
        for control, properties in changes.items():
            control_pattern = rf'this\.{control}\s*='
            control_index = next((i for i, line in enumerate(method_lines) if re.search(control_pattern, line)), -1)
            
            if control_index != -1:
                # Found the control, now update its properties
                insert_index = control_index + 1
                for prop, value in properties.items():
                    prop_pattern = rf'this\.{control}\.{prop}\s*='
                    prop_index = next((i for i, line in enumerate(method_lines[control_index:], start=control_index) if re.search(prop_pattern, line)), -1)
                    
                    if prop_index != -1:
                        # Property exists, update it
                        method_lines[prop_index] = f"            this.{control}.{prop} = {value};"
                        self.logger.debug(f"Updated property: {control}.{prop} = {value}")
                    else:
                        # Property doesn't exist, add it
                        method_lines.insert(insert_index, f"            this.{control}.{prop} = {value};")
                        insert_index += 1
                        self.logger.debug(f"Added new property: {control}.{prop} = {value}")
            else:
                self.logger.warning(f"Control '{control}' not found in InitializeComponent method")

        # Reconstruct the content with updated method
        updated_content = '\n'.join(lines[:start_index+1] + method_lines + lines[end_index:])
        
        return updated_content

    def _log_content_diff(self, old_content, new_content):
        self.logger.info("Logging content differences")
        diff = list(difflib.unified_diff(old_content.splitlines(), new_content.splitlines(), lineterm=''))
        if diff:
            self.logger.debug("Content changes:")
            for line in diff:
                self.logger.debug(line)
        else:
            self.logger.debug("No changes in content")