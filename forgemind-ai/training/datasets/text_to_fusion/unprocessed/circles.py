import adsk.core
import adsk.fusion

def createTwoCirclesOnXZPlane():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct

    rootComp = design.rootComponent

    # Create a new sketch on the xz plane
    sketches = rootComp.sketches
    xzPlane = rootComp.xZConstructionPlane
    sketch = sketches.add(xzPlane)

    # Define circle properties
    radius = 0.3  # radius in cm
    offset = 2.0  # distance from center in cm

    # Access the sketch circles collection
    circles = sketch.sketchCurves.sketchCircles

    # Create two circles
    circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(offset, 0, 0), radius)
    circle2 = circles.addByCenterRadius(adsk.core.Point3D.create(-offset, 0, 0), radius)

createTwoCirclesOnXZPlane()