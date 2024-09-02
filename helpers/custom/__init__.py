"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

The helpers module contains all the helper functions and classes used in RickBot.
"""

# Import necessary modules for dynamic import of helper modules

# Import 'import_module' to programmatically import other modules.
from importlib import import_module

# Import 'Path' to interact with the file system and locate Python files in the current directory.
from pathlib import Path

# Dynamically import all Python modules in the current directory.
# This loop will go through each Python file in the same directory as this script,
# and import it unless it is a special module (like __init__.py) or has already been imported.
for f in Path(__file__).parent.glob("*.py"):
    module_name = f.stem  # Get the module name by removing the .py extension
    if (not module_name.startswith("_")) and (module_name not in globals()):
        import_module(
            f".{module_name}", __package__
        )  # Import the module using its relative name
    # Clean up loop variables to avoid polluting the global namespace
    del f, module_name

# Clean up imported functions to avoid leaving them in the global namespace
del import_module
