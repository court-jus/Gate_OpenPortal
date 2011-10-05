from pandac.PandaModules import EggData, EggVertex, EggPolygon, EggGroup, EggGroupNode, EggVertexPool, EggMaterial, EggTexture
from panda3d.core import Point3D, GlobPattern, VBase4, Point2D

FACES = [
    [(-15.0, 0.0,-15.0),
     (-15.0, 0.0, 15.0),
     (-15.0,15.0, 15.0),
     (-15.0,15.0,-15.0),],
    [( 15.0, 0.0,-15.0),
     ( 15.0, 0.0, 15.0),
     ( 15.0,15.0, 15.0),
     ( 15.0,15.0,-15.0),],
    [(-15.0, 0.0,-15.0),
     ( 15.0, 0.0,-15.0),
     ( 15.0,15.0,-15.0),
     (-15.0,15.0,-15.0),],
    [(-15.0, 0.0, 15.0),
     ( 15.0, 0.0, 15.0),
     ( 15.0,15.0, 15.0),
     (-15.0,15.0, 15.0),],
    [(-15.0, 0.0,-15.0),
     ( 15.0, 0.0,-15.0),
     ( 15.0, 0.0, 15.0),
     (-15.0, 0.0, 15.0),],
    [(-15.0,15.0,-15.0),
     ( 15.0,15.0,-15.0),
     ( 15.0,15.0, 15.0),
     (-15.0,15.0, 15.0),],
    ]

def findUV(x, y, z, face = []):
    X = [v[0] for v in face]
    Y = [v[1] for v in face]
    Z = [v[2] for v in face]
    if min(Y) == max(Y):
        u = 0 if x == 0 else x / abs(x)
        v = 0 if z == 0 else z / abs(z)
    elif min(X) == max(X):
        u = 0 if y == 0 else y / abs(y)
        v = 0 if z == 0 else z / abs(z)
    elif min(Z) == max(Z):
        u = 0 if x == 0 else x / abs(x)
        v = 0 if y == 0 else y / abs(y)
    return Point2D(u, v)

def main():

    eg = EggData()
    mat = EggMaterial("mat")
    mat.setDiff(VBase4(0.640,0.640,0.640,1.000))
    mat.setSpec(VBase4(0.500,0.500,0.500,1.000))
    mat.setEmit(VBase4(0.100,0.100,0.100,1.000))
    mat.setShininess(12.5)

    tex = EggTexture("tex", "./models/tex/dallage.jpg")

    egrp = EggGroup("Cube")
    egrp.setCollideFlags(egrp.CFKeep | egrp.CFDescend)
    egrp.setCsType(egrp.CSTPolyset)
    eg.addChild(egrp)
    evpool = EggVertexPool("Cube")
    egrp.addChild(evpool)

    for face in FACES:
        # Double faces :
        # First one
        epoly = EggPolygon()
        egrp.addChild(epoly)
        epoly.setMaterial(mat)
        epoly.setTexture(tex)
        for vertex in face:
            ev = EggVertex()
            ev.setPos(Point3D(*vertex))
            ev.setUv(findUV(*vertex, face = face))
            evpool.addVertex(ev)
            epoly.addVertex(ev)
        # Second one
        epoly = EggPolygon()
        egrp.addChild(epoly)
        epoly.setMaterial(mat)
        epoly.setTexture(tex)
        for vertex in face[::-1]:
            ev = EggVertex()
            ev.setPos(Point3D(*vertex))
            ev.setUv(findUV(*vertex, face = face))
            evpool.addVertex(ev)
            epoly.addVertex(ev)

    eg.recomputeTangentBinormal(GlobPattern(""))
    eg.removeUnusedVertices(GlobPattern(""))
    eg.triangulatePolygons(EggData.TConvex & EggData.TPolygon)
    eg.recomputePolygonNormals()
    eg.setEggFilename('test.egg')
    eg.writeEgg('test.egg')

if __name__ == "__main__":
    main()
