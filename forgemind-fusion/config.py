# Application Global Variables
# Adding application wide global variables here is a convenient technique
# It allows for access across multiple event handlers and modules

import os

# Function to load environment variables from a .env file without external dependencies
def load_env_file(env_path=None):
    """Load environment variables from a .env file using only built-in libraries."""
    if env_path is None:
        # Try to find .env in the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
    
    if not os.path.exists(env_path):
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse the line
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                # Strip quotes if present
                value = value.strip().strip('\'"')
                
                # Set the environment variable if it's not already set
                if key not in os.environ:
                    os.environ[key] = value

# Load environment variables
load_env_file()

# Set to False to remove most log messages from text palette
DEBUG = True

ADDIN_NAME = 'ForgeMind'
COMPANY_NAME = 'ForgeMind'

# FIXME add good comments
design_workspace = 'FusionSolidEnvironment'
tools_tab_id = "ToolsTab"
my_tab_name = "test"  # Only used if creating a custom Tab

my_panel_id = f'{ADDIN_NAME}_panel_2'
my_panel_name = ADDIN_NAME
my_panel_after = ''

# Backend API base URL - can be changed in .env file
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000")
