# AutoGen File Updater

## Overview

This tool automatically updates AutoGen files based on changes in Designer files within a teleai project structure. It compares the current state of Designer files against a specified Git branch (default: 'develop') and generates or updates corresponding AutoGen files.

## Features

- Automatically locates teleai project directory
- Finds all relevant Designer files
- Compares Designer files against a specified Git branch
- Creates or updates AutoGen files based on detected changes
- Supports separate specification of teleai directory and teleai root directory

## Prerequisites

- Python 3.6 or higher
- Git installed and accessible from command line
- Access to the teleai project repository

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up a virtual environment:
   
   On Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   
   On macOS and Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   You should see `(venv)` at the beginning of your command prompt, indicating that the virtual environment is active.

3. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

4. When you're done working on the project, you can deactivate the virtual environment:
   ```
   deactivate
   ```

## Usage

Ensure your virtual environment is activated before running the script:

On Windows:
```
venv\Scripts\activate
```

On macOS and Linux:
```
source venv/bin/activate
```

Then run the script using the following command:

```
python main.py [options]
```

### Command-line Options

- `--teleai-dir PATH`: Specifies the path to the teleai directory for finding Designer files. If not provided, the script will attempt to find it automatically.
- `--teleai-root PATH`: Specifies the path to the teleai root directory for namespace generation. If not provided, it defaults to the same value as `--teleai-dir`.
- `--branch NAME`: Specifies the Git branch to compare against (default: 'develop').
- `-v, --verbose`: Enables verbose output for debugging.

### Examples

1. Basic usage (auto-detect teleai directory):
   ```
   python main.py
   ```

2. Specify teleai directory:
   ```
   python main.py --teleai-dir C:\path\to\teleai
   ```

3. Specify both teleai directory and root:
   ```
   python main.py --teleai-dir C:\path\to\teleai --teleai-root C:\path\to\teleai\root
   ```

4. Compare against a different branch with verbose output:
   ```
   python main.py --branch feature-branch --verbose
   ```

## How It Works

1. The script first determines the teleai directory, either from the `--teleai-dir` argument or by searching common locations.
2. It then finds all Designer files (*.Designer.cs) within the teleai directory.
3. For each Designer file, it compares the current state against the specified Git branch.
4. If changes are detected, it processes the diff to extract relevant modifications.
5. Based on the extracted changes, it either creates a new AutoGen file or updates an existing one.
6. The AutoGen files are created with the correct namespace based on their location relative to the teleai root directory.

## File Structure

- `main.py`: The main script that orchestrates the entire process.
- `git_operations.py`: Contains functions for Git-related operations and file searching.
- `diff_handler.py`: Handles the processing of Git diffs to extract relevant changes.
- `code_updater.py`: Manages the creation and updating of AutoGen files.
- `requirements.txt`: Lists all Python package dependencies.

## Troubleshooting

- If the script fails to find the teleai directory, use the `--teleai-dir` option to specify it manually.
- If you encounter namespace-related issues in the generated AutoGen files, ensure that the `--teleai-root` is correctly set to the root of your teleai project.
- For more detailed logs, use the `--verbose` option.
- If you encounter any package-related errors, ensure your virtual environment is activated and all dependencies are installed.

## Contributing

Contributions to improve the tool are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature
3. Set up your virtual environment and install dependencies
4. Commit your changes
5. Push to your branch
6. Create a new Pull Request

## License

[Specify your license here]

## Contact

For any queries or issues, please [specify contact method or create an issue in the repository].