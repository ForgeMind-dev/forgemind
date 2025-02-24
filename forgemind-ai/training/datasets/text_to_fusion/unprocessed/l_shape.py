import adsk.core
import adsk.fusion
import adsk.cam

def createLShape():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    design = app.activeProduct
    
    rootComp = design.rootComponent
    
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    lines = sketch.sketchCurves.sketchLines

    # Create the L shape using lines
    line1 = lines.addByTwoPoints(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(4, 0, 0))
    line2 = lines.addByTwoPoints(line1.endSketchPoint, adsk.core.Point3D.create(4, 2, 0))
    line3 = lines.addByTwoPoints(line2.endSketchPoint, adsk.core.Point3D.create(2, 2, 0))
    line4 = lines.addByTwoPoints(line3.endSketchPoint, adsk.core.Point3D.create(2, 4, 0))
    line5 = lines.addByTwoPoints(line4.endSketchPoint, adsk.core.Point3D.create(0, 4, 0))
    line6 = lines.addByTwoPoints(line5.endSketchPoint, adsk.core.Point3D.create(0, 0, 0))

    # Create a profile for extrusion
    prof = sketch.profiles.item(0)
    
    # Create an extrusion input from the L shape profile
    extrudes = rootComp.features.extrudeFeatures
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(2.0)
    
    # Set the extrusion extent
    extInput.setDistanceExtent(False, distance)
    extInput.isSolid = True
    
    # Create the extrusion
    ext = extrudes.add(extInput)
    
createLShape()