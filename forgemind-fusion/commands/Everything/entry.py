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

import math

import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = os.path.basename(os.path.dirname(__file__))
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}'
CMD_Description = 'Various Command Inputs Sample Command'
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

    # Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

    button_icons = os.path.join(ICON_FOLDER, 'buttons')
    inputs = args.command.commandInputs

    initial_value_dist = adsk.core.ValueInput.createByString('0.0 cm')
    initial_value_angle = adsk.core.ValueInput.createByString('0.0 rad')

    origin_point = adsk.core.Point3D.create(0, 0, 0)
    x_vector = adsk.core.Vector3D.create(1, 0, 0)
    y_vector = adsk.core.Vector3D.create(0, 1, 0)
    z_vector = adsk.core.Vector3D.create(0, 0, 1)

    angle_value_input = inputs.addAngleValueCommandInput('angle_value_input', 'Angle Value', initial_value_angle)
    angle_value_input.isMinimumValueInclusive = True
    angle_value_input.isMaximumValueInclusive = False
    angle_value_input.maximumValue = 2 * math.pi
    # angle_value_input.minimumValue = 0
    angle_value_input.setManipulator(origin_point, x_vector, z_vector)

    bool_value_input = inputs.addBoolValueInput('bool_value_input', 'Bool Value', True, '', False)
    bool_value_input.tooltip = "Could be either a button or a check box"

    button_row_input = inputs.addButtonRowCommandInput('button_row_input', 'Button Row', False)
    button_row_input_list_items = button_row_input.listItems
    button_row_input_list_items.add('Button Row ListItem 1', False, button_icons)
    button_row_input_list_items.add('Button Row ListItem 2', True, button_icons)
    button_row_input_list_items.add('Button Row ListItem 3', False, button_icons)

    direction_input_1 = inputs.addDirectionCommandInput('direction_input_1', 'Direction 1')
    direction_input_1.setManipulator(origin_point, x_vector)

    direction_input_2 = inputs.addDirectionCommandInput('direction_input_2', 'Direction 2', button_icons)
    direction_input_2.setManipulator(origin_point, y_vector)

    distance_input = inputs.addDistanceValueCommandInput('distance_input', 'Distance', initial_value_dist)
    distance_input.isEnabled = False
    distance_input.isVisible = False
    distance_input.minimumValue = 0.0
    distance_input.maximumValue = 10.0

    drop_down_style = adsk.core.DropDownStyles.LabeledIconDropDownStyle
    drop_down_input = inputs.addDropDownCommandInput('drop_down_input', 'Drop Down 1', drop_down_style)
    drop_down_items = drop_down_input.listItems
    drop_down_items.add('Drop Down ListItem 1', True)
    drop_down_items.add('Drop Down  2', False)
    drop_down_items.add('Drop Down  3', False)

    radio_input = inputs.addRadioButtonGroupCommandInput('radio_input', 'Radio Group')
    radio_items = radio_input.listItems
    radio_items.add('Radio ListItem 1', True)
    radio_items.add('Radio ListItem 2', False)
    radio_items.add('Radio ListItem 3', False)
    radio_input.isFullWidth = True

    selection_input = inputs.addSelectionInput('selection_input', 'Selection', 'Select a Plane')
    selection_input.addSelectionFilter('PlanarFaces')
    selection_input.addSelectionFilter('ConstructionPlanes')
    selection_input.setSelectionLimits(1, 1)

    string_value_input = inputs.addStringValueInput('string_value_input', 'String Value', 'Click Boolean to change me')
    string_value_input.isPassword = False

    text_box_message = "This is a <b>Text Box</b> Message.<br>You can use <i>basic</i> HTML formatting."
    text_box_input = inputs.addTextBoxCommandInput('text_box_input', 'Text Box', text_box_message, 2, True)
    text_box_input.isFullWidth = True

    value_input = inputs.addValueInput('value_input', 'Value', 'cm', initial_value_dist)

    group_input = inputs.addGroupCommandInput('group_input', 'Additional Value Inputs')
    group_input.isExpanded = False
    children = group_input.children

    float_slider_input = children.addFloatSliderCommandInput('float_slider_input', 'Float Slider', 'cm', 0, 10, False)

    floats = [0, .25, .5, 1.25, 2.5, 3.25, 3.75, 4.0, 4.25, 5.0]
    float_list_input = children.addFloatSliderListCommandInput('float_list_input', 'Float List', 'cm', floats, True)
    float_list_input.setText('Start', 'End')

    float_spinner_input = children.addFloatSpinnerCommandInput('float_spinner', 'Float Spinner', 'cm', 0, 6.5, .25, 0)

    int_slider_input = children.addIntegerSliderCommandInput('int_slider_input', 'Integer Slider', 0, 10, False)

    ints = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    int_list_input = children.addIntegerSliderListCommandInput('int_list_input', 'Integer List', ints, True)
    int_list_input.setText('Start', 'End')

    int_spinner_input = children.addIntegerSpinnerCommandInput('int_spinner', 'Integer Spinner', 0, 10, 1, 0)


