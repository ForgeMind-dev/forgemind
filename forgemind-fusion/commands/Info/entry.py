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
from ...logic import run_logic
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


def get_workspace_description():
    design = adsk.fusion.Design.cast(app.activeProduct)

    if not design:
        futil.log("entry.py::get_workspace_description - No active Fusion 360 design")
        return None

    description = {"name": design.parentDocument.name, "components": []}

    for comp in design.allComponents:
        comp_info = {
            "name": comp.name,
            "bodies": [body.name for body in comp.bRepBodies],
            "sketches": [sketch.name for sketch in comp.sketches],
        }
        description["components"].append(comp_info)

    return {"cad_state": description}


def get_logic():
    # Get workspace description
    workspace_desc = get_workspace_description()
    json_payload = json.dumps(workspace_desc).encode("utf-8")

    # Call /poll first with workspace description
    poll_req = urllib.request.Request(
        "http://127.0.0.1:5000/poll",
        data=json_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        poll_response = urllib.request.urlopen(poll_req)
    except Exception as e:
        futil.log(f"entry.py::get_logic - Error in poll request: {e}")
        return

    if poll_response.getcode() != 200:
        futil.log("entry.py::get_logic - Non-200 status from poll request")
        return None

    poll_data = poll_response.read().decode("utf-8")
    if not json.loads(poll_data).get("status"):
        futil.log("entry.py::get_logic - No instructions found when polling")
        return None
    
    futil.log(f"entry.py::get_logic - Polling message: {json.loads(poll_data).get('message', '[NO MESSAGE]')}")
    # Call /get_instructions
    req = urllib.request.Request(
        "http://127.0.0.1:5000/get_instructions",
        data=json_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    response = urllib.request.urlopen(req)
    if response.getcode() != 200:
        futil.log(f"entry.py::get_logic - Backend returned status code {response.getcode()}")
        return
    
    response_data = response.read().decode("utf-8")
    json_data = json.loads(response_data)
    logic = json_data.get("instructions", None)
    if not logic:
        futil.log(f"entry.py::get_logic - get_instructions returned no logic {response.getcode()}")
        return

    futil.log(f"entry.py::get_logic - get_instructions returned logic:\n\n[\n{logic}\n]")
    run_logic(logic)


# New function to run get_logic every 10 seconds.
def schedule_get_logic():
    futil.log("entry.py::schedule_get_logic - Scheduling get_logic")
    get_logic()
    threading.Timer(1, schedule_get_logic).start()


# Executed when add-in is run.
def start():
    # ******************************** Create Command Definition ********************************
    futil.log("entry.py::start - FORGEMIND ADD IN BEING RUN - start")

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

    # Start the recurring get_logic calls every 10 seconds.
    threading.Timer(0, schedule_get_logic).start()


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
