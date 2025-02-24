app = adsk.core.Application.get()
ui = app.userInterface

design = app.activeProduct

# Get the root component of the active design.
rootComp = design.rootComponent

# Create a new sketch on the xy plane.
sketches = rootComp.sketches
xyPlane = rootComp.xYConstructionPlane
sketch = sketches.add(xyPlane)

# Draw a circle for the base of the cylinder.
circles = sketch.sketchCurves.sketchCircles
circle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 5)

# Get the profile defined by the circle.
profile = sketch.profiles.item(0)

# Create an extrusion input for the profile.
extrudes = rootComp.features.extrudeFeatures
extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

# Define the extent of the extrusion.
distance = adsk.core.ValueInput.createByReal(20)
extInput.setDistanceExtent(False, distance)

# Create the extrusion.
extrude = extrudes.add(extInput)