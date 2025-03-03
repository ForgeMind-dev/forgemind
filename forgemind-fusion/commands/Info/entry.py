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
import adsk.core
import os
from ... import config
from ...logic import run_logic
from ...lib import fusionAddInUtils as futil
import threading
import urllib.request
from ..Login import entry as login
from ...lib import auth_config

app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}'
CMD_Description = 'ForgeMind AI'
IS_PROMOTED = True

# Global variables by referencing values from /config.py
WORKSPACE_ID = config.design_workspace
TAB_ID = config.tools_tab_id
TAB_NAME = config.my_tab_name

PANEL_ID = config.my_panel_id
PANEL_NAME = config.my_panel_name
PANEL_AFTER = config.my_panel_after

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Holds references to event handlers
local_handlers = []

# Global flag to control polling
polling_active = False


# Executed when add-in is run.
def start():
    # ******************************** Create Command Definition ********************************
    futil.log('[4] FORGEMIND ADD IN BEING RUN - start')
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Add command created handler. The function passed here will be executed when the command is executed.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******************************** Create Command Control ********************************
    # Get target workspace for the command.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get target toolbar tab for the command and create the tab if necessary.
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        toolbar_tab = workspace.toolbarTabs.add(TAB_ID, TAB_NAME)

    # Get target panel for the command and and create the panel if necessary.
    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    # Create the command control, i.e. a button in the UI.
    control = panel.controls.addCommand(cmd_def)

    # Now you can set various options on the control such as promoting it to always be shown.
    control.isPromoted = IS_PROMOTED
    
    # Comment out automatic execution to prevent premature polling
    # cmd_def.execute()
    # futil.log('Info command executed - polling should start')


# Executed when add-in is stopped.
def stop():
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
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug
    futil.log(f'{CMD_NAME} Command Created Event')
    
    global polling_active
    
    # First check if user is logged in before starting polling
    try:
        # Check if the login module indicates we're logged in
        is_logged_in = login.get_login_status()
        if not is_logged_in:
            futil.log("User not logged in - not starting polling")
            return
    except Exception as e:
        # If any error occurs checking login status, log it but continue
        futil.log(f"Error checking login status: {str(e)}")
        
    # Mark polling as active
    polling_active = True

    def get_logic():
        while polling_active:  # Use flag to control polling
            try:
                # Use the Supabase backend URL instead of localhost
                backend_url = auth_config.BACKEND_URL
                poll_url = f"{backend_url}/poll"
                
                futil.log(f"Polling for commands at: {poll_url}")
                
                # Get the auth token to include in the request
                auth_token = auth_config.get_auth_token()
                
                # Create a request with the authorization header
                req = urllib.request.Request(poll_url)
                if auth_token:
                    req.add_header('Authorization', f'Bearer {auth_token}')
                req.add_header('Content-Type', 'application/json')
                req.add_header('X-Client-Info', 'forgemind-fusion')
                
                # Make the authenticated request
                response = urllib.request.urlopen(req)
                
                if response.getcode() == 200:
                    logic = response.read().decode('utf-8')
                    futil.log('Running logic: ' + logic)
                    run_logic(logic)
                else:
                    futil.log(f'Poll request returned status code {response.getcode()}')
            except urllib.error.URLError as e:
                futil.log(f'Error polling {poll_url}: {e}')
            except Exception as e:
                futil.log(f'Unexpected error during polling: {str(e)}')
            
            # Wait before next poll
            time.sleep(3)  # Poll every 3 seconds to reduce load

    # Start polling in a separate thread
    polling_thread = threading.Thread(target=get_logic, daemon=True)
    polling_thread.start()
    futil.log('Started polling thread')

    # Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This function will be called when the user hits the OK button in the command dialog
def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f"entry.py::command_execute - {CMD_NAME} Command Execute Event")
    
    # Get backend URL for display
    backend_url = auth_config.SUPABASE_URL
    poll_url = f"{backend_url}/poll"
    
    # Log polling information
    futil.log(f"Polling is now active - checking for commands at {poll_url}")
    
    # Show a minimal message indicating polling is active
    ui.messageBox(f"ForgeMind Add-in is connected and polling for commands.\n\nBackend URL: {backend_url}", "ForgeMind Status")


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers, polling_active
    local_handlers = []
    
    # Stop the polling thread
    polling_active = False
    futil.log('Stopping polling thread')
    
    futil.log(f'{CMD_NAME} Command Destroy Event')
