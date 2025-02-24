import os
import sys
from pathlib import Path

# Get the project root directory
project_root = str(Path(__file__).parent.parent)

# Add the project root to Python path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root) 