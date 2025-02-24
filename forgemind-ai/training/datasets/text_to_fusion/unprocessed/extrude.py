import adsk.core
import adsk.fusion
import adsk.cam

def extrudeSketchByTwo():
    app = adsk.core.Application.get()
    ui = app.userInterface
    
    # Get the active design
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Get the sketch to be extruded
    sketches = rootComp.sketches
    sketch = sketches.item(0)  # Assuming the sketch you want to extrude is the first one
    
    # Get the profile defined by the sketch
    prof = sketch.profiles.item(0)  # Assuming the first profile
    
    # Create an extrusion input from the profile
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # Set the extrusion extent to 2
    distance = adsk.core.ValueInput.createByString("2 cm")
    extInput.setDistanceExtent(False, distance)
    extInput.isSolid = True
    
    # Create the extrusion
    extrude = extrudes.add(extInput)

extrudeSketchByTwo()