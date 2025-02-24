import adsk.core
import adsk.fusion
import adsk.cam

def createXZSketchWithSquare():
app = adsk.core.Application.get()
design = app.activeProduct
rootComp = design.rootComponent

# Create a new sketch on the xz plane
sketches = rootComp.sketches
xzPlane = rootComp.xZConstructionPlane
sketch = sketches.add(xzPlane)

# Draw a 10x10 square
lines = sketch.sketchCurves.sketchLines
corner1 = adsk.core.Point3D.create(-5, -5, 0)
corner2 = adsk.core.Point3D.create(5, -5, 0)
corner3 = adsk.core.Point3D.create(5, 5, 0)
corner4 = adsk.core.Point3D.create(-5, 5, 0)

lines.addByTwoPoints(corner1, corner2)
lines.addByTwoPoints(corner2, corner3)
lines.addByTwoPoints(corner3, corner4)
lines.addByTwoPoints(corner4, corner1)

createXZSketchWithSquare()