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
        active_product = app.activeProduct
        if not active_product:
            futil.log("entry.py::get_workspace_description - No active product")
            return None

        design = adsk.fusion.Design.cast(active_product)

        if not design:
            futil.log("entry.py::get_workspace_description - No active Fusion 360 design")
            return None

        # Ensure the document is valid
        if not design.parentDocument:
            futil.log("entry.py::get_workspace_description - Invalid document")
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



# def filter_historical_code_blocks(code_blocks):
#     """
#     Detect and filter out code blocks that appear to be historical or duplicated.
#     This helps prevent re-executing code from previous conversations that the AI
#     might include in its responses.
    
#     Returns a list of filtered code blocks with duplicates removed.
#     """
#     if len(code_blocks) <= 1:
#         return code_blocks
        
#     # Look for duplicate or near-duplicate code blocks
#     unique_blocks = []
#     block_signatures = set()
    
#     for block in code_blocks:
#         # Create a signature by taking first 50 chars + last 50 chars + length
#         # This helps identify similar blocks without exact matching
#         if len(block) <= 100:
#             signature = block
#         else:
#             signature = block[:50] + block[-50:] + str(len(block))
            
#         # Also add function/class names as part of signature
#         function_matches = re.findall(r'def\s+(\w+)', block)
#         class_matches = re.findall(r'class\s+(\w+)', block)
#         for match in function_matches + class_matches:
#             signature += match
            
#         # Check if we've seen a block with this signature
#         if signature not in block_signatures:
#             block_signatures.add(signature)
#             unique_blocks.append(block)
#             futil.log(f"Including unique code block ({len(block)} chars)")
#         else:
#             futil.log(f"Filtering out duplicate/historical code block ({len(block)} chars)")
            
#     futil.log(f"Filtered {len(code_blocks) - len(unique_blocks)} duplicate/historical blocks, keeping {len(unique_blocks)}")
#     return unique_blocks

# def find_primary_code_block(code_blocks, instruction_text):
#     """
#     When multiple code blocks are present, determine which is the primary one to execute
#     based on its position and relevance to the current instruction.
    
#     Returns the index of the most relevant code block.
#     """
#     # If there's only one code block, it's the primary one
#     if len(code_blocks) <= 1:
#         return 0
    
#     futil.log(f"Multiple code blocks found ({len(code_blocks)}), determining primary block...")
    
#     # The basic rule: the FIRST code block in the message is usually the one we want
#     # This is because AI often includes examples or prior conversation content after the main response
    
#     # However, sometimes the AI might generate multiple valid code blocks in one response
#     # For example, creating multiple shapes. In that case, we should run them all.
    
#     # Check if the instruction contains phrases indicating we should run all blocks
#     run_all_indicators = [
#         "multiple shapes",
#         "multiple objects",
#         "several designs",
#         "create both",
#         "create all",
#         "all of these"
#     ]
    
#     for indicator in run_all_indicators:
#         if indicator.lower() in instruction_text.lower():
#             futil.log(f"Detected '{indicator}' in instruction, will run all code blocks")
#             return -1  # Special value indicating run all blocks
    
#     # By default, just run the first code block as it's most likely the current response
#     futil.log("Using first code block as primary (ignoring potential historical blocks)")
#     return 0

def run_logic(logic: str, chat_id=None) -> dict:
    try:
        exec(logic)
        return {
            'status': 'success',
            'message': '',
            **get_workspace_state()
        }
    except Exception as error:
        futil.log('[entry.py::get_logic] Error: ' + str(error))
        return {
            'status': 'error',
            'message': str(error),
            **get_workspace_state()
        }