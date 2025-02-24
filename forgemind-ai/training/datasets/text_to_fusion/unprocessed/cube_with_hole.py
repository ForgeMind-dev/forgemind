import adsk.core
import adsk.fusion
import adsk.cam

def createCubeWithHole():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    
    # Get the active design
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Create a new sketch on the xy plane
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch = sketches.add(xyPlane)
    
    # Draw a square for the base of the cube
    squareSize = 5
    lines = sketch.sketchCurves.sketchLines
    lines.addTwoPointRectangle(adsk.core.Point3D.create(-squareSize/2, -squareSize/2, 0), 
                               adsk.core.Point3D.create(squareSize/2, squareSize/2, 0))
    
    # Extrude square to form a cube
    prof = sketch.profiles.item(0)
    extrudes = rootComp.features.extrudeFeatures
    distance = adsk.core.ValueInput.createByReal(squareSize)
    extrude = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    # Get the body of the cube
    cubeBody = extrude.bodies.item(0)
    
    # Create a sketch for the hole
    sketchForHole = sketches.add(xyPlane)
    
    # Draw a circle for the hole on the cube
    holeRadius = 3
    circles = sketchForHole.sketchCurves.sketchCircles
    centerPoint = adsk.core.Point3D.create(0, 0, 0)
    circles.addByCenterRadius(centerPoint, holeRadius)
    
    # Cut extrude the circle to create a hole through the cube
    holeProf = sketchForHole.profiles.item(0)
    holeExtrude = extrudes.addSimple(holeProf, distance, adsk.fusion.FeatureOperations.CutFeatureOperation)
    
    return

createCubeWithHole()