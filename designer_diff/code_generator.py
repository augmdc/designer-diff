import os
import re
import logging
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_layout_identifier(method_name: str) -> str:
    logger.debug(f"Getting layout identifier for method: {method_name}")
    if '_' in method_name:
        suffix = method_name.split('_')[-1]
        match = re.match(r'([A-Z])Shaped', suffix)
        if match:
            layout = match.group(1)
            logger.debug(f"Layout identifier found: {layout}")
            return layout
    logger.debug("No specific layout identifier found, defaulting to 'S'")
    return 'S'  # Default to 'S' if no other identifier is found

def get_layout_names(initialize_methods):
    logger.info("Getting layout names")
    layout_names = ['S', 'L']  # Always include both 'S' and 'L'
    logger.debug(f"Layout names: {layout_names}")
    return layout_names

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root):
    logger.info(f"Generating AutoGen content for {designer_file_path}")
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
    relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
    namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep)).replace("client.TeleAiClient.", "")

    logger.debug(f"Class name: {class_name}")
    logger.debug(f"Namespace: {namespace}")

    differences = find_differences(initialize_methods)
    layout_names = get_layout_names(initialize_methods)

    content = f"""using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using ClientUI;

namespace {namespace}
{{
    public partial class {class_name} : BaseDash
    {{
        #region Dash Layouts
        protected override void InitializeLayoutOptions()
        {{
{generate_layout_dictionaries(layout_names)}

{generate_layout_options(differences, layout_names)}
        }}
        #endregion
    }}
}}
"""
    logger.info("AutoGen content generated successfully")
    return content

def generate_layout_dictionaries(layout_names):
    logger.info("Generating layout dictionaries")
    lines = []
    for layout in layout_names:
        lines.append(f'            var layout{layout} = new Dictionary<Control, ControlLayoutOptions>();')
    
    lines.append('')
    for layout in layout_names:
        layout_enum = 'Standard' if layout == 'S' else 'LShapedTelemetry'
        lines.append(f'            _layoutControlSettings.Add(UILayout.{layout_enum}, layout{layout});')
    
    logger.debug(f"Generated layout dictionaries:\n{lines}")
    return '\n'.join(lines)

def generate_layout_options(differences: Dict[str, List[Tuple[str, str, str]]], layout_names: List[str]) -> str:
    logger.info("Generating layout options")
    options = []
    control_differences: Dict[str, Dict[str, Dict[str, str]]] = {}

    for method_pair, diff in differences.items():
        logger.debug(f"Processing differences for method pair: {method_pair}")
        method_names = method_pair.split('_')
        layout1 = get_layout_identifier(method_names[0])
        layout2 = get_layout_identifier(method_names[1])
        
        for control, property_name, value in diff:
            if control not in control_differences:
                control_differences[control] = {}
            if property_name not in control_differences[control]:
                control_differences[control][property_name] = {}
            control_differences[control][property_name][layout1] = value
            control_differences[control][property_name][layout2] = value
            logger.debug(f"Difference found: Control={control}, Property={property_name}, Value={value}, Layouts={layout1},{layout2}")

    for control in sorted(control_differences.keys()):
        logger.debug(f"Generating options for control: {control}")
        control_type = get_control_type(control)
        control_options = []
        for layout in layout_names:
            layout_options = []
            for property_name, values in control_differences[control].items():
                if property_name not in ['TabIndex', 'Name']:
                    if layout in values:
                        layout_options.append(generate_property_option(control, control_type, property_name, values[layout]))
            if layout_options:
                control_options.append(f"            layout{layout}[{control}] = new ControlLayoutOptions(c =>\n            {{\n                {'; '.join(layout_options)}\n            }});")
        
        if control_options:
            options.extend(control_options)
            options.append('')  # Add a blank line for readability

    logger.info(f"Generated layout options for {len(control_differences)} controls")
    return '\n'.join(options)

