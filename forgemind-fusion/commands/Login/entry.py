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
import socket
import ssl
from ... import config
from ...lib import fusionAddInUtils as futil

app = adsk.core.Application.get()
ui = app.userInterface

# Global variables
local_handlers = []
is_authenticated = False
auth_token = None
user_id = None
was_logged_out = False  # Flag to prevent immediate re-authentication after logout

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
    """Authenticate user with the backend API and store credentials securely."""
    global is_authenticated, auth_token, user_id, was_logged_out
    
    # Don't attempt to re-authenticate if user explicitly logged out in this session
    if was_logged_out:
        futil.log("Authentication blocked: User explicitly logged out in this session. Please restart Fusion to login again.")
        return False, "You have logged out. Please restart Fusion to login again."
    
    try:
        # Prepare the authentication payload
        auth_data = {
            "email": email,
            "password": password
        }
        json_payload = json.dumps(auth_data).encode("utf-8")
        
        # Log the URL being used (without showing credentials)
        futil.log(f"Attempting to authenticate user {email} with backend at URL: {config.API_BASE_URL}")
        
        # Create SSL context for secure connections
        ssl_context = ssl.create_default_context()
        
        # For development environments, disable SSL verification if needed
        if config.DISABLE_SSL_VERIFICATION:
            futil.log("WARNING: SSL verification disabled - use only in development")
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        auth_req = urllib.request.Request(
            f"{config.API_BASE_URL}/fusion_auth",
            data=json_payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"ForgeMind-Fusion/{config.VERSION}",
                "X-Client-Platform": platform.system()
            },
            method="POST",
        )
        
        try:
            auth_response = urllib.request.urlopen(auth_req, context=ssl_context, timeout=15)
            
            if auth_response.getcode() != 200:
                futil.log(f"Authentication failed with status code: {auth_response.getcode()}")
                return False, "Authentication failed. Please check your credentials."
                
            # Parse the response
            response_data = auth_response.read().decode("utf-8")
            futil.log(f"Authentication response received, status code: {auth_response.getcode()}")
            
            try:
                json_data = json.loads(response_data)
                
                if not json_data.get("status"):
                    error_msg = json_data.get("message", "Authentication failed")
                    futil.log(f"Authentication failed with message: {error_msg}")
                    return False, error_msg
                
                # Store authentication data
                is_authenticated = True
                auth_token = json_data.get("token")
                user_id = json_data.get("user_id")
                
                if not auth_token or not user_id:
                    futil.log("Authentication missing token or user_id in response")
                    return False, "Invalid authentication response from server"
                
                # Clear the logged out flag since we're successfully logged in now
                was_logged_out = False
                
                # Log success details
                futil.log(f"Authentication successful for user ID: {user_id}")
                
                # Encrypted storage for auth data
                try:
                    save_auth_data(auth_token, user_id)
                    futil.log("Authentication data stored securely")
                except Exception as store_error:
                    futil.log(f"Warning: Failed to store authentication data: {str(store_error)}")
                
                # Success!
                return True, "Authentication successful"
                
            except json.JSONDecodeError as json_error:
                futil.log(f"Error parsing authentication response JSON: {str(json_error)}")
                futil.log(f"Raw response: {response_data}")
                return False, "Invalid response format from server"
                
        except urllib.error.HTTPError as http_error:
            error_msg = f"HTTP Error during authentication: {http_error.code}"
            detailed_error = f"Server error response: {http_error.reason}"
            
            # Additional error info for debugging
            futil.log(f"Authentication HTTP error: {error_msg}")
            futil.log(f"Error reason: {http_error.reason}")
            futil.log(f"Error headers: {http_error.headers}")
            
            if http_error.code == 403:
                futil.log("Forbidden - the server is rejecting the request. Check if the backend is properly configured.")
                detailed_error = "\n\nForbidden - the server is rejecting the request. Check if the backend is properly configured."
            
            # Try to read error response body if available
            try:
                error_body = http_error.read().decode("utf-8")
                futil.log(f"Error response body: {error_body}")
                if error_body:
                    try:
                        error_json = json.loads(error_body)
                        if error_json.get("message"):
                            detailed_error += f"\n\nServer message: {error_json.get('message')}"
                    except:
                        detailed_error += f"\n\nServer response: {error_body}"
            except:
                pass
                
            return False, f"{error_msg}\n{detailed_error}"
            
        except urllib.error.URLError as url_error:
            error_msg = f"URL Error during authentication: {str(url_error.reason)}"
            futil.log(error_msg)
            futil.log(f"Using API URL: {config.API_BASE_URL}")
            return False, f"{error_msg}\n\nPlease check your internet connection and backend URL configuration."
            
        except Exception as e:
            error_msg = f"Unexpected error during authentication: {str(e)}"
            futil.log(error_msg)
            return False, error_msg
    
    except Exception as e:
        error_trace = traceback.format_exc()
        futil.log(f"Unexpected error during authentication: {str(e)}\nTraceback: {error_trace}")
        return False, f"Authentication failed: {str(e)}"

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
    global is_authenticated, auth_token, user_id, was_logged_out
    
    # If we've explicitly logged out in this session, don't try to re-authenticate
    # until the user explicitly logs in again
    if was_logged_out:
        futil.log("Not loading auth data because user explicitly logged out")
        return False
    
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
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"ForgeMind-Fusion/{config.VERSION}",
                "X-Client-Platform": platform.system()
            },
            method="POST",
        )
        
        # Create SSL context for secure connections
        ssl_context = ssl.create_default_context()
        
        # For development environments, disable SSL verification if needed
        if config.DISABLE_SSL_VERIFICATION:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            verify_response = urllib.request.urlopen(verify_req, context=ssl_context, timeout=15)
        except urllib.error.HTTPError as e:
            futil.log(f"Token verification failed with HTTP error: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            futil.log(f"Token verification connection error: {e.reason}")
            return False
        except Exception as e:
            futil.log(f"Token verification unexpected error: {str(e)}")
            return False
        
        if verify_response.getcode() != 200:
            futil.log("Token verification failed with status code: " + str(verify_response.getcode()))
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
    global is_authenticated, auth_token, user_id, was_logged_out
    
    try:
        # Store user_id for logging and backend notification
        uid_to_clear = user_id
        
        # First invalidate local authentication state
        is_authenticated = False
        auth_token = None
        user_id = None
        was_logged_out = True  # Set flag to prevent immediate re-authentication
        
        futil.log("Starting logout process...")
        
        # Notify backend that plugin has logged out
        if uid_to_clear:
            try:
                futil.log(f"Notifying backend of logout for user {uid_to_clear}")
                logout_req = urllib.request.Request(
                    f"{config.API_BASE_URL}/plugin_logout",
                    data=json.dumps({"user_id": uid_to_clear}).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": f"ForgeMind-Fusion/{config.VERSION}",
                        "X-Client-Platform": platform.system()
                    },
                    method="POST",
                )
                
                # Create SSL context for secure connections
                ssl_context = ssl.create_default_context()
                
                # For development environments, disable SSL verification if needed
                if config.DISABLE_SSL_VERIFICATION:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                
                logout_response = urllib.request.urlopen(logout_req, context=ssl_context, timeout=10)
                response_data = logout_response.read().decode('utf-8')
                futil.log(f"Logout notification sent to backend: {response_data}")
            except Exception as e:
                futil.log(f"Error notifying backend about logout: {str(e)}")
                # Continue with local logout even if backend notification fails
        
        # Delete the auth files
        auth_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "auth")
        auth_file = os.path.join(auth_dir, "auth.secure")
        legacy_file = os.path.join(auth_dir, "auth.json")
        
        files_removed = 0
        
        # Remove both auth files if they exist
        if os.path.exists(auth_file):
            try:
                os.remove(auth_file)
                files_removed += 1
                futil.log(f"Removed auth file: {auth_file}")
            except Exception as e:
                futil.log(f"Error removing auth file {auth_file}: {str(e)}")
                return False
                
        if os.path.exists(legacy_file):
            try:
                os.remove(legacy_file)
                files_removed += 1
                futil.log(f"Removed legacy auth file: {legacy_file}")
            except Exception as e:
                futil.log(f"Error removing legacy auth file {legacy_file}: {str(e)}")
                return False
        
        if files_removed == 0:
            futil.log("Warning: No auth files found to remove")
        
        futil.log(f"Logged out user {uid_to_clear} successfully")
        return True
    except Exception as e:
        futil.log(f"Error during logout: {str(e)}")
        return False

