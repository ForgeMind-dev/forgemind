import adsk.core, adsk.fusion, traceback
from adsk.core import Application, UserInterface
from ..lib import fusionAddInUtils as futil
from ..commands.Login import entry as login
import math
import json
import os
import re

app = adsk.core.Application.get()
ui = app.userInterface

# Global dictionary to track designs by chat_id
# Format: {chat_id: [{"name": "design_name", "creation_code": "python_code", "type": "cube|triangle|etc"}]}
chat_designs = {}

# Currently active chat_id
current_chat_id = None

# Debug logs
DEBUG = True

def debug_log(message):
    """Log debug messages if debug is enabled"""
    if DEBUG:
        futil.log(f"DEBUG: {message}")

def get_workspace_state():
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            futil.log("entry.py::get_workspace_description - No active Fusion 360 design")
            return None

        description = {"name": design.parentDocument.name, "components": []}

        for comp in design.allComponents:
            comp_info = {
                "name": comp.name,
                "bodies": [],
                "sketches": []
            }

            for body in comp.bRepBodies:
                body_info = {
                    "name": body.name,
                    "volume": body.volume,
                    "surface_area": body.area,
                    "bounding_box": {
                        "min_point": body.boundingBox.minPoint.asArray(),
                        "max_point": body.boundingBox.maxPoint.asArray()
                    }
                }
                comp_info["bodies"].append(body_info)

            for sketch in comp.sketches:
                sketch_info = {
                    "name": sketch.name,
                    "profiles": []
                }

                for profile in sketch.profiles:
                    profile_info = {
                        "area": profile.areaProperties().area,
                        "perimeter": profile.areaProperties().perimeter
                    }
                    sketch_info["profiles"].append(profile_info)

                comp_info["sketches"].append(sketch_info)

            description["components"].append(comp_info)

        # Get the authenticated user's ID
        user_id = login.get_user_id()
        
        # Use the authenticated user's ID if available, otherwise use a default
        return {"cad_state": description, "user_id": user_id or 'anonymous'}
    except Exception as error:
        futil.log('Error in get_workspace_state: ' + str(error))
        return None

def set_active_chat(chat_id):
    """
    Set the active chat context, loading any existing designs for this chat
    and clearing the workspace if switching chats
    """
    global current_chat_id, chat_designs
    
    # If this is the same chat, nothing to do
    if chat_id == current_chat_id:
        debug_log(f"Already in chat {chat_id}, no context switch needed")
        return
    
    debug_log(f"set_active_chat called with chat_id={chat_id}, current_chat_id={current_chat_id}")
    
    # If we're switching from one chat to another
    if current_chat_id is not None and current_chat_id != chat_id:
        futil.log(f"Switching from chat {current_chat_id} to chat {chat_id}")
        
        # Save the current chat's designs before switching
        if len(chat_designs.get(current_chat_id, [])) > 0:
            debug_log(f"Saving {len(chat_designs[current_chat_id])} designs for chat {current_chat_id}")
        
        # Clear the workspace for the new chat (safer version)
        debug_log("Performing workspace clear")
        clear_workspace()
    
    # Make sure we have an entry for this chat
    if chat_id not in chat_designs:
        chat_designs[chat_id] = []
        debug_log(f"Created new design tracking for chat {chat_id}")
    
    # Ensure we have a document to work with
    create_new_document_safely()
    
    # Update the global current chat ID
    current_chat_id = chat_id

