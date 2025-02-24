app = adsk.core.Application.get()
ui = app.userInterface

# doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)

design = app.activeProduct

# Get the root component of the active design.
rootComp = design.rootComponent

# Create a new sketch on the xy plane.
sketches = rootComp.sketches
xyPlane = rootComp.xYConstructionPlane
sketch = sketches.add(xyPlane)

# Define parameters for the cube    
cube_size = 5.0

# Draw a square for the base of the cube
lines = sketch.sketchCurves.sketchLines
bottom_left = adsk.core.Point3D.create(0, 0, 0)
bottom_right = adsk.core.Point3D.create(cube_size, 0, 0)
top_right = adsk.core.Point3D.create(cube_size, cube_size, 0)
top_left = adsk.core.Point3D.create(0, cube_size, 0)

line1 = lines.addByTwoPoints(bottom_left, bottom_right)
line2 = lines.addByTwoPoints(bottom_right, top_right)
line3 = lines.addByTwoPoints(top_right, top_left)
line4 = lines.addByTwoPoints(top_left, bottom_left)

# Create a profile from the square sketch
profile = sketch.profiles.item(0)

# Extrude the profile to create the cube
extrudes = rootComp.features.extrudeFeatures
extrudeInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

distance = adsk.core.ValueInput.createByReal(cube_size)
extrudeInput.setDistanceExtent(False, distance)
extrude = extrudes.add(extrudeInput)