def start():
    """Start the Login command."""
    # Create command definition
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if not cmd_def:
        cmd_def = ui.commandDefinitions.addButtonDefinition(
            CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
        )
    
    # Add command created handler
    futil.add_handler(cmd_def.commandCreated, command_created)
    
    # Check if already authenticated
    if load_auth_data():
        # User is already authenticated, show a dialog with logout option
        # Use OK/Cancel instead of Yes/No since the Yes/No constants don't seem to work properly
        result = ui.messageBox(
            "You are already authenticated with ForgeMind.\n\nWould you like to sign out?",
            "ForgeMind Authentication",
            1,  # OK/Cancel buttons (0 = OK, 1 = OK/Cancel)
            2   # Question mark icon
        )
        
        # For OK/Cancel dialog: 0 = OK clicked, 1 = Cancel clicked
        if result == 0:  # OK was clicked (equivalent to "Yes")
            # User wants to logout
            if logout():
                ui.messageBox("You have been signed out successfully.")
                # Execute the command to show the login dialog again
                cmd_def.execute()
            else:
                ui.messageBox("Error during logout. Please try again.", "Logout Failed", 0, 1)  # OK button with warning icon
        return
    
    # If not authenticated, execute the command to show the login dialog
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
    """This function is called when the user clicks the command in the Fusion 360 UI."""
    global is_authenticated, was_logged_out, local_handlers
    
    futil.log("Login Command Created Event")
    
    # Get the command
    cmd = args.command
    
    # Get the CommandInputs collection to create new command inputs.
    inputs = cmd.commandInputs
    
    # Create a group input.
    group_input = inputs.addGroupCommandInput("login_group", "Login")
    group_child_inputs = group_input.children
    
    # Email input
    email_input = group_child_inputs.addStringValueInput("email", "Email", "")
    
    # Password input
    password_input = group_child_inputs.addStringValueInput("password", "Password", "")
    password_input.isPassword = True
    
    # Text message for status/error - initially empty
    message_input = group_child_inputs.addTextBoxCommandInput("message", "Status", "", 2, True)
    message_input.text = ""
    
    # Check if already authenticated
    if is_authenticated:
        email_input.isEnabled = False
        password_input.isEnabled = False
        message_input.text = "You are already logged in."
    elif was_logged_out:
        # In this case the user explicitly logged out, so we want to make sure
        # they confirm re-authentication
        message_input.text = "You have logged out. Please log in again."
    
    # Connect to the command events
    futil.add_handler(
        args.command.execute, command_execute, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.destroy, command_destroy, local_handlers=local_handlers
    )

def command_execute(args: adsk.core.CommandEventArgs):
    """This event is fired when the user enters all the values required by your command and clicks OK."""
    global is_authenticated, auth_token, user_id, was_logged_out
    
    futil.log(f"Login Command Execute Event")
    
    # Get the command inputs.
    inputs = args.command.commandInputs
    email_input = inputs.itemById("email")
    password_input = inputs.itemById("password")
    
    # Get the input values.
    email = email_input.value
    password = password_input.value
    
    # Validate inputs
    if not email or not password:
        ui.messageBox("Please enter both email and password.", "Login Error")
        return
    
    # Attempt to authenticate with the backend
    success, message = authenticate(email, password)
    
    if success:
        # Reset was_logged_out flag since we've explicitly logged in now
        was_logged_out = False
        ui.messageBox(f"Successfully authenticated as {email}.", "Login Successful")
        
        # Import the Info/entry module to start polling after login
        from ..Info import entry as info_entry
        
        # Give a short delay for UI to update before starting polling
        def delayed_start_polling():
            futil.log("Delayed start polling after login...")
            info_entry.start_polling()
            
        threading.Timer(0.5, delayed_start_polling).start()
    else:
        ui.messageBox(f"Login failed: {message}", "Login Error")

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