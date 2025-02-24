import adsk.core
import adsk.fusion

def removeAllFillets():
    app = adsk.core.Application.get()
    ui  = app.userInterface
    design = app.activeProduct

    # Get the root component of the active design
    rootComp = design.rootComponent
    allFeatures = rootComp.features

    # Get all the fillet features in the component
    filletFeatures = allFeatures.filletFeatures

    # Iterate through each fillet feature and delete it
    for filletFeature in filletFeatures:
        if filletFeature.isValid:
            filletFeature.deleteMe()

removeAllFillets()