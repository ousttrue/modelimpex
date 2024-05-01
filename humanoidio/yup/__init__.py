import pathlib
import bpy
import struct
from .gltfbuilder import GLTFBuilder
from .to_gltf import to_gltf
from .gltf import GLTF


def get_objects(selected_only: bool) -> list[bpy.types.Object]:
    if selected_only and bpy.context.selected_objects:
        return bpy.context.selected_objects
    else:
        return [o for o in bpy.data.scenes[0].objects if not o.parent]


def to_bytes(path: pathlib.Path, objects: list[bpy.types.Object]) -> tuple[GLTF, bytes]:
    ext = path.suffix.lower()

    with GLTFBuilder() as builder:
        builder.export_objects(objects)

        #
        # export
        #
        bin_path = path.parent / (path.stem + ".bin")
        gltf, bin = to_gltf(builder, path, bin_path if ext != ".glb" else None)
        return gltf, bytes(bin)


def export(path: pathlib.Path, selected_only: bool):
    # object mode
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

    objects = get_objects(selected_only)

    gltf, bin_bytes = to_bytes(path, objects)

    #
    # write
    #
    json_bytes = gltf.to_json().encode("utf-8")

    ext = path.suffix.lower()
    bin_path = path.parent / (path.stem + ".bin")
    if ext == ".gltf":
        with path.open("wb") as f:
            f.write(json_bytes)
        with bin_path.open("wb") as f:
            f.write(bin_bytes)
    elif ext == ".glb" or ext == ".vrm":
        with path.open("wb") as f:
            if len(json_bytes) % 4 != 0:
                json_padding_size = 4 - len(json_bytes) % 4
                print(f"add json_padding_size: {json_padding_size}")
                json_bytes += b" " * json_padding_size
            json_header = struct.pack(b"I", len(json_bytes)) + b"JSON"
            bin_header = struct.pack(b"I", len(bin_bytes)) + b"BIN\x00"
            header = b"glTF" + struct.pack(
                "II",
                2,
                12
                + len(json_header)
                + len(json_bytes)
                + len(bin_header)
                + len(bin_bytes),
            )
            #
            f.write(header)
            f.write(json_header)
            f.write(json_bytes)
            f.write(bin_header)
            f.write(bin_bytes)
    else:
        raise NotImplementedError()
