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

# Draw a rectangle with width 10 and height 40.
lines = sketch.sketchCurves.sketchLines
rectLines = lines.addTwoPointRectangle(adsk.core.Point3D.create(0, 0, 0), adsk.core.Point3D.create(10, 40, 0))

# Get the profile defined by the rectangle.
prof = sketch.profiles.item(0)

# Create an extrusion input
extrudes = rootComp.features.extrudeFeatures
extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

# Define that the extent is a distance extent of 12.
distance = adsk.core.ValueInput.createByReal(12)

# Set the distance extent.
extInput.setDistanceExtent(False, distance)

# Create the extrusion.
ext = extrudes.add(extInput)