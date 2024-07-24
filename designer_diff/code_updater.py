import re
import os

class CodeUpdater:
    def __init__(self, diff_handler):
        self.diff_handler = diff_handler

    def update_autogen_file(self, designer_file_path, changes):
        autogen_file_path = self._get_autogen_path(designer_file_path)
        if not os.path.exists(autogen_file_path):
            print(f"AutoGen file not found: {autogen_file_path}")
            return False

        with open(autogen_file_path, 'r') as file:
            content = file.read()

        updated_content = self._apply_changes(content, changes)

        with open(autogen_file_path, 'w') as file:
            file.write(updated_content)

        return True

    def _get_autogen_path(self, designer_file_path):
        directory = os.path.dirname(designer_file_path)
        filename = os.path.basename(designer_file_path)
        autogen_filename = filename.replace('.Designer.cs', '.AutoGen.cs')
        return os.path.join(directory, autogen_filename)

    def _apply_changes(self, content, changes):
        lines = content.split('\n')
        for component, properties in changes.items():
            for prop, value in properties.items():
                pattern = rf'(this\.{component}\.{prop}\s*=\s*).*;'
                replacement = rf'\1{value};'
                lines = [re.sub(pattern, replacement, line) for line in lines]
        return '\n'.join(lines)