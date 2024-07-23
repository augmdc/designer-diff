import sys
import subprocess

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("Python path:")
for path in sys.path:
    print(f"  {path}")

try:
    import git
    print(f"\nGitPython successfully imported")
    print(f"GitPython version: {git.__version__}")
except ImportError as e:
    print(f"\nFailed to import GitPython. Error: {e}")

try:
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    print(f"\nGit version: {result.stdout.strip()}")
except FileNotFoundError:
    print("\nGit is not installed or not in the system PATH")

print("\nInstalled packages:")
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
print(result.stdout)