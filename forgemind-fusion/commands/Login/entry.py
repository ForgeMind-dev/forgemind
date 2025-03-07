import adsk.core
import adsk.fusion
import os
import json
import urllib.request
import urllib.parse
import traceback
import threading
import time
import base64
import hashlib
import platform
import uuid
import string
import random
from ... import config
from ...lib import fusionAddInUtils as futil

app = adsk.core.Application.get()
ui = app.userInterface

# Global variables
local_handlers = []
is_authenticated = False
auth_token = None
user_id = None

# Command properties
CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}"
CMD_Description = "ForgeMind Login"
IS_PROMOTED = True

# Global variables by referencing values from /config.py
WORKSPACE_ID = config.design_workspace
TAB_ID = config.tools_tab_id
TAB_NAME = config.my_tab_name

PANEL_ID = config.my_panel_id
PANEL_NAME = config.my_panel_name
PANEL_AFTER = config.my_panel_after

# Resource location for command icons
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

def get_machine_fingerprint():
    """Create a unique fingerprint for this machine to prevent token portability."""
    try:
        # Collect hardware information that is unlikely to change
        machine_id = platform.node()  # Computer name
        cpu_info = platform.processor()
        system_info = platform.platform()
        
        # On macOS, try to get hardware UUID
        if platform.system() == 'Darwin':
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Hardware UUID' in line:
                            machine_id = line.split(':')[1].strip()
                            break
            except Exception:
                pass
        
        # Combine and hash the information
        fingerprint_data = f"{machine_id}|{cpu_info}|{system_info}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    except Exception as e:
        futil.log(f"Error generating machine fingerprint: {e}")
        # Fallback to a less specific identifier
        return hashlib.sha256(platform.node().encode()).hexdigest()

def get_encryption_key():
    """Get a machine-specific encryption key."""
    machine_fingerprint = get_machine_fingerprint()
    # Create a key based on the machine fingerprint and a constant
    key_material = f"{machine_fingerprint}_{config.COMPANY_NAME}_{config.ADDIN_NAME}"
    return hashlib.sha256(key_material.encode()).digest()

