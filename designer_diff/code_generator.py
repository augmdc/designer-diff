import os
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def get_layout_identifier(method_name: str) -> str:
    if '_' in method_name:
        suffix = method_name.split('_')[-1]
        match = re.match(r'([A-Z])Shaped', suffix)
        if match:
            return match.group(1)
    return 'S'

def get_layout_names(initialize_methods):
    layout_names = list(set(get_layout_identifier(method) for method in initialize_methods))
    if 'S' not in layout_names:
        layout_names.insert(0, 'S')
    return layout_names

def extract_control_types(designer_content: str) -> Dict[str, str]:
    control_types = {}
    pattern = r'(private|protected|public|internal|protected internal) ((?:\w+\.)*\w+) (\w+);'
    matches = re.findall(pattern, designer_content)
    for _, type_name, control_name in matches:
        control_types[control_name] = type_name
    return control_types
    
def extract_namespace(designer_content):
    namespace_match = re.search(r'namespace\s+([\w.]+)', designer_content)
    if namespace_match:
        return namespace_match.group(1)
    else:
        logger.error("Namespace not found in Designer file")
        return None

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root):
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')

    with open(designer_file_path, 'r', encoding='utf-8') as file:
        designer_content = file.read()

    namespace = extract_namespace(designer_content)
    if namespace is None:
        return None

    layout_names = get_layout_names(initialize_methods)
    control_properties = extract_control_properties(initialize_methods)
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

{generate_layout_options(control_properties, layout_names, control_types)}

            OnInitializeLayoutOptionsCompleted();
        }}
        #endregion
    }}
}}
"""
    return content

def generate_layout_dictionaries(layout_names):
    lines = []
    for layout in layout_names:
        lines.append(f'            var layout{layout} = new Dictionary<Control, ControlLayoutOptions>();')
    
    lines.append('')
    for layout in layout_names:
        layout_enum = 'Standard' if layout == 'S' else f'{layout}ShapedTelemetry'
        lines.append(f'            _layoutControlSettings.Add(UILayout.{layout_enum}, layout{layout});')
    
    return '\n'.join(lines)

def generate_layout_options(control_properties: Dict[str, Dict[str, Dict[str, str]]], layout_names: List[str], control_types: Dict[str, str]) -> str:
    options = []
    layout_names = sorted(layout_names, key=lambda x: (x != 'S', x))

    for control in sorted(control_properties.keys()):
        control_type = control_types.get(control, "System.Windows.Forms.Control")
        
        changed_properties = {}
        for prop, values in control_properties[control].items():
            if prop not in ['TabIndex', 'Name'] and len(set(values.values())) > 1:
                changed_properties[prop] = values

        for layout in layout_names:
            layout_options = []
            for prop, values in changed_properties.items():
                if layout in values:
                    layout_options.append(generate_property_option(prop, values[layout]))
            
            if layout_options:
                options.append(f"            layout{layout}[{control}] = new ControlLayoutOptions(c => {{ var t = c as {control_type}; {' '.join(layout_options)} }});")
        
        if changed_properties:
            options.append('')

    return '\n'.join(options)

def extract_control_properties(initialize_methods):
    control_properties = {}
    for method_name, method_content in initialize_methods.items():
        layout = get_layout_identifier(method_name)
        lines = extract_relevant_lines(method_content)
        for control, prop, value in lines:
            if control not in control_properties:
                control_properties[control] = {}
            if prop not in control_properties[control]:
                control_properties[control][prop] = {}
            control_properties[control][prop][layout] = value
    return control_properties

def generate_property_option(property_name: str, value: str) -> str:
    formatted_value = format_property_value(property_name, value)
    return f"t.{property_name} = {formatted_value};"

def format_property_value(property_name: str, value: str) -> str:
    type_pattern = r'((?:[a-zA-Z_]\w*\.)*[a-zA-Z_]\w*)'
    new_pattern = rf'^new\s+{type_pattern}\s*'
    new_match = re.match(new_pattern, value)
    
    if new_match:
        type_name = new_match.group(1)
        remaining = value[new_match.end():].strip()
        
        if remaining.startswith(type_name):
            remaining = remaining[len(type_name):].strip()
        
        return f'new {type_name}{remaining}'
    else:
        type_match = re.match(type_pattern, value)
        if type_match:
            type_name = type_match.group(1)
            remaining = value[type_match.end():].strip()
            
            if remaining.startswith(type_name):
                remaining = remaining[len(type_name):].strip()
            
            return f'{type_name}{remaining}'
    
    return value

def extract_relevant_lines(method):
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
    
    return relevant_lines