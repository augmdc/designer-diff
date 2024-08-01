import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def extract_initialize_methods(content: str) -> Dict[str, str]:
    methods = re.findall(r'private void InitializeComponent(?:_\w+)?\s*\(\)\s*{.*?}', content, re.DOTALL)
    extracted_methods = {}
    for method in methods:
        method_name = re.search(r'InitializeComponent(?:_\w+)?', method).group()
        extracted_methods[method_name] = method
    return extracted_methods

def find_differences(methods: Dict[str, str]) -> Dict[str, List[Tuple[str, str, str]]]:
    differences = {}
    method_names = sorted(methods.keys())
    
    if len(method_names) < 2:
        return differences

    for i in range(len(method_names)):
        for j in range(i + 1, len(method_names)):
            method1, method2 = method_names[i], method_names[j]
            diff = compare_methods(methods[method1], methods[method2])
            if diff:
                differences[f"{method1}_{method2}"] = diff
    
    return differences

def compare_methods(method1, method2):
    lines1 = sorted(extract_relevant_lines(method1))
    lines2 = sorted(extract_relevant_lines(method2))
    diff = []
    
    controls1 = {line[0] for line in lines1}
    controls2 = {line[0] for line in lines2}
    all_controls = sorted(controls1.union(controls2))
    
    for control in all_controls:
        lines1_control = [line for line in lines1 if line[0] == control]
        lines2_control = [line for line in lines2 if line[0] == control]
        
        max_length = max(len(lines1_control), len(lines2_control))
        for i in range(max_length):
            line1 = lines1_control[i] if i < len(lines1_control) else None
            line2 = lines2_control[i] if i < len(lines2_control) else None
            
            if line1 != line2:
                diff.append((control, line1, line2))
    
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