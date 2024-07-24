# AutoGen File Updater

## Overview
This tool automatically updates AutoGen files based on changes in Designer files for the TeleAI project. It compares the current state of Designer files with a specified Git branch (default: 'develop') and generates or updates corresponding AutoGen files with the relevant changes.

## Features
- Automatically finds the TeleAI directory
- Detects and processes changes in Designer files
- Creates or updates AutoGen files based on the detected changes
- Provides detailed logging for better debugging and monitoring
- Supports command-line arguments for flexible usage

## Requirements
- Python 3.6+
- GitPython library

## Installation
1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```
   pip install gitpython
   ```

## Usage
Run the script using Python:

```
python main.py [options]
```

### Command-line Options:
- `--teleai-dir PATH`: Specify the path to the TeleAI directory. If not provided, the script will attempt to find it automatically.
- `--branch BRANCH`: Specify the Git branch to compare against (default: 'develop').
- `-v, --verbose`: Enable verbose output for detailed logging.

### Examples:
1. Run with default settings:
   ```
   python main.py
   ```

2. Specify a custom TeleAI directory and branch:
   ```
   python main.py --teleai-dir C:\path\to\teleai --branch feature-branch
   ```

3. Run with verbose logging:
   ```
   python main.py -v
   ```

## How It Works
1. The script searches for the TeleAI directory (unless specified).
2. It finds all Designer files within the TeleAI project structure.
3. For each Designer file, it compares the current state with the specified branch.
4. If changes are detected, it processes the diff and updates or creates the corresponding AutoGen file.
5. Detailed logs are generated throughout the process.

## File Structure
- `main.py`: The main script that orchestrates the update process.
- `code_updater.py`: Contains the `CodeUpdater` class responsible for creating and updating AutoGen files.
- `diff_handler.py`: Handles the processing of Git diffs.
- `git_operations.py`: Manages Git-related operations like finding diffs and locating the TeleAI directory.

## Logging
The script uses Python's logging module to provide informative output. Use the `-v` or `--verbose` flag for detailed debug information.

## Contributing
Contributions to improve the tool are welcome. Please submit a pull request or open an issue to discuss proposed changes.

## License
[Specify your license here]