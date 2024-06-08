import os
import subprocess
import sys
import re

def create_venv(venv_path):
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
    else:
        print(f"Virtual environment already exists at {venv_path}.")

def ensure_pip_installed(venv_path):
    pip_executable = os.path.join(venv_path, 'bin', 'pip')
    subprocess.run([pip_executable, 'install', '--upgrade', 'pip'], check=True)
    subprocess.run([pip_executable, 'install', '--upgrade', 'setuptools'], check=True)

def ensure_stdlib_list_installed(venv_path):
    pip_executable = os.path.join(venv_path, 'bin', 'pip')
    python_executable = os.path.join(venv_path, 'bin', 'python')
    try:
        __import__('stdlib_list')
    except ImportError:
        print("Installing stdlib_list...")
        subprocess.run([pip_executable, 'install', 'stdlib-list'], check=True)
        # Use the virtual environment's Python interpreter to ensure stdlib_list is installed
        result = subprocess.run([python_executable, '-c', 'import stdlib_list; print("stdlib_list imported successfully")'], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            print("Error: stdlib_list import failed within virtual environment.")
            sys.exit(1)

def install_requirements(venv_path):
    ensure_pip_installed(venv_path)
    ensure_stdlib_list_installed(venv_path)

    pip_executable = os.path.join(venv_path, 'bin', 'pip')
    requirements_file = 'requirements.txt'
    
    if os.path.exists(requirements_file):
        print("Installing requirements from requirements.txt...")
        subprocess.run([pip_executable, 'install', '-r', requirements_file], check=True)
    else:
        print("No requirements.txt found. Parsing the script for dependencies...")
        dependencies = parse_dependencies(script_path, venv_path)
        if dependencies:
            # Dynamically import stdlib_list within the function scope
            python_executable = os.path.join(venv_path, 'bin', 'python')
            version = sys.version_info
            formatted_version = f"{version.major}.{version.minor}"
            result = subprocess.run([python_executable, '-c', f'import stdlib_list; print(stdlib_list.stdlib_list("{formatted_version}"))'], capture_output=True, text=True)
            if result.returncode != 0:
                print("Error: stdlib_list command failed.")
                print(result.stdout)
                print(result.stderr)
                sys.exit(1)
            stdlib_modules = set(result.stdout.strip().strip('[]').replace("'", "").replace(" ", "").split(","))
            for dep in dependencies:
                if dep in stdlib_modules:
                    print(f"Skipping built-in module {dep}...")
                    continue
                if dep == 'dotenv':
                    dep = 'python-dotenv'  # Correct the dependency name
                print(f"Checking installation of {dep}...")
                try:
                    # Check if the dependency is already installed in the virtual environment
                    subprocess.run([pip_executable, 'show', dep.split('==')[0]], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    print(f"Installing {dep}...")
                    subprocess.run([pip_executable, 'install', dep], check=True)
        else:
            print("No dependencies found in the script.")

def parse_dependencies(script_path, venv_path):
    with open(script_path, 'r') as f:
        content = f.read()
    
    imports = re.findall(r'^\s*import\s+(\S+)|^\s*from\s+(\S+)\s+import', content, re.MULTILINE)
    dependencies = set()
    
    for imp in imports:
        module = imp[0] if imp[0] else imp[1]
        dependencies.add(module)
    
    return dependencies

def run_script(venv_path, script_path, *args):
    python_executable = os.path.join(venv_path, 'bin', 'python')
    subprocess.run([python_executable, script_path, *args], check=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python venv_wrapper.py <script.py> [args...]")
        sys.exit(1)

    global venv_path
    global script_path
    venv_path = '.venv'
    script_path = sys.argv[1]
    script_args = sys.argv[2:]

    create_venv(venv_path)
    install_requirements(venv_path)
    run_script(venv_path, script_path, *script_args)

if __name__ == "__main__":
    main()


