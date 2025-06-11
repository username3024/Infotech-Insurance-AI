import unittest
import os
import sys

# Add the project root to the Python path to allow imports like 'from main import app'
# and 'from app.models...' etc., from within the test files.
# The 'ai_underwriter' directory is effectively our source root.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_underwriter'))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__))) # Add /app to path
sys.path.insert(0, project_root) # Add /app/ai_underwriter to path


if __name__ == "__main__":
    print(f"Current sys.path: {sys.path}")
    print(f"Attempting to discover tests in: {os.path.join(project_root, 'tests')}")

    loader = unittest.TestLoader()
    # Adjust start_dir to point to where the 'tests' directory is located
    # relative to this script, or use an absolute path.
    # Since run_tests.py is in /app, and tests are in /app/ai_underwriter/tests
    suite = loader.discover(start_dir=os.path.join(project_root, 'tests'), pattern='test_*.py')

    # Check if any tests were loaded
    if suite.countTestCases() == 0:
        print("\nNo tests found. Check the discovery path and pattern.")
        print(f"Discovery path used: {os.path.join(project_root, 'tests')}")
        print("If your tests are in a different location, adjust 'start_dir'.")
        print("Ensure test files are named 'test_*.py' and contain unittest.TestCase classes.")
    else:
        print(f"\nFound {suite.countTestCases()} tests. Running them...\n")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
