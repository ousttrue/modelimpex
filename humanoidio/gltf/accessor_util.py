from typing import Iterable, Iterator, Any, TypeVar, Callable, Type
import ctypes
import array
from enum import IntEnum
from .types import Float2, Float3, Float4
from . import gltf_json_type


T = TypeVar("T")


def enumerate_1(iterable: Iterable[T]) -> Callable[[], Iterator[T]]:
    def g():
        for x in iterable:
            yield x

    return g


def enumerate_2(iterable: Iterable[T]) -> Callable[[], Iterator[tuple[T, T]]]:
    def g():
        it = iter(iterable)
        while True:
            try:
                _0 = next(it)
                _1 = next(it)
                yield (_0, _1)
            except StopIteration:
                break

    return g


def enumerate_3(iterable: Iterable[T]) -> Callable[[], Iterator[tuple[T, T, T]]]:
    def g():
        it = iter(iterable)
        while True:
            try:
                _0 = next(it)
                _1 = next(it)
                _2 = next(it)
                yield (_0, _1, _2)
            except StopIteration:
                break

    return g


def enumerate_4(iterable: Iterable[T]) -> Callable[[], Iterator[tuple[T, T, T, T]]]:
    def g():
        it = iter(iterable)
        while True:
            try:
                _0 = next(it)
                _1 = next(it)
                _2 = next(it)
                _3 = next(it)
                yield (_0, _1, _2, _3)
            except StopIteration:
                break

    return g


class ComponentType(IntEnum):
    Int8 = 5120
    UInt8 = 5121
    Int16 = 5122
    UInt16 = 5123
    UInt32 = 5125
    Float = 5126


def get_span(data: bytes | bytearray, ct: ComponentType) -> Iterable[Any]:
    if ct == ComponentType.Int8:
        return memoryview(data).cast("b")
    elif ct == ComponentType.UInt8:
        return memoryview(data).cast("B")
    elif ct == ComponentType.Int16:
        return memoryview(data).cast("h")
    elif ct == ComponentType.UInt16:
        return memoryview(data).cast("H")
    elif ct == ComponentType.UInt32:
        return memoryview(data).cast("I")
    elif ct == ComponentType.Float:
        return memoryview(data).cast("f")
    else:
        raise ValueError(f"unknown component type: {ct}")


CT_SIZE_MAP: dict[ComponentType, int] = {
    ComponentType.Int8: 1,
    ComponentType.UInt8: 1,
    ComponentType.Int16: 2,
    ComponentType.UInt16: 2,
    ComponentType.UInt32: 4,
    ComponentType.Float: 4,
}

TYPE_SIZE_MAP: dict[str, int] = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16,
}


def get_size_count(accessor: gltf_json_type.Accessor) -> tuple[int, int]:
    ct = accessor["componentType"]
    t = accessor["type"]
    return (CT_SIZE_MAP[ComponentType(ct)], TYPE_SIZE_MAP[t])  # type: ignore


def get_type_count(
    values: memoryview | ctypes.Array[Any] | array.array,  # type: ignore
) -> tuple[ComponentType, str]:
    if isinstance(values, memoryview):
        raise NotImplementedError()
    elif isinstance(values, ctypes.Array):
        t = values._type_
        s = ctypes.sizeof(t)
        if values._type_ == ctypes.c_uint32:
            return ComponentType.UInt32, "SCALAR"
        elif s == 12:
            return ComponentType.Float, "VEC3"
        elif s == 16:
            return ComponentType.Float, "VEC4"
        else:
            raise NotImplementedError(f"{values._type_}")
    else:  # isinstance(values, array.array):
        if values.typecode == "f":
            return ComponentType.Float, "SCALAR"
        else:
            raise NotImplementedError(f"array.array: {values.typecode}")