# This function will be called when the user clicks the OK button in the command dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Execute Event')
    inputs = args.command.commandInputs

    # Display the palette that represents the TEXT COMMANDS palette
    text_palette = ui.palettes.itemById('TextCommands')
    if not text_palette.isVisible:
        text_palette.isVisible = True

    # Prints info about all the commands to the text commands palette
    log_command_inputs(inputs)

    ui.messageBox("See command summary logs in the Text Commands palette")


# This function will be called when the user changes anything in the command dialog.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.input.parentCommand.commandInputs
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')

    # Get a reference to your command's inputs
    selection_input: adsk.core.SelectionCommandInput = inputs.itemById('selection_input')
    distance_input: adsk.core.DistanceValueCommandInput = inputs.itemById('distance_input')
    bool_value_input: adsk.core.BoolValueCommandInput = inputs.itemById('bool_value_input')
    string_value_input: adsk.core.StringValueCommandInput = inputs.itemById('string_value_input')

    # Show and update the distance input when a plane is selected
    if changed_input.id == selection_input.id:
        if selection_input.selectionCount > 0:
            selection = selection_input.selection(0)
            selection_point = selection.point
            selected_entity = selection.entity
            plane = selected_entity.geometry

            distance_input.setManipulator(selection_point, plane.normal)
            distance_input.expression = "10mm * 2"
            distance_input.isEnabled = True
            distance_input.isVisible = True
        else:
            distance_input.isEnabled = False
            distance_input.isVisible = False

    # Enable edit on the string value input when the boolean is selected
    elif changed_input.id == bool_value_input.id:
        if bool_value_input.value:
            string_value_input.value = 'The Bool Value is checked'
        else:
            string_value_input.value = 'The Bool Value is not checked'


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f'{CMD_NAME} Command Destroy Event')


def log_command_inputs(inputs):
    seperator = '\n***************************\n'
    futil.log(seperator)
    futil.log('Summary of Command Inputs')
    futil.log(seperator)

    for command_input in inputs:
        display_value = 'N/A'
        
        if hasattr(command_input, 'expression'):
            display_value = command_input.expression
        
        elif hasattr(command_input, 'value'):
            display_value = command_input.value
            
        elif hasattr(command_input, 'valueOne'):
            display_value = f'\n    Value 1: {command_input.valueOne}'
            if hasattr(command_input, 'valueTwo'):
                display_value += f'\n    Value 2: {command_input.valueTwo}'
        
        elif hasattr(command_input, 'listItems'):
            display_value = command_input.selectedItem.name
        
        elif hasattr(command_input, 'isDirectionFlipped'):
            display_value = f'{command_input.isDirectionFlipped} (Is Direction Flipped?)'
            
        elif command_input.objectType == adsk.core.SelectionCommandInput.classType():
            selection = command_input.selection(0)
            selected_entity = selection.entity
            if selected_entity.objectType == adsk.fusion.ConstructionPlane.classType():
                display_value = f'A Construction Plane named: {selected_entity.name}'
            elif selected_entity.objectType == adsk.fusion.BRepFace.classType():
                parent_component_name = selected_entity.body.parentComponent.name
                display_value = f'A planar face from {parent_component_name}'

        futil.log(f'Name: {command_input.name}')
        futil.log(f'Type: {type(command_input).__name__}')
        futil.log(f'Input ID: {command_input.id}')
        futil.log(f'User Input: {display_value}')
        futil.log(seperator)
