import adsk.core
import adsk.fusion
import adsk.cam
import math


def createHollowCylinder():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    design = app.activeProduct


    rootComp = design.rootComponent
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane
    sketch = sketches.add(xzPlane)

    # Define the outer circle for the hollow cylinder
    outerRadius = 7.5 / 2.0  # Convert diameter to radius
    circles = sketch.sketchCurves.sketchCircles
    outerCircle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), outerRadius)

    # Define the inner circle for the hollow cylinder
    wallThickness = 0.5
    innerRadius = outerRadius - wallThickness
    innerCircle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), innerRadius)

    # Get the profile of the ring
    prof = sketch.profiles.item(0)

    # Create an extrusion input
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Define the extent of the extrusion
    distance = adsk.core.ValueInput.createByReal(12.0)
    extInput.setDistanceExtent(False, distance)
    extInput.isSolid = True

    # Create the extrusion
    ext = extrudes.add(extInput)

createHollowCylinder()