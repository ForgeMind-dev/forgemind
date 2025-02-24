import adsk.core
import adsk.fusion
import adsk.cam


def createDiskOnXZPlane():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    design = app.activeProduct


    rootComp = design.rootComponent

    # Create a new sketch on the xz plane
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane
    sketch = sketches.add(xzPlane)

    # Draw a circle centered at the origin with a radius of 2 cm
    circles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = circles.addByCenterRadius(centerPoint, 2.0)

    # Create an extrusion input for the profile
    prof = sketch.profiles.item(0)
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Define the extent of the extrusion to be 0.5 cm
    distance = adsk.core.ValueInput.createByReal(0.5)
    extInput.setDistanceExtent(False, distance)

    # Create the extrusion
    extrude = extrudes.add(extInput)

createDiskOnXZPlane()