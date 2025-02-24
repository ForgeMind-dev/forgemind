import adsk.core
import adsk.fusion
import adsk.cam


def createCircleAndExtrude():
    app = adsk.core.Application.get()
    ui  = app.userInterface


    design = app.activeProduct
    rootComp = design.rootComponent

    # Create a new sketch on the xz plane.
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane
    sketch = sketches.add(xzPlane)

    # Draw a circle with a diameter of 6.5 cm (radius 3.25 cm).
    circles = sketch.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circle = circles.addByCenterRadius(centerPoint, 3.25)  # Radius is half the diameter

    # Get the profile defined by the circle.
    prof = sketch.profiles.item(0)

    # Create an extrusion input for the profile and join it to the existing feature.
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # Define the extent of the extrusion.
    distance = adsk.core.ValueInput.createByReal(0.5)  # Extrusion distance is 0.5 cm
    extInput.setDistanceExtent(False, distance)

    # Create the extrusion.
    extrude = extrudes.add(extInput)

createCircleAndExtrude()