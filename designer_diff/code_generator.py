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
    layout_names = list(set(get_layout_identifier(method) for method in initialize_methods))
    if 'S' not in layout_names:
        layout_names.insert(0, 'S')  # Ensure 'S' is always first
    logger.debug(f"Layout names: {layout_names}")
    return layout_names

def extract_control_types(designer_content: str) -> Dict[str, str]:
    logger.info("Extracting control types from Designer file")
    control_types = {}
    pattern = r'(private|protected|public|internal|protected internal) ((?:\w+\.)*\w+) (\w+);'
    matches = re.findall(pattern, designer_content)
    for _, type_name, control_name in matches:
        control_types[control_name] = type_name
    logger.debug(f"Extracted types for {len(control_types)} controls")
    return control_types

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root, excluded_properties):
    logger.info(f"Generating AutoGen content for {designer_file_path}")
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
    relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
    namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep)).replace("client.TeleAiClient.", "")

    logger.debug(f"Class name: {class_name}")
    logger.debug(f"Namespace: {namespace}")

    layout_names = get_layout_names(initialize_methods)
    control_properties = extract_control_properties(initialize_methods, excluded_properties)
    this_size_properties = extract_this_size_properties(initialize_methods)

    # Read the Designer file content
    with open(designer_file_path, 'r') as file:
        designer_content = file.read()

    # Extract control types
    control_types = extract_control_types(designer_content)

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

{generate_this_size_options(this_size_properties, layout_names)}
{generate_layout_options(control_properties, layout_names, control_types)}
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
        layout_enum = 'Standard' if layout == 'S' else f'{layout}ShapedTelemetry'
        lines.append(f'            _layoutControlSettings.Add(UILayout.{layout_enum}, layout{layout});')
    
    logger.debug(f"Generated layout dictionaries:\n{lines}")
    return '\n'.join(lines)

def generate_this_size_options(this_size_properties, layout_names):
    logger.info("Generating 'this.Size' options")
    lines = []
    for layout in layout_names:
        if layout in this_size_properties:
            size = this_size_properties[layout]
            lines.append(f'            layout{layout}[this] = new ControlLayoutOptions(new Size({size[0]}, {size[1]}));')
    
    logger.debug(f"Generated 'this.Size' options:\n{lines}")
    return '\n'.join(lines) + '\n'

def generate_layout_options(control_properties: Dict[str, Dict[str, Dict[str, str]]], layout_names: List[str], control_types: Dict[str, str]) -> str:
    logger.info("Generating layout options")
    options = []

    # Ensure 'S' layout comes first
    layout_names = sorted(layout_names, key=lambda x: (x != 'S', x))

    for control in sorted(control_properties.keys()):
        logger.debug(f"Generating options for control: {control}")
        control_type = control_types.get(control, "System.Windows.Forms.Control")
        
        # Determine which properties have changed across layouts
        changed_properties = {}
        for prop, values in control_properties[control].items():
            if len(set(values.values())) > 1:
                changed_properties[prop] = values

        for layout in layout_names:
            layout_options = []
            for prop, values in changed_properties.items():
                if layout in values:
                    layout_options.append(generate_property_option(prop, values[layout]))
            
            if layout_options:
                options.append(f"            layout{layout}[{control}] = new ControlLayoutOptions(c => {{ var t = c as {control_type}; {' '.join(layout_options)} }});")
        
        if changed_properties:
            options.append('')  # Add a blank line for readability

    logger.info(f"Generated layout options for {len(control_properties)} controls")
    return '\n'.join(options)

def extract_control_properties(initialize_methods, excluded_properties):
    logger.info("Extracting control properties from InitializeComponent methods")
    control_properties = {}
    for method_name, method_content in initialize_methods.items():
        layout = get_layout_identifier(method_name)
        lines = extract_relevant_lines(method_content, excluded_properties)
        for control, prop, value in lines:
            if control != 'this':  # Exclude 'this' as it's handled separately
                if control not in control_properties:
                    control_properties[control] = {}
                if prop not in control_properties[control]:
                    control_properties[control][prop] = {}
                control_properties[control][prop][layout] = value
    logger.debug(f"Extracted properties for {len(control_properties)} controls")
    return control_properties

def extract_this_size_properties(initialize_methods):
    logger.info("Extracting 'this.Size' properties")
    this_size_properties = {}
    for method_name, method_content in initialize_methods.items():
        layout = get_layout_identifier(method_name)
        lines = method_content.split('\n')
        for line in lines:
            match = re.search(r'this\.Size\s*=\s*new\s+System\.Drawing\.Size\((\d+),\s*(\d+)\)', line)
            if match:
                width, height = match.groups()
                this_size_properties[layout] = (width, height)
                logger.debug(f"Found 'this.Size' for layout {layout}: ({width}, {height})")
    return this_size_properties

def generate_property_option(property_name: str, value: str) -> str:
    logger.debug(f"Generating property option: Property={property_name}, Value={value}")
    formatted_value = format_property_value(property_name, value)
    return f"t.{property_name} = {formatted_value};"

def format_property_value(property_name: str, value: str) -> str:
    logger.debug(f"Formatting property value: Property={property_name}, Value={value}")
    
    # Pattern to match fully qualified type names
    type_pattern = r'((?:[a-zA-Z_]\w*\.)*[a-zA-Z_]\w*)'
    
    # Check if the value starts with 'new' followed by a type name
    new_pattern = rf'^new\s+{type_pattern}\s*'
    new_match = re.match(new_pattern, value)
    
    if new_match:
        # If it starts with 'new', keep the 'new' and the type name
        type_name = new_match.group(1)
        remaining = value[new_match.end():].strip()
        
        # Check if the remaining part starts with the same type name
        if remaining.startswith(type_name):
            remaining = remaining[len(type_name):].strip()
        
        return f'new {type_name}{remaining}'
    else:
        # If it doesn't start with 'new', check for a type name at the start
        type_match = re.match(type_pattern, value)
        if type_match:
            type_name = type_match.group(1)
            remaining = value[type_match.end():].strip()
            
            # Check if the remaining part starts with the same type name
            if remaining.startswith(type_name):
                remaining = remaining[len(type_name):].strip()
            
            return f'{type_name}{remaining}'
    
    # If no duplication found, return the original value
    return value

def extract_relevant_lines(method, excluded_properties):
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
            if property not in excluded_properties:
                relevant_lines.append((control, property, value))
                logger.debug(f"Relevant line found: Control={control}, Property={property}, Value={value}")
    
    logger.debug(f"Total relevant lines extracted: {len(relevant_lines)}")
    return relevant_lines