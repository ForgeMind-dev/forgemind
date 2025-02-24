import adsk.core, adsk.fusion, adsk.cam

def create_stop_sign():
    # Create a new Fusion 360 document
    app = adsk.core.Application.get()
    design = app.activeProduct

    # Create a new component
    root_comp = design.rootComponent
    all_occurrences = root_comp.occurrences
    trans = adsk.core.Matrix3D.create()
    occ = all_occurrences.addNewComponent(trans)
    comp = adsk.fusion.Component.cast(occ.component)

    # Create a new sketch
    sketches = comp.sketches
    xyPlane = comp.xYConstructionPlane
    sketch = sketches.add(xyPlane)

    # Define dimensions for the stop sign
    side_length = 100  # Side length of the octagon

    # Calculate the points of the octagon
    num_sides = 8
    angle_offset = math.radians(22.5)  # Offset to start from flat side
    center = adsk.core.Point3D.create(0, 0, 0)
    points = []

    for i in range(num_sides):
        angle = i * (2 * math.pi / num_sides) + angle_offset
        x = center.x + side_length * math.cos(angle)
        y = center.y + side_length * math.sin(angle)
        points.append(adsk.core.Point3D.create(x, y, 0))
    
    # Draw the octagon
    lines = sketch.sketchCurves.sketchLines
    for i in range(num_sides):
        start_point = points[i]
        end_point = points[(i + 1) % num_sides]
        lines.addByTwoPoints(start_point, end_point)

    # Extrude the profile
    prof = sketch.profiles.item(0)
    extrudes = comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(10)  # Thickness of the stop sign
    extrude_input.setDistanceExtent(False, distance)
    extrudes.add(extrude_input)

create_stop_sign()
