import math

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return Vector2(self.x, self.y)

    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return Vector2(self.x, self.y)

    def __mul__(self, other):
        if type(other) == float:
            return Vector2(self.x*other, self.y*other)
        else:
            return Vector2(self.x*other.x, self.y*other.y)

    def normalize(self):
        xxyy = self.x*self.x + self.y*self.y

        if xxyy == 0.0:
            return Vector2(self.x, self.y)

        invLength = 1.0 / math.sqrt(xxyy)
        self.x *= invLength
        self.y *= invLength
        return Vector2(self.x, self.y)

def Vector2Distance(va, vb):
    return math.sqrt((va.x-vb.x)**2.0 + (va.y-vb.y)**2.0)

def PointDistance(a, b):
    return math.sqrt((a[0]-b[0])**2.0 + (a[1]-b[1])**2.0)

def Vector2Lerp(vfrom, vto, t):

    _EPS = (1e-6)

    temp = Vector2(0.0, 0.0)
    omega = cosom = sinom = scale0 = scale1 = 0.0

    if t < 0.0:
        return vfrom
    elif t > 1.0:
        return vto

    cosom = vfrom.x * vto.x + vfrom.y * vto.y

    if cosom < 0.0:
        temp = -vto
        cosom = -cosom
    else:
        temp = vto

    if(1.0 - cosom) > _EPS:
        omega = math.acos(cosom)
        sinom = 1.0 / math.sin(omega)
        scale0 = math.sin((1.0 - t) * omega) * sinom
        scale1 = math.sin(t * omega) * sinom
    else:
        scale0 = 1.0 - t
        scale1 = t

    return (vfrom * scale0) + (temp * scale1)


def Vector2Length(v):
    return math.sqrt(v.x*v.x + v.y*v.y)

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


def Collide_Circle_Point(vSphere, Radius, vPoint, vReaction):

    dist = Vector2Distance(vSphere, vPoint)
    if dist <= Radius:
        intdir = vSphere-vPoint
        intdir.normalize()

        vReaction += Vector2(
            intdir.x*(Radius-dist),
            intdir.y*(Radius-dist)
        )

        return True

    return False

def Collide_Circle_Line(vObjPos, ObjRadius, LineA, LineB, vReaction):
    
    vCircleCentre = Vector2(vObjPos.x, vObjPos.y)

    closestX = vCircleCentre.x
    closestY = vCircleCentre.y

    if vCircleCentre.x < LineA[0]:
        closestX = LineA[0]
    elif vCircleCentre.x > LineB[0]:
        closestX = LineB[0]

    if vCircleCentre.y < LineA[1]:
        closestY = LineA[1]
    elif vCircleCentre.y > LineB[1]:
        closestY = LineB[1]

    intline = Vector2(closestX, closestY)
    dist = Vector2Distance(vCircleCentre, intline)
    
    if dist < ObjRadius:
        intdir = intline-vCircleCentre
        intdir.normalize()

        vReaction += Vector2(
            -(intdir.x*(ObjRadius-dist)),
            -(intdir.y*(ObjRadius-dist))
        )

        return True

    return False

def Collide_Circle_Rectangle(vObjPos, ObjRadius, Rect, vReaction):
    
    vCircleCentre = Vector2(vObjPos.x, vObjPos.y)

    closestX = vCircleCentre.x
    closestY = vCircleCentre.y

    if vCircleCentre.x < Rect.x:
        closestX = Rect.x
    elif vCircleCentre.x > Rect.x+Rect.w:
        closestX = Rect.x+Rect.w

    if vCircleCentre.y < Rect.y:
        closestY = Rect.y
    elif vCircleCentre.y > Rect.y+Rect.h:
        closestY = Rect.y+Rect.h

    intline = Vector2(closestX, closestY)
    dist = Vector2Distance(vCircleCentre, intline)
    
    if dist < ObjRadius:
        intdir = intline-vCircleCentre
        intdir.normalize()

        vReaction += Vector2(
            -(intdir.x*(ObjRadius-dist)),
            -(intdir.y*(ObjRadius-dist))
        )

        return True

    return False


def Collide_Circle_Circle(PosA, RadiusA, PosB, RadiusB, vReaction):

    dist = Vector2Distance(PosA, PosB)
    rs = RadiusA+RadiusB

    if dist < rs:

        intdir = (PosA-PosB).normalize()

        vReaction += Vector2(
            intdir.x*(rs-dist),
            intdir.y*(rs-dist)
        )

        return True

    return False


def Collide_Line_Rect(x1, y1, x2, y2, rx, ry, rw, rh):
    def _line_line(x1, y1, x2, y2, x3, y3, x4, y4):
        uA0 = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))
        uA1 = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
        uB0 = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3))
        uB1 = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

        if uA1 == 0.0 or uB1 == 0.0:
            return False

        uA = uA0 / uA1
        uB = uB0 / uB1
        return (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1)

    #l
    if _line_line(x1, y1, x2, y2, rx, ry, rx, ry+rh):
        return True
    #r
    if _line_line(x1, y1, x2, y2, rx+rw, ry, rx+rw, ry+rh):
        return True
    #t
    if _line_line(x1, y1, x2, y2, rx, ry, rx+rw, ry):
        return True
    #b
    if _line_line(x1, y1, x2, y2, rx, ry+rh, rx+rw, ry+rh):
        return True

    return False