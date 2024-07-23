import re
from designer_diff.git_operations import get_file_diff
from designer_diff.logging_config import logger

class DiffHandler:
    def __init__(self, relevant_properties=None, ignored_properties=None):
        self.relevant_properties = relevant_properties or ['Location', 'Size']
        self.ignored_properties = ignored_properties or ['TabIndex']

    def process_diff(self, file_path, old_commit, new_commit):
        """
        Process the diff between two commits for a specific file.

        :param file_path: Path to the file
        :param old_commit: The older commit
        :param new_commit: The newer commit
        :return: A dictionary of relevant changes
        """
        try:
            diff_text = get_file_diff(file_path, old_commit, new_commit)
            if not diff_text:
                logger.info(f"No diff found for {file_path} between {old_commit} and {new_commit}")
                return None

            return self.analyze_diff(diff_text)
        except Exception as e:
            logger.error(f"Error processing diff for {file_path}: {str(e)}")
            return None

    def analyze_diff(self, diff_text):
        """
        Analyze the diff text and extract relevant changes.

        :param diff_text: The diff text to analyze
        :return: A dictionary of relevant changes
        """
        changes = {}
        lines = diff_text.split('\n')
        current_component = None

        try:
            for line in lines:
                if line.startswith('+++') or line.startswith('---'):
                    continue  # Skip diff headers

                if line.startswith('-') or line.startswith('+'):
                    component_match = re.match(r'[+-]\s*this\.(\w+)\.', line)
                    if component_match:
                        current_component = component_match.group(1)
                        if current_component not in changes:
                            changes[current_component] = {}

                    for prop in self.relevant_properties:
                        prop_match = re.match(rf'[+-]\s*this\.{current_component}\.{prop} = (.+);', line)
                        if prop_match:
                            value = prop_match.group(1)
                            changes[current_component][prop] = value

            return self.filter_changes(changes)
        except Exception as e:
            logger.error(f"Error analyzing diff: {str(e)}")
            return {}

    def filter_changes(self, changes):
        """
        Filter out ignored properties from the changes.

        :param changes: Dictionary of changes
        :return: Filtered dictionary of changes
        """
        filtered_changes = {}
        for component, props in changes.items():
            filtered_props = {k: v for k, v in props.items() if k not in self.ignored_properties}
            if filtered_props:
                filtered_changes[component] = filtered_props
        return filtered_changes