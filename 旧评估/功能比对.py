import re
def compare_predicted_functions(file1, file2):
    with open(file1, 'r') as f:
        content1 = f.read()
    with open(file2, 'r') as f:
        content2 = f.read()

    # Extract predicted function descriptions
    func_pattern = r'Gene\s+Ghir_A02G007610\s+is\spredicted\sto\sfunction\sas\s(.*?)(?=\.|\n)'
    func1 = re.search(func_pattern, content1, re.DOTALL).group(1).strip()
    func2 = re.search(func_pattern, content2, re.DOTALL).group(1).strip()

    # Compare the two descriptions
    return func1 == func2, func1, func2

# Example usage
consistent, func1, func2 = compare_predicted_functions('1.txt', '2.txt')
print(f"Function descriptions consistent: {consistent}")
if not consistent:
    print(f"File1 Function: {func1}")
    print(f"File2 Function: {func2}")