def encrypt_data(data):
    """Simple encryption using XOR with a key derived from the machine fingerprint."""
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)
        
        # Add some random padding to prevent identical encryptions for identical data
        padding = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        padded_data = padding + json_data
        data_bytes = padded_data.encode()
        
        # Get the encryption key
        key = get_encryption_key()
        
        # Create a repeating key pattern of the same length as the data
        key_repeated = (key * (len(data_bytes) // len(key) + 1))[:len(data_bytes)]
        
        # XOR the data with the key
        encrypted_bytes = bytes(a ^ b for a, b in zip(data_bytes, key_repeated))
        
        # Return the base64 encoded string
        return base64.b64encode(encrypted_bytes).decode()
    except Exception as e:
        futil.log(f"Encryption error: {str(e)}")
        return None

def decrypt_data(encrypted_str):
    """Decrypt data that was encrypted using the encrypt_data function."""
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_str)
        
        # Get the encryption key
        key = get_encryption_key()
        
        # Create a repeating key pattern of the same length as the data
        key_repeated = (key * (len(encrypted_bytes) // len(key) + 1))[:len(encrypted_bytes)]
        
        # XOR the encrypted data with the key to get the original data
        decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, key_repeated))
        
        # Remove the padding and parse the JSON
        decrypted_str = decrypted_bytes.decode()
        # Skip the first 16 characters (padding)
        json_str = decrypted_str[16:]
        
        # Parse the JSON
        return json.loads(json_str)
    except Exception as e:
        futil.log(f"Decryption error: {str(e)}")
        return None

def authenticate(email, password):
    """Authenticate with the backend server using email and password."""
    global is_authenticated, auth_token, user_id
    
    try:
        # Prepare the authentication payload
        auth_data = {
            "email": email,
            "password": password
        }
        json_payload = json.dumps(auth_data).encode("utf-8")
        
        # Make the authentication request to the backend
        auth_req = urllib.request.Request(
            f"{config.API_BASE_URL}/fusion_auth",
            data=json_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        auth_response = urllib.request.urlopen(auth_req)
        
        if auth_response.getcode() != 200:
            futil.log(f"Authentication failed with status code: {auth_response.getcode()}")
            return False, "Authentication failed. Please check your credentials."
        
        # Parse the response
        response_data = auth_response.read().decode("utf-8")
        json_data = json.loads(response_data)
        
        if not json_data.get("status"):
            return False, json_data.get("message", "Authentication failed")
        
        # Store authentication data
        is_authenticated = True
        auth_token = json_data.get("token")
        user_id = json_data.get("user_id")
        
        # Save authentication data securely
        save_auth_data(auth_token, user_id)
        
        return True, "Authentication successful"
    
    except Exception as e:
        futil.log(f"Authentication error: {str(e)}")
        return False, f"Authentication error: {str(e)}"

def save_auth_data(token, uid):
    """Save authentication data securely."""
    try:
        # Create the auth directory if it doesn't exist
        auth_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "auth")
        if not os.path.exists(auth_dir):
            os.makedirs(auth_dir)
        
        # Get machine fingerprint to bind the token to this machine
        machine_fingerprint = get_machine_fingerprint()
        
        # Create a secure hash of the token with the machine fingerprint
        token_hash = hashlib.sha256(f"{token}{machine_fingerprint}".encode()).hexdigest()
        
        # Build auth data with additional security measures
        auth_data = {
            "token": token,
            "user_id": uid,
            "timestamp": time.time(),
            "machine_fingerprint": machine_fingerprint,
            "token_hash": token_hash,
            "expiration": time.time() + (7 * 24 * 60 * 60),  # 7 days from now
            "version": 1  # For future upgrades to token format
        }
        
        # Encrypt the auth data
        encrypted_data = encrypt_data(auth_data)
        if not encrypted_data:
            raise Exception("Failed to encrypt authentication data")
            
        # Create integrity signature
        integrity_signature = hashlib.sha256(encrypted_data.encode()).hexdigest()
        
        # Save the auth data with integrity signature
        auth_file = os.path.join(auth_dir, "auth.secure")
        with open(auth_file, "w") as f:
            json.dump({
                "data": encrypted_data,
                "signature": integrity_signature,
                "version": 1  # For future upgrades to storage format
            }, f)
        
        futil.log("Authentication data saved securely")
    except Exception as e:
        futil.log(f"Error saving authentication data: {str(e)}")

def load_auth_data():
    """Load authentication data securely."""
    global is_authenticated, auth_token, user_id
    
    try:
        # Check if the auth file exists
        auth_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "auth")
        auth_file = os.path.join(auth_dir, "auth.secure")
        
        # Try the legacy auth.json for backward compatibility
        if not os.path.exists(auth_file):
            legacy_file = os.path.join(auth_dir, "auth.json")
            if os.path.exists(legacy_file):
                futil.log("Found legacy auth file, migrating to secure format")
                try:
                    with open(legacy_file, "r") as f:
                        legacy_data = json.load(f)
                        token = legacy_data.get("token")
                        uid = legacy_data.get("user_id")
                        # If valid legacy data found, save in new secure format and delete the old file
                        if token and uid:
                            save_auth_data(token, uid)
                            os.remove(legacy_file)
                            auth_token = token
                            user_id = uid
                            is_authenticated = True
                            return True
                except Exception as e:
                    futil.log(f"Error migrating legacy auth data: {str(e)}")
            return False
        
        # Load the encrypted auth data
        with open(auth_file, "r") as f:
            stored_data = json.load(f)
        
        # Verify the version
        if stored_data.get("version", 0) != 1:
            futil.log("Unsupported auth data version")
            return False
            
        # Get the encrypted data and signature
        encrypted_data = stored_data.get("data")
        stored_signature = stored_data.get("signature")
        
        if not encrypted_data or not stored_signature:
            futil.log("Invalid auth data format")
            return False
            
        # Verify integrity signature to detect tampering
        calculated_signature = hashlib.sha256(encrypted_data.encode()).hexdigest()
        
        if calculated_signature != stored_signature:
            futil.log("Auth data integrity check failed - possible tampering detected")
            return False
        
        # Decrypt the data
        auth_data = decrypt_data(encrypted_data)
        if not auth_data:
            futil.log("Failed to decrypt auth data")
            return False
        
        # Get current machine fingerprint
        current_fingerprint = get_machine_fingerprint()
        
        # Verify machine fingerprint to prevent token portability
        if auth_data.get("machine_fingerprint") != current_fingerprint:
            futil.log("Auth data machine fingerprint mismatch - possible token theft")
            return False
        
        # Verify token hash
        token = auth_data.get("token")
        stored_token_hash = auth_data.get("token_hash")
        calculated_token_hash = hashlib.sha256(f"{token}{current_fingerprint}".encode()).hexdigest()
        
        if stored_token_hash != calculated_token_hash:
            futil.log("Token hash verification failed")
            return False
        
        # Check expiration
        if time.time() > auth_data.get("expiration", 0):
            futil.log("Auth token expired")
            return False
        
        # Set the global variables
        auth_token = token
        user_id = auth_data.get("user_id")
        
        # Verify the token with the backend
        verify_req = urllib.request.Request(
            f"{config.API_BASE_URL}/verify_token",
            data=json.dumps({"token": auth_token}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        verify_response = urllib.request.urlopen(verify_req)
        
        if verify_response.getcode() != 200:
            futil.log("Token verification failed")
            return False
        
        response_data = verify_response.read().decode("utf-8")
        json_data = json.loads(response_data)
        
        if not json_data.get("status"):
            futil.log("Token is invalid")
            return False
        
        is_authenticated = True
        futil.log("Authentication loaded successfully")
        return True
    
    except Exception as e:
        futil.log(f"Error loading authentication data: {str(e)}")
        return False

def logout():
    """Log out the user by clearing the authentication data."""
    global is_authenticated, auth_token, user_id
    
    try:
        # Clear the global variables
        is_authenticated = False
        auth_token = None
        user_id = None
        
        # Delete the auth file
        auth_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "auth")
        auth_file = os.path.join(auth_dir, "auth.secure")
        legacy_file = os.path.join(auth_dir, "auth.json")
        
        # Remove both auth files if they exist
        if os.path.exists(auth_file):
            os.remove(auth_file)
        if os.path.exists(legacy_file):
            os.remove(legacy_file)
        
        futil.log("Logged out successfully")
        return True
    except Exception as e:
        futil.log(f"Error during logout: {str(e)}")
        return False

def start():
    """Start the Login command."""
    # Check if already authenticated
    if load_auth_data():
        futil.log("User is already authenticated")
        return
    
    # Create command definition
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if not cmd_def:
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
        )
    
    # Add command created handler
    futil.add_handler(cmd_def.commandCreated, command_created)
    
    # Execute the command to show the login dialog
    cmd_def.execute()

