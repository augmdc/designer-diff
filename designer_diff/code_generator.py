import os
import re
from code_analyzer import find_differences

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root):
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
    relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
    namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))

    differences = find_differences(initialize_methods)
    layout_names = get_layout_names(initialize_methods)

    content = f"""using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

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

def get_layout_names(initialize_methods):
    return ['S'] + [method[-1].upper() for method in initialize_methods if method != 'InitializeComponent']

def generate_layout_dictionaries(layout_names):
    lines = []
    for layout in layout_names:
        lines.append(f'            var Layout{layout} = new Dictionary<Control, ControlLayoutOptions>();')
    
    lines.append('')
    for layout in layout_names:
        layout_enum = 'Standard' if layout == 'S' else f'{layout}ShapedTelemetry'
        lines.append(f'            _layoutControlSettings.Add(UILayout.{layout_enum}, Layout{layout});')
    
    return '\n'.join(lines)

def generate_layout_options(differences, layout_names):
    options = []
    all_controls = set()
    control_differences = {}

    for method_pair, diff in differences.items():
        for control, line1, line2 in diff:
            if control not in control_differences:
                control_differences[control] = {}
            layout1, layout2 = method_pair.split('_')
            layout1_char = layout1[-1].upper() if layout1 != "InitializeComponent" else "S"
            layout2_char = layout2[-1].upper() if layout2 != "InitializeComponent" else "S"
            control_differences[control][layout1_char] = line1
            control_differences[control][layout2_char] = line2
            all_controls.add(control)

    for control in sorted(all_controls):
        for layout in layout_names:
            if layout in control_differences[control]:
                lambda_expr = generate_lambda_expression(control, control_differences[control][layout])
                options.append(f'            Layout{layout}[{control}] = new ControlLayoutOptions({lambda_expr});')
        options.append('')  # Add a blank line for readability

    return '\n'.join(options)

def generate_lambda_expression(control, line):
    pattern1 = r'^\s*this\.(\w+)\s*=\s*new\s*([^(]+)\((.*)\);$'
    pattern2 = r'^\s*this\.(\w+)\.(\w+)\s*=\s*(.*);$'
    
    match1 = re.match(pattern1, line)
    match2 = re.match(pattern2, line)
    
    if match1:
        control, value, args = match1.group(1), match1.group(2), match1.group(3)
        return f'new {value}({args})'
    elif match2:
        property, value = match2.group(2), match2.group(3)
        if property == 'Location':
            return f'new Point({value})'
        elif property == 'Size':
            return f'new Size({value})'
        elif property == 'Visible':
            return f'c => {{ c.Visible = {value.lower()}; }}'
        elif property.startswith('Middle') or property.startswith('Selected'):
            return f'c => {{ var t = c as AutoButton; t.{property} = {value}; }}'
        elif property == 'TextAlign':
            return f'c => {{ var t = c as Button; t.{property} = {value}; }}'
        else:
            return f'c => {{ var t = c as Control; t.{property} = {value}; }}'
    else:
        return f'/* Unable to parse: {line} */'