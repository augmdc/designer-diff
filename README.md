# AutoGen File Updater

## Overview

The AutoGen File Updater is a tool designed to automate the process of creating and updating AutoGen files based on changes in Designer files within the TeleAI project. This tool helps maintain synchronization between Designer files and their corresponding AutoGen files, ensuring that UI layouts are consistently represented across different file types.

## Features

- Automatically detect changes in Designer files
- Create or update corresponding AutoGen files
- Support for multiple layout types (Standard, L-Shaped, etc.)
- Logging functionality for tracking operations and debugging
- Initialization mode for creating AutoGen files for all existing Designer files

## Setup

### Prerequisites

- Python 3.7 or higher
- Git (for detecting file changes)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/autogen-file-updater.git
   cd autogen-file-updater
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script with the following command:

```
python main.py [options]
```

### Options:

- `--teleai-dir`: Path to the TeleAI directory for finding Designer files
- `--teleai-root`: Path to the TeleAI root directory for namespace generation
- `--init`: Initialize AutoGen files for all Designer files (use this for first-time setup)
- `-v`, `--verbosity`: Increase output verbosity (e.g., -v, -vv, -vvv)
- `--log-file`: Path to the log file (default: autogen_updater.log)

### Examples:

1. Initialize AutoGen files for all Designer files:
   ```
   python main.py --init --teleai-dir /path/to/teleai
   ```

2. Update AutoGen files based on recent changes with increased verbosity:
   ```
   python main.py --teleai-dir /path/to/teleai -vv
   ```

3. Specify a custom log file:
   ```
   python main.py --teleai-dir /path/to/teleai --log-file my_custom_log.log
   ```

## Project Structure

Here's an overview of the key files in this project and their purposes:

1. `main.py`: The entry point of the application. It parses command-line arguments, sets up logging, and orchestrates the overall process of updating AutoGen files.

2. `code_analyzer.py`: Contains functions for analyzing Designer files, extracting relevant methods, and finding differences between different layout methods.

3. `code_generator.py`: Responsible for generating the content of AutoGen files based on the analyzed Designer files.

4. `code_updater.py`: Manages the process of updating AutoGen files, including checking for changes and writing new content.

5. `file_operations.py`: Provides utility functions for file I/O operations, such as reading and writing files, and finding Designer files in the project directory.

6. `git_operations.py`: Contains functions for interacting with Git, including finding the TeleAI directory and getting file diffs.

7. `utils.py`: Includes various utility functions used across the project, such as finding the TeleAI directory and generating file paths.

## How It Works

1. The tool searches for the TeleAI directory in common locations or uses the provided path.
2. It finds all relevant Designer files within the TeleAI project.
3. For each Designer file:
   - It checks if there are any changes compared to the develop branch.
   - If changes are detected or in init mode, it extracts the InitializeComponent methods.
   - It analyzes the methods to find differences between different layout types.
   - It generates new content for the corresponding AutoGen file.
   - It writes the new content to the AutoGen file.
4. The tool logs all operations, successes, and failures to both the console and a log file.

## Troubleshooting

If you encounter any issues:

1. Check the log file for detailed error messages and the execution flow.
2. Ensure you have the correct permissions to read Designer files and write AutoGen files.
3. Verify that the TeleAI directory structure matches the expected layout.
4. Make sure your Git repository is in a clean state and you have the latest changes from the develop branch.

## Contributing

Contributions to improve the AutoGen File Updater are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive commit messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

## License

[Specify your license here]