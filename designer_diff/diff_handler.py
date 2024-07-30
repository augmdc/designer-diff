import re

class DiffHandler:
    def __init__(self):
        self.relevant_properties = ['Location', 'Size']

    def process_diff(self, diff_text):
        changes = {'layouts': {}, 'layoutL': {}}
        lines = diff_text.split('\n')
        current_layout = None

        for line in lines:
            if line.startswith('+'):
                layout_match = re.match(r'\+\s*(layouts|layoutL)\[', line)
                if layout_match:
                    current_layout = layout_match.group(1)
                    continue

                if current_layout:
                    component_match = re.match(r'\+\s*(layouts|layoutL)\[(\w+)\]\s*=\s*new\s*ControlLayoutOptions\((.*?)\);', line)
                    if component_match:
                        layout, component, value = component_match.groups()
                        # Extract only the Point part
                        point_match = re.search(r'new\s*Point\((.*?)\)', value)
                        if point_match:
                            point_value = point_match.group(1)
                            changes[layout][component] = point_value

        return changes