def full_clear_workspace():
    """
    Performs a conservative but thorough workspace clear by deleting all
    objects in the current design without attempting to close or create documents.
    
    Returns True if successful, False if any errors occur
    """
    try:
        futil.log("Performing workspace clear")
        app = adsk.core.Application.get()
        
        # Get the active product
        product = app.activeProduct
        if not product:
            futil.log("No active product found")
            return False
            
        # Get the design
        design = adsk.fusion.Design.cast(product)
        if not design:
            futil.log("No active design found")
            return False
            
        # Get the root component
        rootComp = design.rootComponent
        if not rootComp:
            futil.log("No root component found")
            return False
        
        # APPROACH 1: Try using the undo API to get back to a clean state
        try:
            # Attempt to undo operations to clear the design
            undoCount = 0
            while app.activeDocument.canUndo and undoCount < 20:  # Limit to 20 undos to prevent infinite loops
                app.activeDocument.undo()
                undoCount += 1
                
            if undoCount > 0:
                futil.log(f"Performed {undoCount} undo operations")
        except Exception as e:
            futil.log(f"Error using undo: {str(e)}")
        
        # APPROACH 2: Methodically delete all objects
        try:
            # Delete all bodies
            bodies = rootComp.bRepBodies
            bodiesDeleted = 0
            
            # We need to be careful to handle the changing collection size
            while bodies.count > 0:
                try:
                    body = bodies.item(0)  # Always get the first body
                    body.deleteMe()
                    bodiesDeleted += 1
                except Exception as inner_e:
                    futil.log(f"Error deleting body: {str(inner_e)}")
                    # If we can't delete this body, move to the next one to avoid an infinite loop
                    if bodies.count > 1:
                        try:
                            # Try the second body instead
                            body = bodies.item(1)
                            body.deleteMe()
                            bodiesDeleted += 1
                        except:
                            # If we can't delete any bodies, break out
                            break
                    else:
                        # If there's only one body and we can't delete it, break out
                        break
            
            futil.log(f"Deleted {bodiesDeleted} bodies")
            
            # Delete all sketches
            sketches = rootComp.sketches
            sketchesDeleted = 0
            
            while sketches.count > 0:
                try:
                    sketch = sketches.item(0)  # Always get the first sketch
                    sketch.deleteMe()
                    sketchesDeleted += 1
                except Exception as inner_e:
                    futil.log(f"Error deleting sketch: {str(inner_e)}")
                    # If we can't delete this sketch, try to move on or break
                    if sketches.count > 1:
                        try:
                            sketch = sketches.item(1)
                            sketch.deleteMe()
                            sketchesDeleted += 1
                        except:
                            break
                    else:
                        break
            
            futil.log(f"Deleted {sketchesDeleted} sketches")
            
            # Delete all occurrences
            occs = rootComp.occurrences
            occsDeleted = 0
            
            while occs.count > 0:
                try:
                    occ = occs.item(0)  # Always get the first occurrence
                    occ.deleteMe()
                    occsDeleted += 1
                except Exception as inner_e:
                    futil.log(f"Error deleting occurrence: {str(inner_e)}")
                    # If we can't delete this occurrence, try to move on or break
                    if occs.count > 1:
                        try:
                            occ = occs.item(1)
                            occ.deleteMe()
                            occsDeleted += 1
                        except:
                            break
                    else:
                        break
            
            futil.log(f"Deleted {occsDeleted} occurrences")
            
            # Check if anything remains
            remainingBodies = rootComp.bRepBodies.count
            remainingOccs = rootComp.occurrences.count
            remainingSketches = rootComp.sketches.count
            
            futil.log(f"Remaining after cleanup: {remainingBodies} bodies, {remainingOccs} occurrences, {remainingSketches} sketches")
            
        except Exception as e:
            futil.log(f"Error during cleanup: {str(e)}")
        
        return True
    except Exception as e:
        futil.log(f"Critical error in workspace clear: {str(e)}")
        return False

def create_new_document_safely():
    """
    Creates a new empty document in a safe way that won't crash Fusion 360.
    Returns True if successful, False otherwise.
    """
    try:
        app = adsk.core.Application.get()
        
        # First check if a document already exists
        if app.documents.count == 0:
            futil.log("No documents exist, creating a new document")
            
            # Create a new document
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            if not doc:
                futil.log("Failed to create new document")
                return False
                
            futil.log("New document created successfully")
            return True
        else:
            # A document already exists
            futil.log("Document already exists, not creating a new one")
            return True
    except Exception as e:
        futil.log(f"Error creating new document: {str(e)}")
        return False

