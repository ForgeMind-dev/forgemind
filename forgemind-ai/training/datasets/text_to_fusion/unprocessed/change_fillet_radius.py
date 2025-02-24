import adsk.core
import adsk.fusion
import adsk.cam


def changeFilletRadiusTo2mm():
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = app.activeProduct
    rootComp = design.rootComponent


    # Get all features in the root component
    features = rootComp.features

    # Get all Fillet features
    filletFeatures = features.filletFeatures

    # Iterate through each fillet feature
    for fillet in filletFeatures:
        # Get all fillet edge sets from this fillet feature
        filletEdgeSets = fillet.edgeSets
        for edgeSet in filletEdgeSets:
            # Access the radius parameter of the edge set
            radiusParameter = edgeSet.radius
            # Change the radius to 2mm
            radiusParameter.value = 0.2

changeFilletRadiusTo2mm()