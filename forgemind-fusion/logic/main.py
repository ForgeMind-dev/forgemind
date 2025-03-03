import adsk.core, adsk.fusion, traceback
from adsk.core import Application, UserInterface
from ..lib import fusionAddInUtils as futil
import math

app = adsk.core.Application.get()
ui = app.userInterface

def get_workspace_state():
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

    return {"cad_state": description, "user_id": 'FURGO'}

def run_logic(logic: str) -> dict:
    try:
        futil.log('Running logic')
        futil.log(logic)
        exec(logic)
        # app = adsk.core.Application.get()
        # ui = app.userInterface
        
        # # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        
        # design = app.activeProduct

        # # Get the root component of the active design.
        # rootComp = design.rootComponent

        # # Create a new sketch on the xy plane.
        # sketches = rootComp.sketches
        # xyPlane = rootComp.xYConstructionPlane
        # sketch = sketches.add(xyPlane)

        # # Draw some circles.
        # circles = sketch.sketchCurves.sketchCircles

        # circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 2)
        # circle2 = circles.addByCenterRadius(adsk.core.Point3D.create(8, 3, 0), 3)

        # # Add a circle at the center of one of the existing circles.
        # circle3 = circles.addByCenterRadius(circle2.centerSketchPoint, 4)
        return {
            'status': 'success',
            'workspace_state': get_workspace_state()
        }
    except Exception as error:
        futil.log('Error: ' + str(error))
        return {
            'status': 'error',
            'message': str(error)
        }