def clear_workspace():
    """
    Simple wrapper around full_clear_workspace that includes
    proper error handling and logging.
    """
    try:
        result = full_clear_workspace()
        if result:
            futil.log("Workspace cleared successfully")
        else:
            futil.log("Warning: Failed to clear workspace")
        return result
    except Exception as e:
        futil.log(f"Error in clear_workspace: {str(e)}")
        return False

def is_delete_operation(instruction):
    """Determine if the instruction is asking to delete or clear something"""
    # Convert the instruction to lowercase for case-insensitive matching
    instruction_lower = instruction.lower()
    
    # Simple exact matches for very basic commands
    if instruction_lower.strip() in ["delete all", "clear all", "delete", "clear"]:
        debug_log(f"Detected simple delete command: {instruction_lower}")
        return True
    
    # Check for common delete/clear/remove phrases
    delete_patterns = [
        r'delete all',
        r'clear all',
        r'remove all',
        r'delete the (\w+)',
        r'clear the (\w+)',
        r'remove the (\w+)',
        r'delete everything',
        r'clear everything',
        r'erase everything',
        r'\bdelete\b',  # The word "delete" as a standalone word
        r'\bclear\b',   # The word "clear" as a standalone word
        r'\bremove\b'   # The word "remove" as a standalone word
    ]
    
    # Check each pattern
    for pattern in delete_patterns:
        if re.search(pattern, instruction_lower):
            debug_log(f"Detected delete operation with pattern: {pattern}")
            return True
    
    return False

def identify_delete_targets(instruction):
    """Identify what specifically needs to be deleted"""
    instruction_lower = instruction.lower()
    
    # Check if this is a "delete all" type instruction
    if any(x in instruction_lower for x in ['delete all', 'clear all', 'remove all', 'delete everything']):
        debug_log("Identified 'delete all' operation")
        return 'all'
    
    # Try to extract specific objects to delete
    targets = []
    patterns = [
        (r'delete the (\w+)', 1),
        (r'clear the (\w+)', 1),
        (r'remove the (\w+)', 1)
    ]
    
    for pattern, group in patterns:
        matches = re.finditer(pattern, instruction_lower)
        for match in matches:
            if match.group(group):
                targets.append(match.group(group))
    
    debug_log(f"Identified delete targets: {targets}")
    return targets if targets else 'all'

def extract_design_type(code):
    """Try to determine what type of design is being created"""
    code_lower = code.lower()
    
    # Check for common design types
    if 'cube' in code_lower or 'box' in code_lower:
        return 'cube'
    elif 'triangle' in code_lower:
        return 'triangle'
    elif 'circle' in code_lower or 'sphere' in code_lower:
        return 'circle'
    elif 'square' in code_lower:
        return 'square'
    elif 'text' in code_lower:
        return 'text'
    else:
        return 'unknown'

def extract_user_intent(instruction):
    """
    Try to extract the original user intent from a complex AI response
    This helps with commands like "delete all" that might be wrapped in explanatory text
    """
    # Look for common patterns indicating what the user asked for
    intent_patterns = [
        r'user requested to "(.*?)"',
        r'user asked to "(.*?)"',
        r'user wants to "(.*?)"',
        r'command to "(.*?)"',
        r'instructed to "(.*?)"',
        r"user requested to '(.*?)'",
        r"user asked to '(.*?)'",
        r"user wants to '(.*?)'"
    ]
    
    instruction_lower = instruction.lower()
    
    # Check each pattern
    for pattern in intent_patterns:
        match = re.search(pattern, instruction_lower)
        if match:
            return match.group(1)
    
    # Also check the first line, which often contains the core instruction
    lines = instruction.strip().split('\n')
    if lines and len(lines[0]) < 100:  # Only consider short first lines
        return lines[0]
    
    return None

def basic_code_validation(code):
    """
    Perform basic validation of code before execution to catch common issues
    Returns (is_valid, error_message)
    """
    # Check for known problematic patterns
    if '.remove(' in code:
        return False, "Error: '.remove()' method is not supported in Fusion 360. Use '.deleteMe()' instead."
    
    # Try to compile the code to catch syntax errors
    try:
        compile(code, '<string>', 'exec')
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error in code: {str(e)}"
    except Exception as e:
        return False, f"Error validating code: {str(e)}"

