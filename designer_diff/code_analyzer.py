import re
from itertools import combinations

def extract_initialize_methods(content):
    methods = re.findall(r'private void InitializeComponent.*?\(\)\s*{.*?}', content, re.DOTALL)
    return {f"InitializeComponent_{i}" if i > 0 else "InitializeComponent": method 
            for i, method in enumerate(methods)}

def find_differences(methods):
    differences = {}
    method_names = sorted(methods.keys())
    
    if len(method_names) < 2:
        return differences

    for method1, method2 in combinations(method_names, 2):
        diff = compare_methods(methods[method1], methods[method2])
        if diff:
            differences[f"{method1}_{method2}"] = diff
    
    return differences

def compare_methods(method1, method2):
    lines1 = extract_relevant_lines(method1)
    lines2 = extract_relevant_lines(method2)
    diff = []
    
    controls1 = {line.split('.')[0].split()[-1] for line in lines1}
    controls2 = {line.split('.')[0].split()[-1] for line in lines2}
    
    common_controls = controls1.intersection(controls2)  # Changed back to intersection
    
    for control in common_controls:
        lines1_control = [line for line in lines1 if line.startswith(f"this.{control}")]
        lines2_control = [line for line in lines2 if line.startswith(f"this.{control}")]
        
        if lines1_control != lines2_control:
            diff.append((control, lines1_control[0] if lines1_control else "", lines2_control[0] if lines2_control else ""))
    
    return diff

def extract_relevant_lines(method):
    lines = method.split('\n')
    relevant_lines = []
    
    pattern1 = r'^\s*this\.(\w+)\s*=\s*new\s*([^(]+)\(.*\);$'
    pattern2 = r'^\s*this\.(\w+)\.(\w+)\s*=\s*(.*);$'
    
    for line in lines:
        if re.match(pattern1, line) or re.match(pattern2, line):
            relevant_lines.append(line.strip())
    
    return sorted(relevant_lines)