def stop():
    """Stop the Login command."""
    # Clean up the command definition
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()
    
    # Clear the local handlers
    global local_handlers
    local_handlers = []

def command_created(args: adsk.core.CommandCreatedEventArgs):
    """Handle the command created event."""
    futil.log(f"{CMD_NAME} Command Created Event")
    
    # Get the command
    cmd = args.command
    
    # Connect to the command events
    futil.add_handler(cmd.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(cmd.destroy, command_destroy, local_handlers=local_handlers)
    
    # Create the command inputs
    inputs = cmd.commandInputs
    
    # Add a text box for the email
    email_input = inputs.addStringValueInput('email', 'Email', '')
    
    # Add a text box for the password (secured)
    password_input = inputs.addStringValueInput('password', 'Password', '')
    password_input.isPassword = True
    
    # Add a message for errors
    message_text = inputs.addTextBoxCommandInput('message', '', '', 2, True)
    message_text.isFullWidth = True

def command_execute(args: adsk.core.CommandEventArgs):
    """Handle the command execute event."""
    futil.log(f"{CMD_NAME} Command Execute Event")
    
    # Get the inputs
    inputs = args.command.commandInputs
    
    email_input = inputs.itemById('email')
    password_input = inputs.itemById('password')
    message_input = inputs.itemById('message')
    
    # Validate inputs
    if not email_input.value or not password_input.value:
        message_input.text = "Email and password are required"
        args.executeFailed = True
        args.executeFailedMessage = "Email and password are required"
        return
    
    # Authenticate with the backend
    success, message = authenticate(email_input.value, password_input.value)
    
    if not success:
        message_input.text = message
        args.executeFailed = True
        args.executeFailedMessage = message
        return
    
    # Authentication successful
    ui.messageBox("Login successful! You can now use ForgeMind.")

def command_destroy(args: adsk.core.CommandEventArgs):
    """Handle the command destroy event."""
    global local_handlers
    local_handlers = []
    futil.log(f"{CMD_NAME} Command Destroy Event")

def is_user_authenticated():
    """Check if the user is authenticated."""
    global is_authenticated
    
    # If not authenticated, try to load from saved data
    if not is_authenticated:
        is_authenticated = load_auth_data()
    
    return is_authenticated

def get_user_id():
    """Get the authenticated user's ID."""
    global user_id
    return user_id 