def exec_with_safety(code_block):
    """Execute code with extra safety checks"""
    # First validate the code
    is_valid, error_message = basic_code_validation(code_block)
    if not is_valid:
        futil.log(f"Code validation failed: {error_message}")
        
        # Fix common issues if possible
        fixed_code = code_block
        if '.remove(' in code_block:
            fixed_code = code_block.replace('.remove(', '.deleteMe(')
            futil.log(f"Attempting to fix code by replacing .remove() with .deleteMe()")
            
            # Try to validate the fixed code
            is_valid, _ = basic_code_validation(fixed_code)
            if is_valid:
                futil.log("Fixed code passes validation, executing fixed version")
                exec(fixed_code)
                return True
        
        # If we couldn't fix it or the fix didn't pass validation
        raise Exception(error_message)
    
    # If validation passed, execute the code
    exec(code_block)
    return True

def filter_historical_code_blocks(code_blocks):
    """
    Detect and filter out code blocks that appear to be historical or duplicated.
    This helps prevent re-executing code from previous conversations that the AI
    might include in its responses.
    
    Returns a list of filtered code blocks with duplicates removed.
    """
    if len(code_blocks) <= 1:
        return code_blocks
        
    # Look for duplicate or near-duplicate code blocks
    unique_blocks = []
    block_signatures = set()
    
    for block in code_blocks:
        # Create a signature by taking first 50 chars + last 50 chars + length
        # This helps identify similar blocks without exact matching
        if len(block) <= 100:
            signature = block
        else:
            signature = block[:50] + block[-50:] + str(len(block))
            
        # Also add function/class names as part of signature
        function_matches = re.findall(r'def\s+(\w+)', block)
        class_matches = re.findall(r'class\s+(\w+)', block)
        for match in function_matches + class_matches:
            signature += match
            
        # Check if we've seen a block with this signature
        if signature not in block_signatures:
            block_signatures.add(signature)
            unique_blocks.append(block)
            futil.log(f"Including unique code block ({len(block)} chars)")
        else:
            futil.log(f"Filtering out duplicate/historical code block ({len(block)} chars)")
            
    futil.log(f"Filtered {len(code_blocks) - len(unique_blocks)} duplicate/historical blocks, keeping {len(unique_blocks)}")
    return unique_blocks

def find_primary_code_block(code_blocks, instruction_text):
    """
    When multiple code blocks are present, determine which is the primary one to execute
    based on its position and relevance to the current instruction.
    
    Returns the index of the most relevant code block.
    """
    # If there's only one code block, it's the primary one
    if len(code_blocks) <= 1:
        return 0
    
    futil.log(f"Multiple code blocks found ({len(code_blocks)}), determining primary block...")
    
    # The basic rule: the FIRST code block in the message is usually the one we want
    # This is because AI often includes examples or prior conversation content after the main response
    
    # However, sometimes the AI might generate multiple valid code blocks in one response
    # For example, creating multiple shapes. In that case, we should run them all.
    
    # Check if the instruction contains phrases indicating we should run all blocks
    run_all_indicators = [
        "multiple shapes",
        "multiple objects",
        "several designs",
        "create both",
        "create all",
        "all of these"
    ]
    
    for indicator in run_all_indicators:
        if indicator.lower() in instruction_text.lower():
            futil.log(f"Detected '{indicator}' in instruction, will run all code blocks")
            return -1  # Special value indicating run all blocks
    
    # By default, just run the first code block as it's most likely the current response
    futil.log("Using first code block as primary (ignoring potential historical blocks)")
    return 0

