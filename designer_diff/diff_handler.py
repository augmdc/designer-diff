import re
import logging

logger = logging.getLogger(__name__)

class DiffHandler:
    def __init__(self):
        self.relevant_properties = ['Location', 'Size']
        logger.info("DiffHandler initialized")

    def process_diff(self, diff_text):
        logger.info("Processing diff")
        changes = {'layouts': {}, 'layoutL': {}}
        lines = diff_text.split('\n')
        current_layout = None
        in_initialize_layout = False

        for line in lines:
            logger.debug(f"Processing line: {line}")
            if 'InitializeLayoutOptions()' in line:
                logger.debug("Entering InitializeLayoutOptions section")
                in_initialize_layout = True
                continue
            
            if not in_initialize_layout:
                continue

            if line.strip() == '}':
                logger.debug("Exiting InitializeLayoutOptions section")
                in_initialize_layout = False
                continue

            layout_match = re.match(r'[+-]?\s*(layouts|layoutL)\[', line)
            if layout_match:
                current_layout = layout_match.group(1)
                logger.debug(f"Current layout set to: {current_layout}")
                continue

            if current_layout:
                component_match = re.match(r'[+-]?\s*(layouts|layoutL)\[(\w+)\]\s*=\s*new\s*ControlLayoutOptions\((.*?)\);', line)
                if component_match:
                    layout, component, value = component_match.groups()
                    # Extract only the Point part
                    point_match = re.search(r'new\s*Point\((.*?)\)', value)
                    if point_match:
                        point_value = point_match.group(1)
                        changes[layout][component] = point_value
                        logger.debug(f"Found change: {layout}[{component}] = {point_value}")

        logger.info(f"Processed diff. Found changes: {changes}")
        return changes