class GltfAccessor:
    bufferViews: list[gltf_json_type.BufferView]
    accessors: list[gltf_json_type.Accessor]
    images: list[gltf_json_type.Image]
    bin: bytes

    def __init__(self, gltf: gltf_json_type.glTF, bin: bytes | bytearray | None):
        match bin:
            case bytes():
                self.bin = bin
            case bytearray():
                self.bin = bytes(bin)
            case _:
                self.bin = b""

        match gltf:
            case {"bufferViews": bufferViews}:
                self.bufferViews = bufferViews
                self._write_buffer = None
                if isinstance(bin, bytearray):
                    # writeable
                    self._write_buffer = bin
            case _:
                raise RuntimeError()

        match gltf:
            case {"accessors": accessors}:
                self.accessors = accessors
            case _:
                self.accessors = []

        match gltf:
            case {"images": images}:
                self.images = images
            case _:
                self.images = []

    def bufferview_bytes(self, index: int) -> bytes:
        bufferView = self.bufferViews[index]
        match bufferView:
            case {"byteOffset": offset, "byteLength": length}:
                return self.bin[offset : offset + length]
            case _:
                raise RuntimeError("invalid bufferView")

    def image_mime_bytes(
        self, index: int
    ) -> tuple[gltf_json_type.ImageMimeType, bytes]:
        image = self.images[index]
        match image:
            case {"mimeType": mime, "bufferView": bufferView}:
                return mime, self.bufferview_bytes(bufferView)
            case _:
                raise RuntimeError("invalid image")

    def get_typed_accessor(self, t: Type[T], accessor_index: int) -> ctypes.Array[T]:
        accessor = self.accessors[accessor_index]
        if t == ctypes.c_uint16:
            assert accessor["type"] == "SCALAR"
            assert accessor["componentType"] == 5123
        elif t == ctypes.c_int32:
            assert accessor["type"] == "SCALAR"
            assert accessor["componentType"] == 5125
        elif t == Float2:
            assert accessor["type"] == "VEC2"
            assert accessor["componentType"] == 5126
        elif t == Float3:
            assert accessor["type"] == "VEC3"
            assert accessor["componentType"] == 5126
        elif t == Float4:
            assert accessor["type"] == "VEC4"
            assert accessor["componentType"] == 5126
        else:
            raise NotImplementedError()

        array_type = t * accessor["count"]
        match accessor:
            case {"bufferView": int(bufferview_index)}:
                data = self.bufferview_bytes(bufferview_index)
                return array_type.from_buffer_copy(data)
            case _:
                raise NotImplementedError()

    def get_index_accessor(
        self, accessor_index: int
    ) -> ctypes.Array[ctypes.c_uint16] | ctypes.Array[ctypes.c_int32]:
        """
        BYTE = 5120
        UNSIGNED_BYTE = 5121
        SHORT = 5122
        UNSIGNED_SHORT = 5123
        UNSIGNED_INT = 5125
        FLOAT = 5126
        """
        accessor = self.accessors[accessor_index]
        assert accessor["type"] == "SCALAR"
        match accessor["componentType"]:
            case 5122 | 5123:
                return self.get_typed_accessor(ctypes.c_uint16, accessor_index)
            case 5125:
                return self.get_typed_accessor(ctypes.c_int32, accessor_index)
            case _:
                raise NotImplementedError()

    def accessor_generator(self, index: int) -> Callable[[], Iterator[Any]]:
        accessor = self.accessors[index]
        offset = accessor.get("byteOffset", 0)
        count = accessor.get("count")
        element_size, element_count = get_size_count(accessor)
        match accessor:
            case {"bufferView": bufferView, "componentType": componentType}:
                buffer = self.bufferview_bytes(bufferView)
                if not buffer:
                    raise Exception("")
                data = buffer[offset : offset + element_size * element_count * count]
                span = get_span(data, ComponentType(componentType))
                if element_count == 1:
                    return enumerate_1(span)
                elif element_count == 2:
                    return enumerate_2(span)
                elif element_count == 3:
                    return enumerate_3(span)
                elif element_count == 4:
                    return enumerate_4(span)
                else:
                    raise NotImplementedError()
            case _:
                raise Exception("")

    def push_bytes(self, data: bytes | memoryview) -> int:
        if self._write_buffer == None:
            raise Exception("not writable")
        bufferView_index = len(self.bufferViews)
        bufferView: gltf_json_type.BufferView = {
            "buffer": 0,
            "byteOffset": len(self.bin),
            "byteLength": len(data),
        }
        self._write_buffer.extend(data)
        self.bufferViews.append(bufferView)
        return bufferView_index

    def push_array(self, values: Any, min_max: Any = None) -> int:
        accessor_index = len(self.accessors)
        t, c = get_type_count(values)
        accessor: gltf_json_type.Accessor = {  # type: ignore
            "bufferView": self.push_bytes(memoryview(values).cast("B")),
            "type": c,
            "componentType": t.value,
            "count": len(values),
        }
        if min_max:
            c = min_max()
            for v in values:
                c.push(v)
            accessor["min"] = c.min
            accessor["max"] = c.max

        self.accessors.append(accessor)
        return accessor_index
