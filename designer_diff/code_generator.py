import os
import re
from code_analyzer import find_differences

def generate_autogen_content(designer_file_path, initialize_methods, teleai_root):
    class_name = os.path.basename(designer_file_path).replace('.Designer.cs', '')
    relative_path = os.path.relpath(os.path.dirname(designer_file_path), teleai_root)
    namespace = "TeleAI.Client." + ".".join(relative_path.split(os.path.sep))

    differences = find_differences(initialize_methods)
    components_list = list(set(control for diff in differences.values() for control, _, _ in diff))

    content = f"""using System;
using System.Windows.Forms;
using System.Drawing;
using System.Collections.Generic;

namespace {namespace}
{{
    public partial class {class_name} : BaseDash
    {{
        #region Dash Layouts
        protected override void InitializeLayoutOptions()
        {{
            var layoutS = new Dictionary<Control, ControlLayoutOptions>();
            var layoutL = new Dictionary<Control, ControlLayoutOptions>();
            _layoutControlSettings.Add(UILayout.Standard, layoutS);
            _layoutControlSettings.Add(UILayout.LShapedTelemetry, layoutL);

{generate_layout_options(differences)}
        }}
        #endregion
    }}
}}
"""
    return content

def generate_layout_options(differences):
    options = []
    layout_map = {
        'InitializeComponent': 'S',
        'InitializeComponent_LShaped': 'L'
    }

    for method_pair, diff in differences.items():
        layouts = method_pair.split('_')
        for i in range(len(layouts) - 1):
            for j in range(i + 1, len(layouts)):
                layout1 = layouts[i]
                layout2 = layouts[j]
                layout1_char = layout_map.get(layout1, layout1[-1])
                layout2_char = layout_map.get(layout2, layout2[-1])

                for control, line1, line2 in diff:
                    lambda1 = generate_lambda_expression(control, line1)
                    lambda2 = generate_lambda_expression(control, line2)
                    
                    options.append(f'            layout{layout1_char}[{control}] = new ControlLayoutOptions({lambda1});')
                    options.append(f'            layout{layout2_char}[{control}] = new ControlLayoutOptions({lambda2});')
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
        elif value.lower() in ['true', 'false']:
            return f'c => {{ c.Visible = {value.lower()}; }}'
        else:
            return f'c => {{ var t = c as Control; t.{property} = {value}; }}'
    else:
        return f'/* Unable to parse: {line} */'