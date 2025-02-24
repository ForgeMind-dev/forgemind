import adsk.core
import adsk.fusion
import adsk.cam

def applyFilletToAllEdges():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    
    # Get the active design
    design = app.activeProduct
    rootComp = design.rootComponent

    # Get all bodies in the root component
    bodies = rootComp.bRepBodies
    if bodies.count == 0:
        ui.messageBox('No bodies in the component')
        return
        
    # Select the first body
    body = bodies.item(0)

    # Collect all edges in the body
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        edges.add(edge)

    # Create a fillet input
    filletFeatures = rootComp.features.filletFeatures
    filletInput = filletFeatures.createInput()

    # Define the radius for the fillet
    radiusValue = adsk.core.ValueInput.createByReal(0.25)

    # Add the edges with constant radius to the fillet input
    filletInput.addConstantRadiusEdgeSet(edges, radiusValue, True)

    # Create the fillet
    filletFeatures.add(filletInput)

applyFilletToAllEdges()