def run_logic(logic: str, chat_id=None) -> dict:
    global current_chat_id
    
    try:
        futil.log('Running logic')
        debug_log('=== INSTRUCTION RECEIVED ===')
        debug_log(logic)
        debug_log('===========================')
        
        # If a chat_id is provided, update the active chat context
        if chat_id:
            # Always fully set the active chat when a specific chat_id is provided
            # This ensures we're in the correct context for this operation
            set_active_chat(chat_id)
            current_chat_id = chat_id
            debug_log(f"Updated current_chat_id to {current_chat_id}")
        else:
            futil.log("Warning: No chat_id provided for this operation")
        
        # Initialize chat designs array if not yet created for this chat
        if current_chat_id and current_chat_id not in chat_designs:
            chat_designs[current_chat_id] = []
            debug_log(f"Initialized empty chat_designs for {current_chat_id}")
        
        # ============ FIRST-PASS INTENT DETECTION =============
        # Check if this is a direct delete operation or contains delete keywords
        
        # 1. Convert to lowercase for easier matching
        logic_lower = logic.lower()
        
        # 2. Check for direct delete commands in various forms
        is_delete_request = False
        is_design_request = False
        
        # Common delete patterns
        delete_keywords = [
            "delete all", 
            "clear all", 
            "delete the", 
            "clear the", 
            "remove all",
            "erase everything"
        ]
        
        # Design patterns
        design_keywords = [
            "design", 
            "create", 
            "make", 
            "draw", 
            "build"
        ]
        
        # Check if this appears to be a delete operation
        for keyword in delete_keywords:
            if keyword in logic_lower:
                is_delete_request = True
                debug_log(f"Direct delete command detected: '{keyword}'")
                break
        
        # Check if this appears to be a design operation
        for keyword in design_keywords:
            if keyword in logic_lower:
                is_design_request = True
                break
        
        # Special case: If this is ONLY a delete request and nothing else
        if is_delete_request and not is_design_request:
            debug_log("============================================")
            debug_log("HANDLING PURE DELETE REQUEST")
            debug_log("============================================")
            
            # Clear workspace (using the safer method)
            futil.log("Performing workspace clearing for delete command")
            result = full_clear_workspace()
            
            if result:
                futil.log("Workspace cleared successfully")
            else:
                futil.log("Warning: Failed to clear workspace")
            
            # Reset the design tracking for this chat
            if current_chat_id and current_chat_id in chat_designs:
                chat_designs[current_chat_id] = []
                debug_log(f"Reset chat_designs for {current_chat_id}")
            
            # Return immediately - DO NOT process any code blocks
            return {
                **get_workspace_state(),
                'status': 'success',
                'message': 'Delete operation completed successfully'
            }
        
        # If this is a delete+design operation, handle the delete part first
        if is_delete_request and is_design_request:
            debug_log("============================================")
            debug_log("HANDLING COMBINED DELETE+DESIGN REQUEST")
            debug_log("============================================")
            
            # Perform workspace clearing
            futil.log("Clearing workspace before new design")
            result = full_clear_workspace()
            
            if result:
                futil.log("Workspace cleared successfully before creating new design")
            else:
                futil.log("Warning: Failed to clear workspace before creating new design")
            
            # Reset the design tracking for this chat
            if current_chat_id and current_chat_id in chat_designs:
                chat_designs[current_chat_id] = []
                debug_log(f"Reset chat_designs for {current_chat_id}")
        
        # Extract Python code from markdown
        code_to_execute = ""
        in_code_block = False
        python_code_blocks = []
        
        # Split the content by lines to process line by line
        for line in logic.split('\n'):
            # Check for the start of a Python code block
            if line.strip().startswith('```python'):
                in_code_block = True
                continue  # Skip the ```python line
            # Check for the end of a code block
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                python_code_blocks.append(code_to_execute)
                code_to_execute = ""  # Reset for potential next code block
                continue  # Skip the ``` line
            # If we're inside a code block, add the line to our code
            elif in_code_block:
                code_to_execute += line + '\n'
        
        debug_log(f"Extracted {len(python_code_blocks)} Python code blocks")
        
        # NEW: Filter out historical/duplicate code blocks
        python_code_blocks = filter_historical_code_blocks(python_code_blocks)
        
        # If this is a design request with code blocks, execute them
        executed_blocks = 0
        execution_errors = []
        
        if not is_delete_request or (is_delete_request and is_design_request):
            if python_code_blocks:
                # NEW: Determine which code blocks to execute
                primary_block_index = find_primary_code_block(python_code_blocks, logic)
                blocks_to_execute = []
                
                if primary_block_index == -1:
                    # Special case: execute all blocks
                    blocks_to_execute = list(range(len(python_code_blocks)))
                    futil.log(f"Will execute all {len(blocks_to_execute)} code blocks")
                else:
                    # Just execute the primary block
                    blocks_to_execute = [primary_block_index]
                    futil.log(f"Will execute only the primary code block ({primary_block_index + 1} of {len(python_code_blocks)})")
                
                # Only clear if this is a new design in a completely new chat session
                # Or if we're specifically asked to clear
                should_clear = is_delete_request
                
                # If we're in a new chat or there are no designs for this chat yet, we should clear
                if current_chat_id and (current_chat_id not in chat_designs or len(chat_designs[current_chat_id]) == 0):
                    should_clear = True
                    futil.log("No existing designs in this chat, will clear workspace")
                
                if should_clear:
                    futil.log("Clearing workspace before executing new design code")
                    full_clear_workspace()
                    
                    # Reset design tracking as we're starting fresh
                    if current_chat_id and current_chat_id in chat_designs:
                        chat_designs[current_chat_id] = []
                        debug_log(f"Reset chat_designs for {current_chat_id}")
                else:
                    futil.log("Keeping existing workspace state (not clearing)")
                
                for idx in blocks_to_execute:
                    code_block = python_code_blocks[idx]
                    futil.log(f"Executing code block {idx + 1} of {len(python_code_blocks)}")
                    
                    # Get a name for the design - use a simple naming scheme
                    design_type = extract_design_type(code_block)
                    design_count = 1
                    
                    # Find appropriate design number
                    if current_chat_id in chat_designs:
                        design_count = len(chat_designs[current_chat_id]) + 1
                    
                    design_name = f"{design_type}_{design_count}"
                    debug_log(f"Assigning name {design_name} for new design")
                    
                    # Execute the code with safety
                    try:
                        # Use the safer execution function
                        exec_with_safety(code_block)
                        executed_blocks += 1
                        
                        # Store the code with the current chat if we have a chat_id
                        if current_chat_id:
                            # Store the design code with the chat
                            chat_designs[current_chat_id].append({
                                "name": design_name,
                                "creation_code": code_block,
                                "type": design_type
                            })
                            
                            futil.log(f"Added design '{design_name}' to chat {current_chat_id}")
                            debug_log(f"Chat {current_chat_id} now has {len(chat_designs[current_chat_id])} designs")
                    except Exception as e:
                        error_msg = str(e)
                        futil.log(f"Error executing code block: {error_msg}")
                        execution_errors.append(error_msg)
                        # Continue with next block even if one fails
            else:
                # No code blocks found, but we need to handle the case anyway
                futil.log("No Python code blocks found in design request")
        
        # Return status based on what happened
        if is_delete_request and executed_blocks == 0:
            return {
                **get_workspace_state(),
                'status': 'success',
                'message': 'Delete operation completed successfully'
            }
        elif executed_blocks > 0:
            if len(execution_errors) > 0:
                return {
                    **get_workspace_state(),
                    'status': 'partial_success',
                    'message': f'Executed {executed_blocks} code blocks with {len(execution_errors)} errors',
                    'errors': execution_errors
                }
            else:
                return {
                    **get_workspace_state(),
                    'status': 'success',
                    'message': f'Successfully executed {executed_blocks} code blocks'
                }
        else:
            if len(execution_errors) > 0:
                return {
                    **get_workspace_state(),
                    'status': 'error',
                    'message': 'Failed to execute any code blocks',
                    'errors': execution_errors
                }
            else:
                return {
                    **get_workspace_state(),
                    'status': 'warning',
                    'message': 'No operations were performed'
                }
    except Exception as error:
        futil.log('Error: ' + str(error))
        return {
            'status': 'error',
            'message': str(error),
            **get_workspace_state()
        }