def get_control_type(control: str) -> str:
    logger.debug(f"Getting control type for: {control}")
    control_types = {
        'autoButton': 'ClientUI.AutoButton',
        'klVehicleTilt': 'ClientUI.klVehicleTilt',
        'box': 'ClientUI.Box',
        'label': 'System.Windows.Forms.Label',
        'panel': 'System.Windows.Forms.Panel',
        'picturebox': 'System.Windows.Forms.PictureBox',
        'textBox': 'System.Windows.Forms.TextBox',
    }
    
    for prefix, control_type in control_types.items():
        if control.lower().startswith(prefix):
            logger.debug(f"Control type found: {control_type}")
            return control_type
    
    logger.debug("No specific control type found, defaulting to System.Windows.Forms.Control")
    return 'System.Windows.Forms.Control'

def generate_property_option(control: str, control_type: str, property_name: str, value: str) -> str:
    logger.debug(f"Generating property option: Control={control}, Type={control_type}, Property={property_name}, Value={value}")
    formatted_value = format_property_value(property_name, value)
    return f"var t = c as {control_type}; t.{property_name} = {formatted_value}"

def format_property_value(property_name: str, value: str) -> str:
    logger.debug(f"Formatting property value: Property={property_name}, Value={value}")
    if property_name == 'Location':
        return f'new System.Drawing.Point{value}'
    elif property_name == 'Size':
        return f'new System.Drawing.Size{value}'
    elif property_name == 'Visible':
        return value.lower()
    elif property_name == 'TextAlign':
        return f'System.Drawing.ContentAlignment.{value}'
    elif property_name.startswith('Middle') or property_name.startswith('Selected'):
        return f'((System.Drawing.Image)(resources.GetObject("{value}")))'
    else:
        return value

def find_differences(methods):
    logger.info("Finding differences between methods")
    differences = {}
    method_names = sorted(methods.keys())
    
    if len(method_names) < 2:
        logger.warning("Less than 2 methods found, no differences to compare")
        return differences

    # Compare each pair of methods
    for i in range(len(method_names)):
        for j in range(i + 1, len(method_names)):
            method1, method2 = method_names[i], method_names[j]
            logger.debug(f"Comparing methods: {method1} and {method2}")
            diff = compare_methods(methods[method1], methods[method2])
            if diff:
                differences[f"{method1}_{method2}"] = diff
                logger.debug(f"Found {len(diff)} differences between {method1} and {method2}")
    
    logger.info(f"Total differences found: {sum(len(diff) for diff in differences.values())}")
    return differences

def compare_methods(method1, method2):
    logger.debug("Comparing two methods")
    lines1 = extract_relevant_lines(method1)
    lines2 = extract_relevant_lines(method2)
    diff = []
    
    controls1 = {line[0] for line in lines1}
    controls2 = {line[0] for line in lines2}
    all_controls = sorted(controls1.union(controls2))
    
    for control in all_controls:
        properties1 = {line[1]: line[2] for line in lines1 if line[0] == control}
        properties2 = {line[1]: line[2] for line in lines2 if line[0] == control}
        all_properties = set(properties1.keys()).union(set(properties2.keys()))
        
        for prop in all_properties:
            value1 = properties1.get(prop)
            value2 = properties2.get(prop)
            
            if value1 != value2:
                diff.append((control, prop, value1 or value2))
                logger.debug(f"Difference found: Control={control}, Property={prop}, Value={value1 or value2}")
    
    logger.debug(f"Total differences found in method comparison: {len(diff)}")
    return diff

def extract_relevant_lines(method):
    logger.debug("Extracting relevant lines from method")
    lines = method.split('\n')
    relevant_lines = []
    
    pattern = r'^\s*this\.(?P<control>\w+)\.(?P<property>\w+)\s*=\s*(?P<value>.*);$'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            control = match.group('control')
            property = match.group('property')
            value = match.group('value').strip()
            relevant_lines.append((control, property, value))
            logger.debug(f"Relevant line found: Control={control}, Property={property}, Value={value}")
    
    logger.debug(f"Total relevant lines extracted: {len(relevant_lines)}")
    return relevant_lines