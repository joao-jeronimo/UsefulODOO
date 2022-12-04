
def VmrlModel(objects):
    return """#VRML V2.0 utf8
# Automatically generated VRML file by wrlgen:
DirectionalLight {
  direction 0 -1 0
}
""" + "\n".join(objects)

def Transform(translate=False, objects=[]):
    transformations = ""
    if translate:
        transformations += "translation %d %d %d" % translate
    # Build final object:
    return """
    Transform {
        %(transformations)s
        children [
            %(objects)s
        ]
    }""" % {
        'transformations'   : transformations,
        'objects'           : "\n".join(objects),
        }

