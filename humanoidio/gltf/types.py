import ctypes


class Float2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


class Float3(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]

    def __eq__(self, o: object) -> bool:
        match o:
            case Float3():
                return self.x == o.x and self.y == o.y and self.z == o.z
            case _:
                return False


class Float4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]


class Vertex(ctypes.Structure):
    _fields_ = [
        ("position", Float3),
        ("normal", Float3),
        ("uv", Float2),
    ]


class Bdef4(ctypes.Structure):
    _fields_ = [
        ("joints", Float4),
        ("weights", Float4),
    ]
