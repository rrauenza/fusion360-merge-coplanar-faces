# Original:
# https://forums.autodesk.com/t5/fusion-360-api-and-scripts/merging-all-coplanar-faces/td-p/8333642

import traceback
import adsk.core
import adsk.fusion


def run(context):
    try:
        root = adsk.core.Application.get().activeProduct.rootComponent  # type: adsk.fusion.Component
        merge_planar_faces(root.bRepBodies[0])
    except Exception:
        print(traceback.format_exc())


def collection_of(collection):
    object_collection = adsk.core.ObjectCollection.create()
    for obj in collection:
        object_collection.add(obj)
    return object_collection


def merge_planar_faces(body: adsk.fusion.BRepBody):
    first_temp_surface = None
    temp_unioned_surface = None

    brep = adsk.fusion.TemporaryBRepManager.get()

    for face in body.faces:
        # convert the face to a temporary BRepBody
        temp_surface = brep.copy(face)
        if first_temp_surface is None:
            # We need at least two faces to use a stitch feature, so keep a lone copy of the first face
            first_temp_surface = temp_surface
        elif temp_unioned_surface is None:
            # All the other faces get unioned into a single temporary BRepBody
            temp_unioned_surface = temp_surface
        else:
            # Adds this face to the temporary BRepBody that contains all the other faces
            brep.booleanOperation(temp_unioned_surface, temp_surface, adsk.fusion.BooleanTypes.UnionBooleanType)

    # Now stitch the first face, and all the remaining faces together, into a single solid body
    # This has the side effect of merging any coplanar faces that share an edge
    surfaces = [body.parentComponent.bRepBodies.add(first_temp_surface),
                body.parentComponent.bRepBodies.add(temp_unioned_surface)]
    stitch_input = body.parentComponent.features.stitchFeatures.createInput(
        collection_of(surfaces),
        adsk.core.ValueInput.createByReal(.01),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body.parentComponent.features.stitchFeatures.add(stitch_input)
    body.deleteMe()
