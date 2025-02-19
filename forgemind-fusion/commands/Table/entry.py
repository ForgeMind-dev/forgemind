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

import adsk.core
import os
from ...lib import fusionAddInUtils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}'
CMD_Description = 'Table Input Sample Command'
IS_PROMOTED = False

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

# Used to keep track of table rows
ROW_NUMBER = 1


# Executed when add-in is run.
def start():
    # ******************************** Create Command Definition ********************************
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


# Function to be called when a user clicks the corresponding button in the UI.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{CMD_NAME} Command Created Event')
    global ROW_NUMBER
    ROW_NUMBER = 1

    # Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

    inputs = args.command.commandInputs

    # Create table input
    table_input = inputs.addTableCommandInput('table', 'Table', 4, '1:2:3:1')
    add_header_row_to_table(table_input)
    add_row_to_table(table_input)
    add_row_to_table(table_input)

    # Add rows to the table.
    add_button_input = inputs.addBoolValueInput('table_add', 'Add', False, '', True)
    table_input.addToolbarCommandInput(add_button_input)

    # Delete rows from table
    delete_button_input = inputs.addBoolValueInput('table_delete', 'Delete', False, '', True)
    table_input.addToolbarCommandInput(delete_button_input)


# This function will be called when the user changes anything in the command dialog.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.input.parentCommand.commandInputs
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')

    table_input = inputs.itemById('table')

    if changed_input.id == 'table_add':
        add_row_to_table(table_input)

    elif changed_input.id == 'table_delete':
        if table_input.selectedRow == -1:
            ui.messageBox('Select one row to delete.')
        else:
            table_input.deleteRow(table_input.selectedRow)


# This function will be called when the user clicks the OK button in the command dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Execute Event')

    inputs = args.command.commandInputs
    table_input: adsk.core.TableCommandInput = inputs.itemById('table')
    num_rows = table_input.rowCount
    string_values = []

    # Get the value of the String Input for all rows below the header (skip first row)
    for row_number in range(1, num_rows):
        string_input: adsk.core.StringValueCommandInput = table_input.getInputAtPosition(row_number, 2)
        string_values.append(string_input.value)

    msg = f'The Table had {num_rows-1} rows plus the header.<br>The String Values were:<br>{"<br>".join(string_values)}'
    ui.messageBox(msg)


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f'{CMD_NAME} Command Destroy Event')


# Adds a new row to the table.
def add_row_to_table(table_input: adsk.core.TableCommandInput):
    global ROW_NUMBER
    # Get the CommandInputs object associated with the parent command.
    inputs = adsk.core.CommandInputs.cast(table_input.commandInputs)

    # Create new command inputs.
    row_name = f'<b>Item {ROW_NUMBER}</b>'
    text_input = inputs.addTextBoxCommandInput(f'text_input_{ROW_NUMBER}', '', row_name, 1, True)

    initial_value = adsk.core.ValueInput.createByReal(ROW_NUMBER)
    value_input = inputs.addValueInput(f'value_input_{ROW_NUMBER}', 'Value', 'cm', initial_value)

    initial_string = f'String {ROW_NUMBER}'
    string_input = inputs.addStringValueInput(f'string_input_{ROW_NUMBER}', 'String', initial_string)

    spinner_input = inputs.addIntegerSpinnerCommandInput(f'spinner_input_{ROW_NUMBER}', 'Int', 0, 100, 2, ROW_NUMBER)

    # Add the inputs to the table.
    row = table_input.rowCount
    table_input.addCommandInput(text_input, row, 0, 0, 0)
    table_input.addCommandInput(value_input, row, 1, 0, 0)
    table_input.addCommandInput(string_input, row, 2, 0, 0)
    table_input.addCommandInput(spinner_input, row, 3, 0, 0)

    # Increment a counter used to make each row unique.
    ROW_NUMBER = ROW_NUMBER + 1

    if table_input.rowCount > table_input.maximumVisibleRows:
        table_input.maximumVisibleRows = table_input.rowCount


# Adds a header row to the table.
def add_header_row_to_table(table_input: adsk.core.TableCommandInput):
    inputs = adsk.core.CommandInputs.cast(table_input.commandInputs)
    column_names = ['Name', 'Value', 'String', 'Integer']

    for i in range(len(column_names)):
        column_name = f'<b>{column_names[i]}</b>'
        text_input = inputs.addTextBoxCommandInput(f'header_{i}', '', column_name, 1, True)
        table_input.addCommandInput(text_input, 0, i)
