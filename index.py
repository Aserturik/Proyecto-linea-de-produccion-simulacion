import sys
import os

# Add the 'aleatorios' directory to sys.path
# This allows importing 'test_random_quality' and ensures its internal imports work
# (e.g., 'from src.modelos...' will resolve to 'aleatorios/src/modelos...')
current_script_dir = os.path.dirname(os.path.abspath(__file__))
aleatorios_dir_path = os.path.join(current_script_dir, 'aleatorios')
if aleatorios_dir_path not in sys.path:
    sys.path.insert(0, aleatorios_dir_path)

# Now we can import from test_random_quality
# The RandomTester class needs its own imports (numpy, tabulate, matplotlib, src.modelos...) 
# to be resolved correctly. Adding aleatorios_dir_path to sys.path handles 'src.modelos...'.
# The user needs to ensure numpy, tabulate, and matplotlib are installed.
try:
    from test_random_quality import RandomTester
except ImportError as e:
    print(f"Error importing RandomTester: {e}")
    print("Please ensure that the 'aleatorios' directory is structured correctly and all dependencies (numpy, tabulate, matplotlib) are installed.")
    print("Expected structure includes: ./aleatorios/test_random_quality.py and ./aleatorios/src/modelos/...")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during import: {e}")
    sys.exit(1)


def main():
    """
    Main function to set up and run the RandomTester.
    """
    # Default sample size, same as in test_random_quality.py
    sample_size = 10000
    
    # Allow specifying sample size via command line arguments to index.py
    # e.g., python index.py 5000
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
            print(f"Using custom sample size from command line: {sample_size}")
        except ValueError:
            print(f"Invalid sample size argument: '{sys.argv[1]}'. Using default: {sample_size}")
            
    # Execute tests
    print(f"Initializing RandomTester with sample_size = {sample_size}")
    try:
        tester = RandomTester(sample_size=sample_size)
        tester.run_all_tests()
        print("RandomTester finished.")
    except Exception as e:
        print(f"An error occurred while running the tests: {e}")
        # Potentially print traceback for more detailed debugging if needed
        # import traceback
        # traceback.print_exc()

if __name__ == '__main__':
    main()
