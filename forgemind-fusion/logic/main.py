import adsk.core, adsk.fusion, traceback
from adsk.core import Application, UserInterface
from ..lib import fusionAddInUtils as futil
from ..commands.Login import entry as login
import math

app = adsk.core.Application.get()
ui = app.userInterface

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
                    "surface_area": body.area,  # Fixed the error here
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
            **get_workspace_state(),
            'status': 'success',
        }
    except Exception as error:
        futil.log('Error: ' + str(error))
        return {
            'status': 'error',
            'message': str(error),
            **get_workspace_state()
        }