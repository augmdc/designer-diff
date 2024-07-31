import re
from itertools import combinations

def extract_initialize_methods(content):
    methods = re.findall(r'private void InitializeComponent.*?\(\)\s*{.*?}', content, re.DOTALL)
    return {f"InitializeComponent_{i}" if i > 0 else "InitializeComponent": method 
            for i, method in enumerate(methods)}

def find_differences(methods):
    differences = {}
    method_names = sorted(methods.keys())
    
    for method1, method2 in combinations(method_names, 2):
        diff = compare_methods(methods[method1], methods[method2])
        if diff:
            differences[f"{method1}_{method2}"] = diff
    
    return differences

def compare_methods(method1, method2):
    lines1 = extract_relevant_lines(method1)
    lines2 = extract_relevant_lines(method2)
    diff = []
    
    for line1 in lines1:
        for line2 in lines2:
            control_match1 = re.search(r'this\.(\w+)\.', line1)
            control_match2 = re.search(r'this\.(\w+)\.', line2)
            
            if control_match1 and control_match2 and control_match1.group(1) == control_match2.group(1):
                if line1 != line2:
                    diff.append((control_match1.group(1), line1, line2))
                break
    
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