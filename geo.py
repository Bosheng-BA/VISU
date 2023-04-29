import math


def det(u, v):
    """Determinant of two vectors (u, v)"""
    return u[0] * v[1] - u[1] * v[0]


def sca(u, v):
    """Scalar product of two vectors (u, v)"""
    return u[0] * v[0] + u[1] * v[1]


def norm(u):
    """Norm of vector u"""
    return math.sqrt(sca(u, u))


def vector(a, b):
    """Vector from xy1 to xy2"""
    return (b[0] - a[0], b[1] - a[1])


def angle_2p(p1, p2):
    # print('p1', p1, 'p2', p2)
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return math.atan2(x2 - x1, y2 - y1)



def angle(a, b, c):
    """Angle (p1, p2, p3) in radians"""
    u = vector(a, b)
    v = vector(b, c)
    return math.atan2(det(u, v), sca(u, v))


def length(l):
    """Length of a line ((x, y), ...)"""
    return sum(norm(vector(l[i], l[i + 1])) for i in range(len(l) - 1))


def dist_pt_seg(p, seg):
    """ Distance from a point to a segment """
    a, b = seg
    ab = vector(a, b)
    ap = vector(a, p)
    if 0 < sca(ab, ap):
        bp = vector(b, p)
        if sca(ab, bp) < 0:
            return abs(det(ab, ap)) / norm(ab)
        else:
            return norm(bp)
    else:
        return norm(ap)
