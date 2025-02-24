import adsk.core
import adsk.fusion
import adsk.cam

def deleteAllBodiesAndSketches():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct
    rootComp = design.rootComponent
    
    # Delete all bodies
    bodies = rootComp.bRepBodies
    for body in bodies:
        body.deleteMe()
    
    # Delete all sketches
    sketches = rootComp.sketches
    for sketch in sketches:
        sketch.deleteMe()

deleteAllBodiesAndSketches()