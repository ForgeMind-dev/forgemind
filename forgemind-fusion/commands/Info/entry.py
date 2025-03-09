#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.

import time
import adsk.core, adsk.fusion, adsk.cam
import os
from ... import config
from ...logic import run_logic, get_workspace_state, set_active_chat, debug_log
from ...lib import fusionAddInUtils as futil
import threading
import json
import urllib.request

app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}"
CMD_Description = "ForgeMind AI"
IS_PROMOTED = True

# Global variables by referencing values from /config.py
WORKSPACE_ID = config.design_workspace
TAB_ID = config.tools_tab_id
TAB_NAME = config.my_tab_name

PANEL_ID = config.my_panel_id
PANEL_NAME = config.my_panel_name
PANEL_AFTER = config.my_panel_after

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# Holds references to event handlers
local_handlers = []
# Holds reference to the timer
timer = None
# Flag to check if the timer is running
is_timer_running = False

def save_and_compress_screenshot(filename_prefix):
    screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{filename_prefix}.png")
    
    app.activeViewport.saveAsImageFile(screenshot_path, 1920, 1080)
    futil.log(f"entry.py::save_and_compress_screenshot - Screenshot saved to {screenshot_path}")
    
    return screenshot_path

def delete_files(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            futil.log(f"entry.py::delete_files - Deleted file {file_path}")

def get_logic():
    # Check authentication first - don't poll if not authenticated
    from ...commands.Login import entry as login
    if not login.is_user_authenticated():
        futil.log("entry.py::get_logic - User not authenticated, skipping poll")
        return
    
    # Get workspace description
    workspace_desc = get_workspace_state()
    
    # Add user_id to the request
    workspace_desc["user_id"] = login.get_user_id()
    
    json_payload = json.dumps(workspace_desc).encode("utf-8")

    # Call /poll first with workspace description
    poll_req = urllib.request.Request(
        f"{config.API_BASE_URL}/poll",
        data=json_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        poll_response = urllib.request.urlopen(poll_req)
    except urllib.error.HTTPError as e:
        # Check if this is an authentication error from server
        if e.code == 401:
            try:
                error_data = json.loads(e.read().decode("utf-8"))
                if error_data.get("authentication_required"):
                    futil.log("entry.py::get_logic - Server indicates authentication required, stopping polling")
                    # If server says we need to authenticate, tell the user and stop polling
                    ui.messageBox("You need to log in again to use ForgeMind.", "Authentication Required", 0, 1)
                    # Reset local authentication state
                    login.was_logged_out = True
                    login.is_authenticated = False
                    # Stop polling
                    stop_polling()
                    return
            except:
                pass
                
        futil.log(f"entry.py::get_logic - Error in poll request: {e}")
        return
    except Exception as e:
        futil.log(f"entry.py::get_logic - General error in poll request: {e}")
        return

    if poll_response.getcode() != 200:
        futil.log("entry.py::get_logic - Non-200 status from poll request")
        return None

    poll_data = poll_response.read().decode("utf-8")
    poll_json = json.loads(poll_data)
    
    if not poll_json.get("status"):
        # futil.log("entry.py::get_logic - No instructions found when polling")
        return None
    
    futil.log(f"entry.py::get_logic - Polling message: {poll_json.get('message', '[NO MESSAGE]')}")
    
    # Call /get_instructions
    req = urllib.request.Request(
        f"{config.API_BASE_URL}/get_instructions",
        data=json_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        # Check if this is an authentication error
        if e.code == 401:
            try:
                error_data = json.loads(e.read().decode("utf-8"))
                if error_data.get("authentication_required"):
                    futil.log("entry.py::get_logic - Server indicates authentication required, stopping polling")
                    # If server says we need to authenticate, stop polling
                    stop_polling()
                    return
            except:
                pass
        futil.log(f"entry.py::get_logic - Error in get_instructions request: {e}")
        return
    except Exception as e:
        futil.log(f"entry.py::get_logic - General error in get_instructions request: {e}")
        return
        
    if response.getcode() != 200:
        futil.log(f"entry.py::get_logic - Backend returned status code {response.getcode()}")
        return
    
    response_data = response.read().decode("utf-8")
    json_data = json.loads(response_data)
    logic = json_data.get("instructions", None)
    chat_id = json_data.get("chat_id", None)  # Extract chat_id from response
    operation_id = json_data.get("operation_id", None)  # Extract operation_id for tracking
    
    if not logic:
        futil.log(f"entry.py::get_logic - get_instructions returned no logic {response.getcode()}")
        return

    futil.log(f"entry.py::get_logic - get_instructions returned logic for chat {chat_id}:\n\n[\n{logic}\n]")
    
    try:
        # Pass chat_id to run_logic to maintain chat context
        debug_log(f"Executing operation for chat_id={chat_id}, operation_id={operation_id}")
        
        # Save and compress screenshots before and after execution
        before_screenshot_path = save_and_compress_screenshot("workspace_screenshot_before")
        run_logic_result = run_logic(logic, chat_id)
        after_screenshot_path, compressed_after_screenshot_path = save_and_compress_screenshot("workspace_screenshot_after")
        
        # Add user_id and screenshots to result payload
        run_logic_result["user_id"] = login.get_user_id()
        run_logic_result["operation_id"] = operation_id  # Include operation_id in the result
        with open(before_screenshot_path, "rb") as before_img_file:
            run_logic_result["before_screenshot"] = before_img_file.read()
        with open(after_screenshot_path, "rb") as after_img_file:
            run_logic_result["after_screenshot"] = after_img_file.read()

        # Send run_logic_result to /instruction_result
        result_payload = json.dumps(run_logic_result).encode("utf-8")
        result_req = urllib.request.Request(
            f"{config.API_BASE_URL}/instruction_result",
            data=result_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            result_response = urllib.request.urlopen(result_req)
            if result_response.getcode() != 200:
                futil.log(f"entry.py::get_logic - Error sending result: {result_response.getcode()}")
        except Exception as e:
            futil.log(f"entry.py::get_logic - Error in result request: {e}")
        finally:
            delete_files(before_screenshot_path, after_screenshot_path)
    except Exception as e:
        futil.log(f"entry.py::get_logic - Error executing logic: {e}")
        # Send error result
        error_result = {
            "user_id": login.get_user_id(),
            "operation_id": operation_id,
            "status": "error",
            "message": str(e)
        }
        error_payload = json.dumps(error_result).encode("utf-8")
        error_req = urllib.request.Request(
            f"{config.API_BASE_URL}/instruction_result",
            data=error_payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            error_response = urllib.request.urlopen(error_req)
        except:
            pass
        finally:
            # Delete the screenshot files in case of error
            delete_files(before_screenshot_path, compressed_before_screenshot_path, after_screenshot_path, compressed_after_screenshot_path)

# Modified schedule_get_logic to check authentication before executing
def schedule_get_logic():
    global timer, is_timer_running
    if not is_timer_running:
        return
        
    # Check if user is authenticated before polling
    from ...commands.Login import entry as login
    if not login.is_user_authenticated():
        futil.log("entry.py::schedule_get_logic - User not authenticated, stopping polling")
        stop_polling()
        return
        
    # futil.log("entry.py::schedule_get_logic - Scheduling get_logic")
    get_logic()
    timer = threading.Timer(2, schedule_get_logic)
    timer.start()


# Add a function to stop polling
def stop_polling():
    global timer, is_timer_running
    if timer:
        futil.log("entry.py::stop_polling - Cancelling get_logic timer")
        timer.cancel()
        timer = None
    is_timer_running = False


# Modified start to only start polling if user is authenticated
def start():
    global timer, is_timer_running
    # ******************************** Create Command Definition ********************************
    futil.log("entry.py::start - FORGEMIND ADD IN BEING RUN - start")
    
    # Check if user is authenticated before starting polling
    from ...commands.Login import entry as login
    is_auth = login.is_user_authenticated()
    user_id = login.get_user_id()
    futil.log(f"entry.py::start - User authenticated: {is_auth}, User ID: {user_id or 'None'}")
    
    # Double-check authentication - make sure we have both authenticated flag AND user ID
    if not is_auth or not user_id:
        futil.log(f"entry.py::start - Authentication check failed: is_auth={is_auth}, user_id={user_id or 'None'}")
        # If either check fails, consider user not authenticated
        is_auth = False
        # Reset timer to ensure no polling occurs
        if timer:
            timer.cancel()
            timer = None
        is_timer_running = False

    # Prevent duplicate command definition error
    existing_cmd = ui.commandDefinitions.itemById(CMD_ID)
    if existing_cmd:
        existing_cmd.deleteMe()

    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
    )

    # Add command created handler. The function passed here will be executed when the command is executed.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******************************** Create Command Control ********************************
    # Get target workspace for the command.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get target toolbar tab for the command and create the tab if necessary.
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        toolbar_tab = workspace.toolbarTabs.add(TAB_ID, TAB_NAME)

    # Get target panel for the command and create the panel if necessary.
    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    # Before adding new control, delete an existing one if present.
    existing_control = panel.controls.itemById(CMD_ID)
    if existing_control:
        existing_control.deleteMe()

    # Create the command control, i.e. a button in the UI.
    control = panel.controls.addCommand(cmd_def)

    # Now you can set various options on the control such as promoting it to always be shown.
    control.isPromoted = IS_PROMOTED

    # Cancel any existing timer before potentially starting a new one
    if timer:
        futil.log("entry.py::start - Cancelling existing get_logic timer")
        timer.cancel()
        timer = None
        is_timer_running = False

    # Only start the timer if the user is authenticated
    if is_auth:
        # Verify authentication with backend before starting polling
        try:
            # Create a simple verification request to test if we can actually connect
            workspace_desc = {"user_id": user_id, "test_auth": True}
            json_payload = json.dumps(workspace_desc).encode("utf-8")
            
            test_req = urllib.request.Request(
                f"{config.API_BASE_URL}/poll",
                data=json_payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            try:
                test_response = urllib.request.urlopen(test_req)
                # If we got a 200 response, authentication is working
                if test_response.getcode() == 200:
                    futil.log("entry.py::start - Authentication verified with backend, starting polling")
                    # Now it's safe to start polling
                    start_polling()
                else:
                    futil.log(f"entry.py::start - Backend verification failed with status {test_response.getcode()}")
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    # Authentication issue - inform user and don't start polling
                    futil.log("entry.py::start - Backend rejected authentication, showing login prompt")
                    login.was_logged_out = True  # Force re-login
                    login.is_authenticated = False
                    ui.messageBox("Please login again to use ForgeMind.", "Authentication Required")
                else:
                    futil.log(f"entry.py::start - HTTP error while verifying auth: {e.code}")
            except Exception as e:
                futil.log(f"entry.py::start - Error verifying authentication: {str(e)}")
        except Exception as e:
            futil.log(f"entry.py::start - Failed to verify authentication: {str(e)}")
    else:
        futil.log("entry.py::start - Not starting polling because user is not authenticated")
        is_timer_running = False


# Executed when add-in is stopped.
def stop():
    global timer, is_timer_running
    # Cancel the recurring get_logic calls
    if timer:
        futil.log("entry.py::stop - Cancelling get_logic timer")
        timer.cancel()
        timer = None
        is_timer_running = False
    else:
        futil.log("entry.py::stop - No timer to cancel")

    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()

    # Delete the panel if it is empty
    if panel.controls.count == 0:
        panel.deleteMe()

    # Delete the tab if it is empty
    if toolbar_tab.toolbarPanels.count == 0:
        toolbar_tab.deleteMe()


# Function to be called when a user clicks the corresponding button in the UI
# Here you define the User Interface for your command and identify other command events to potentially handle
def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f"entry.py::command_created - {CMD_NAME} Command Created Event")

    # Connect to the events that are needed by this command.
    futil.add_handler(
        args.command.execute, command_execute, local_handlers=local_handlers
    )
    futil.add_handler(
        args.command.destroy, command_destroy, local_handlers=local_handlers
    )


# This function will be called when the user hits the OK button in the command dialog
def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"entry.py::command_execute - {CMD_NAME} Command Execute Event")
    # msg = f'Running that shit'
    # ui.messageBox(msg)


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f"entry.py::command_destroy - {CMD_NAME} Command Destroy Event")


# New helper function to start polling
def start_polling():
    global timer, is_timer_running
    if is_timer_running and timer:
        # Already polling, don't start again
        futil.log("entry.py::start_polling - Already polling, not starting again")
        return
        
    futil.log("entry.py::start_polling - Starting polling")
    is_timer_running = True
    get_logic()  # run immediately
    timer = threading.Timer(2, schedule_get_logic)
    timer.start()
    futil.log("entry.py::start_polling - Polling started successfully")
