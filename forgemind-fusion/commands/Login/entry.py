import adsk.core
import adsk.fusion
import os
import traceback
import threading
from ... import config
from ...lib import fusionAddInUtils as futil
from ...lib import auth_config

"""
ForgeMind Login Module

This module provides user authentication functionality for the ForgeMind add-in.
It implements a login dialog that collects user credentials, validates them,
and manages the login state throughout the add-in's lifecycle.

Key features:
- Login dialog with email/password inputs and "Remember Me" option
- Input validation with error messaging
- Persistence of login state
- Handling of login cancellation
- Integration with backend authentication service
- Session management and validation

Usage:
    The login module is designed to be the first command executed when the add-in starts.
    Other commands should check the login status using the get_login_status() function
    before executing their functionality.

Security Notes:
    - Credentials are validated through a secure backend service
    - Session tokens are managed securely
    - No sensitive information is stored locally
"""

app = adsk.core.Application.get()
ui = app.userInterface

# Global flag to track login state
is_logged_in = False
# Flag to track if login was explicitly canceled (only set by Cancel button)
login_canceled = False
# Flag to track if login is being retried due to validation failure
login_retry = False
# Store input values to repopulate on retry
last_email = ""
login_error_message = ""

CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}"
CMD_Description = "Login to ForgeMind"
IS_PROMOTED = True

# Global variables by referencing values from /config.py
WORKSPACE_ID = config.design_workspace
TAB_ID = config.tools_tab_id
TAB_NAME = config.my_tab_name

PANEL_ID = config.my_panel_id
PANEL_NAME = config.my_panel_name
PANEL_AFTER = config.my_panel_after

# Holds references to event handlers
local_handlers = []

def validate_credentials(email, password):
    """
    Validates user credentials against the backend authentication service.
    
    Parameters:
    -----------
    email : str
        The email address provided by the user
    password : str
        The password provided by the user
        
    Returns:
    --------
    bool
        True if credentials are valid, False otherwise
    """
    # Log the email being used (but never log passwords!)
    futil.log(f"Attempting to validate credentials for email: {email}")
    
    # Basic validation
    if not email or not password or '@' not in email:
        futil.log("Basic validation failed: invalid email or empty password")
        if not email:
            futil.log("Email is empty")
        if not password:
            futil.log("Password is empty")
        if '@' not in email:
            futil.log("Email does not contain @")
        return False
    
    # Verify credentials with backend
    return auth_config.verify_credentials(email, password)

def get_login_status():
    """
    Returns the current login status of the user.
    
    This function is the primary interface for other commands to check
    if the user is authenticated before executing their functionality.
    It also verifies the validity of the session if one exists.
    
    Returns:
    --------
    bool
        True if the user is logged in and authenticated
        False if the user is not logged in, canceled the login, or authentication failed
    """
    futil.log(f"Login status check: is_logged_in={is_logged_in}, canceled={login_canceled}, retry={login_retry}")
    
    # If login was canceled, always return False
    if login_canceled:
        return False
    
    # If not logged in, return False
    if not is_logged_in:
        return False
    
    # Validate the current session
    if auth_config.validate_session():
        return True
    else:
        # If session is invalid, clear it and return False
        is_logged_in = False
        auth_config.clear_session()
        return False

def execute_login_command():
    # Create the command definition
    cmd_def = ui.commandDefinitions.itemById(CMD_ID)
    if cmd_def:
        cmd_def.deleteMe()
    
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description
    )
    
    # Connect to command created event
    futil.add_handler(cmd_def.commandCreated, command_created)
    
    # Execute the command
    cmd_def.execute()
    return cmd_def

# Executed when add-in is run.
def start():
    futil.log("Login::start - Starting login sequence")
    execute_login_command()

# Executed when add-in is stopped.
def stop():
    # Clean up command definition
    command_definition = ui.commandDefinitions.itemById(CMD_ID)
    if command_definition:
        command_definition.deleteMe()

# Function to be called when a user clicks the corresponding button in the UI
def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f"Login::command_created - {CMD_NAME} Command Created Event")
    
    # Get the command
    cmd = args.command
    cmd.isOKButtonVisible = True
    cmd.cancelButtonText = "Cancel"
    cmd.okButtonText = "Login"
    
    # Get the command inputs
    inputs = cmd.commandInputs
    
    # Display error message if it exists from previous attempt
    global login_error_message
    if login_error_message:
        error_text = inputs.addTextBoxCommandInput('errorMessage', '', login_error_message, 2, True)
        error_text.isFullWidth = True
    
    # Create email input
    email_input = inputs.addStringValueInput('email', 'Email', last_email)
    email_input.isFullWidth = True
    
    # Create password input
    password_input = inputs.addStringValueInput('password', 'Password', '')
    password_input.isPassword = True  # Hide the password
    password_input.isFullWidth = True
    
    # Add remember me checkbox
    remember_me = inputs.addBoolValueInput('rememberMe', 'Remember Me', True, '', False)
    
    # Connect to the events
    futil.add_handler(
        cmd.execute, command_execute, local_handlers=local_handlers
    )
    futil.add_handler(
        cmd.inputChanged, command_input_changed, local_handlers=local_handlers
    )
    futil.add_handler(
        cmd.destroy, command_destroy, local_handlers=local_handlers
    )
    futil.add_handler(
        cmd.executePreview, command_preview, local_handlers=local_handlers
    )
    futil.add_handler(
        cmd.validateInputs, command_validate_inputs, local_handlers=local_handlers
    )
    futil.add_handler(
        cmd.incomingFromHTML, command_html_input, local_handlers=local_handlers
    )

