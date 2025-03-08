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
        print(f"Warning: .env file not found at {env_path}")
        return
    
    print(f"Loading environment variables from {env_path}")
    loaded_vars = []
    
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
                    loaded_vars.append(key)
    
    print(f"Loaded environment variables: {', '.join(loaded_vars)}")

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
# Use the production URL as the default (not localhost) to prevent connection issues
default_url = "https://forgemind-backend-5b7b6de8ddcc.herokuapp.com"
API_BASE_URL = os.environ.get("API_BASE_URL", default_url)

# Log the API URL for debugging purposes
print(f"Using API_BASE_URL: {API_BASE_URL}")

# SSL verification configuration
# In production, this should always be True
# Set to False only for debugging HTTPS connection issues
DISABLE_SSL_VERIFICATION = False

# Add version information
VERSION = "1.0.0"

# Connection settings
CONNECTION_TIMEOUT = 15  # seconds
CONNECTION_RETRIES = 3

# Enable additional debugging
DEBUG_HTTP_REQUESTS = True
