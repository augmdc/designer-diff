import re

class DiffHandler:
    def __init__(self):
        self.relevant_properties = ['Location', 'Size']

    def process_diff(self, diff_text):
        changes = {}
        lines = diff_text.split('\n')
        current_component = None

        for line in lines:
            if line.startswith('+'):
                component_match = re.match(r'\+\s*this\.(\w+)\.', line)
                if component_match:
                    current_component = component_match.group(1)
                    if current_component not in changes:
                        changes[current_component] = {}

                for prop in self.relevant_properties:
                    prop_match = re.match(rf'\+\s*this\.{current_component}\.{prop} = (.+);', line)
                    if prop_match:
                        value = prop_match.group(1)
                        changes[current_component][prop] = value

        return changes