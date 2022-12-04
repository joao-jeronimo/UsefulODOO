
def VmrlModel(objects):
    return """#VRML V2.0 utf8
# Automatically generated VRML file by wrlgen:
DirectionalLight {
  direction 0 -1 0
}
""" + "\n".join(objects)

