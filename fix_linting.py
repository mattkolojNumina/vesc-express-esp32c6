#!/usr/bin/env python3
"""
Automatic code linting fixes for tool discoverability system.
Fixes common issues like trailing whitespace, unused imports, blank lines, etc.
"""

import re
import os
from pathlib import Path

def fix_file_linting(file_path: str):
    """Fix common linting issues in a file."""
    print(f"Fixing linting issues in {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix trailing whitespace
    content = re.sub(r' +$', '', content, flags=re.MULTILINE)
    
    # Fix blank lines with whitespace
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    
    # Ensure file ends with newline
    if not content.endswith('\n'):
        content += '\n'
    
    # Remove unused imports in main enhancer file
    if 'tool_discoverability_enhancer.py' in file_path:
        # Remove unused imports
        content = re.sub(r'^import os\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^import shutil\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^import subprocess\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^from typing import Dict, List, Any, Optional, Tuple\n',
                        'from typing import Dict, Any\n', content, flags=re.MULTILINE)
        content = re.sub(r'^from datetime import datetime\n', '', content, flags=re.MULTILINE)
    
    # Remove unused imports in generators file
    if 'tool_discoverability_generators.py' in file_path:
        content = re.sub(r'^import json\n', '', content, flags=re.MULTILINE)
        content = re.sub(r'^from pathlib import Path\n', '', content, flags=re.MULTILINE)
    
    # Fix class spacing (2 blank lines before class)
    content = re.sub(r'\n\nclass ', '\n\n\nclass ', content)
    content = re.sub(r'\n\n\n\nclass ', '\n\n\nclass ', content)  # Fix over-correction
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

def main():
    """Fix linting issues in all refactored files."""
    files_to_fix = [
        'tool_discoverability_enhancer.py',
        'tool_discoverability_templates.py', 
        'tool_discoverability_generators.py'
    ]
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            fix_file_linting(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()