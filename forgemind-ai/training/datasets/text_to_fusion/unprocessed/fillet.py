import adsk.core
import adsk.fusion
import adsk.cam


def addFilletToEdges():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct


    rootComp = design.rootComponent
    features = rootComp.features

    # Get the edges of the body to fillet
    filletInput = features.filletFeatures.createInput()
    edges = adsk.core.ObjectCollection.create()

    # Assuming that `body` refers to the body you want to fillet
    body = rootComp.bRepBodies.item(0)  # Get the first body
    for edge in body.edges:
        edges.add(edge)

    # Set fillet radius
    radius = adsk.core.ValueInput.createByReal(0.3)  # Radius is 3 mm, convert to centimeters
    filletInput.addConstantRadiusEdgeSet(edges, radius, True)

    # Create the fillet
    fillet = features.filletFeatures.add(filletInput)

addFilletToEdges()