# Handle input changes
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    # Clear error message when user starts typing
    global login_error_message
    input_id = args.input.id
    if input_id == 'email' or input_id == 'password':
        login_error_message = ""

# These are additional handlers to fully capture all cancel scenarios
def command_preview(args: adsk.core.CommandEventArgs):
    pass

def command_validate_inputs(args: adsk.core.ValidateInputsEventArgs):
    pass

def command_html_input(args: adsk.core.HTMLEventArgs):
    pass

# This function will be called when the user hits the OK button in the command dialog
def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"Login::command_execute - {CMD_NAME} Command Execute Event")
    
    global is_logged_in, last_email, login_error_message, login_retry
    
    # Get the inputs
    command = args.command
    inputs = command.commandInputs
    email = inputs.itemById('email').value
    password = inputs.itemById('password').value
    remember_me = inputs.itemById('rememberMe').value
    
    # Store email for repopulating the form if needed
    last_email = email
    
    try:
        # Validate credentials
        if validate_credentials(email, password):
            is_logged_in = True
            login_retry = False
            # If login is successful, save this state
            futil.log(f"Login successful for user: {email}")
            if remember_me:
                # Here we could securely store the session token for future use
                futil.log("Remember me set - session persistence not yet implemented")
        else:
            # If login fails, set appropriate error message
            login_error_message = "Invalid credentials. Please try again."
            futil.log(f"Login failed: {login_error_message}")
            is_logged_in = False
            login_retry = True  # Mark that we're retrying due to validation failure
            args.isValidResult = False
            
            # Show error in dialog
            try:
                ui.messageBox(login_error_message, 'Login Error')
            except:
                pass
            
            # Reopen the dialog after a brief delay
            timer = threading.Timer(0.1, execute_login_command)
            timer.start()
    except Exception as e:
        error_msg = str(e)
        login_error_message = "Authentication error. Please try again."
        
        # Check for specific error types to provide better user feedback
        if "API endpoint not found" in error_msg:
            login_error_message = "Backend service is starting up. Please wait a moment and try again."
        elif "connection" in error_msg.lower():
            login_error_message = "Could not connect to authentication service. Please check your connection."
        elif "timeout" in error_msg.lower():
            login_error_message = "Connection timed out. Please try again."
        elif "Backend server not available" in error_msg:
            login_error_message = "Authentication service is not available. Please try again in a moment."
        
        futil.log(f"Login error: {error_msg}")
        is_logged_in = False
        login_retry = True
        args.isValidResult = False
        
        # Show error in dialog
        try:
            ui.messageBox(login_error_message, 'Login Error')
        except:
            pass
            
        # Reopen the dialog after a brief delay
        timer = threading.Timer(0.1, execute_login_command)
        timer.start()

# This function will be called when the user completes or cancels the command
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers, login_canceled
    local_handlers = []
    futil.log(f"Login::command_destroy - {CMD_NAME} Command Destroy Event")
    
    # Check if command was canceled - check directly from the args
    if not is_logged_in and args.terminationReason == adsk.core.CommandTerminationReason.CancelledTerminationReason:
        login_canceled = True
        futil.log("Login dialog was canceled by user (detected in destroy handler)")
    
    # Handle termination if needed
    if login_canceled:
        futil.log("Login was canceled, terminating add-in...")
        
        # Show a message that the add-in is being terminated
        ui.messageBox('Add-in operation canceled by user. The add-in will now exit.')
        
        # Terminate the add-in completely
        try:
            # Stop any other commands
            from ... import commands
            commands.stop()
            
            # Clean up all UI elements
            stop()
            
            # Use sys.exit directly instead of adsk.terminate()
            import sys
            sys.exit(0)
        except SystemExit:
            # Catch SystemExit and re-raise it
            raise
        except:
            futil.log(f"Error during termination: {traceback.format_exc()}")
            import sys
            sys.exit(1)  # Exit with error code
            
    elif not is_logged_in and not login_retry:
        # This covers cases where the dialog might be closed without explicit cancel
        # but also not during a retry for validation failure
        futil.log("Login dialog was closed without successful login, terminating add-in...")
        ui.messageBox('Add-in requires login to operate. The add-in will now exit.')
        try:
            from ... import commands
            commands.stop()
            stop()
            import sys
            sys.exit(0)
        except SystemExit:
            # Catch SystemExit and re-raise it
            raise
        except:
            futil.log(f"Error during termination: {traceback.format_exc()}")
            import sys
            sys.exit(1)  # Exit with error code 