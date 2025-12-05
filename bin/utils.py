import sys
from pathlib import Path

# Lets Python files in this folder import normflix even though it's in a parent
# folder
sys.path.append(str(Path(__file__).absolute().parent.parent))
