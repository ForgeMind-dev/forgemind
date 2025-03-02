import adsk.core
import adsk.fusion
import adsk.cam

def createTextInRectangle():
    # Get the application and user interface
    app = adsk.core.Application.get()
    ui  = app.userInterface
    design = app.activeProduct

    # Get the root component of the active design
    rootComp = design.rootComponent

    # Create a new sketch on the xy plane
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)

    # Draw the rectangular frame
    lines = sketch.sketchCurves.sketchLines
    lines.addTwoPointRectangle(adsk.core.Point3D.create(-5, -2, 0), adsk.core.Point3D.create(5, 2, 0))

    # Create the text 'YC' inside the rectangle
    texts = sketch.sketchTexts
    position = adsk.core.Point3D.create(0, 0, 0)
    textInput = texts.createInput("YC", 1.0, position)
    sketchText = texts.add(textInput)

    # Use the sketchText directly in extrusion
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(sketchText, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

    # Define the extent of the extrusion
    extDistance = adsk.core.ValueInput.createByReal(0.25)
    extInput.setDistanceExtent(False, extDistance)

    # Create the extrusion
    extrudes.add(extInput)

createTextInRectangle()