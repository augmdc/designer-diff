import os
import re
from typing import Dict, List, Tuple

def get_layout_identifier(method_name: str) -> str:
    if '_' in method_name:
        suffix = method_name.split('_')[-1]
        match = re.match(r'([A-Z])Shaped', suffix)
        if match:
            return match.group(1)
    return 'S'  # Default to 'S' if no other identifier is found

def get_layout_names(initialize_methods):
    layout_names = ['S']  # Always include 'S' for standard layout first
    for method_name in initialize_methods:
        layout = get_layout_identifier(method_name)
        if layout != 'S' and layout not in layout_names:
            layout_names.append(layout)
    return layout_names  # No need to sort, we want to keep this order

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root):
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
    relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
    namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep)).replace("client.TeleAiClient.", "")

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
    return content

def generate_layout_dictionaries(layout_names):
    lines = []
    for layout in layout_names:
        lines.append(f'            var Layout{layout} = new Dictionary<Control, ControlLayoutOptions>();')
    
    lines.append('')
    for layout in layout_names:
        layout_enum = 'Standard' if layout == 'S' else f'{layout}ShapedTelemetry'
        lines.append(f'            _layoutControlSettings.Add(UILayout.{layout_enum}, Layout{layout});')
    
    return '\n'.join(lines)

def generate_layout_options(differences: Dict[str, List[Tuple[str, str, str]]], layout_names: List[str]) -> str:
    options = []
    control_differences: Dict[str, Dict[str, Dict[str, str]]] = {}

    for method_pair, diff in differences.items():
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

    for control in sorted(control_differences.keys()):
        control_options = []
        for layout in layout_names:
            layout_options = []
            for property_name, values in control_differences[control].items():
                if layout in values and property_name not in ['TabIndex', 'Name']:
                    layout_options.append(generate_property_option(control, property_name, values[layout]))
            
            if layout_options:
                control_options.append(f"            Layout{layout}[{control}] = new ControlLayoutOptions(c =>\n            {{\n                {'; '.join(layout_options)}\n            }});")
        
        if control_options:
            options.extend(control_options)
            options.append('')  # Add a blank line for readability

    return '\n'.join(options)

def generate_property_option(control: str, property_name: str, value: str) -> str:
    special_properties = {
        'Location': lambda v: f"c.Location = {v}",
        'Size': lambda v: f"c.Size = {v}",
        'Visible': lambda v: f"c.Visible = {v.lower()}",
        'TextAlign': lambda v: f"((Button)c).{property_name} = {v}",
        'AudioAlerts': lambda v: f"((klVehicleTilt)c).AudioAlerts = {v}",
    }

    if property_name in special_properties:
        return special_properties[property_name](value)
    elif property_name.startswith('Middle') or property_name.startswith('Selected'):
        return f"((AutoButton)c).{property_name} = {value}"
    else:
        return f"c.{property_name} = {value}"

def find_differences(methods):
    differences = {}
    method_names = sorted(methods.keys())
    
    if len(method_names) < 2:
        return differences

    # Compare each pair of methods
    for i in range(len(method_names)):
        for j in range(i + 1, len(method_names)):
            method1, method2 = method_names[i], method_names[j]
            diff = compare_methods(methods[method1], methods[method2])
            if diff:
                differences[f"{method1}_{method2}"] = diff
    
    return differences

def compare_methods(method1, method2):
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
    
    return diff

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