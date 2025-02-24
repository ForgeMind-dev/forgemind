app = adsk.core.Application.get()
ui = app.userInterface

design = app.activeProduct

# Get the root component of the active design.
rootComp = design.rootComponent

# Create a new sketch on the xy plane.
sketches = rootComp.sketches
xyPlane = rootComp.xYConstructionPlane
sketch = sketches.add(xyPlane)

# Draw two circles to represent the hollow cylinder's walls.
circles = sketch.sketchCurves.sketchCircles
outerCircle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 2) # Outer radius is 2
innerCircle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 1) # Inner radius is 1

# Use the profiles of the circles to create the hollow cylinder.
prof = sketch.profiles.item(0)
extrudes = rootComp.features.extrudeFeatures
extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
distance = adsk.core.ValueInput.createByReal(4) # Height is 4
extInput.setDistanceExtent(False, distance)
extrude = extrudes.add(extInput)