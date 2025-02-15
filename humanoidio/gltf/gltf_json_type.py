# this is generated by sukonbu
from typing import TypedDict, List, Dict, Any, Literal
from enum import IntEnum, StrEnum


class AccessorSparseIndicesComponentType(IntEnum):
    UNSIGNED_BYTE = 5121
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125


class AccessorSparseIndicesRequired(TypedDict):
    # The index of the bufferView with sparse indices. Referenced bufferView can't have ARRAY_BUFFER or ELEMENT_ARRAY_BUFFER target.
    bufferView: int
    # The indices data type.
    componentType: AccessorSparseIndicesComponentType


class AccessorSparseIndicesOptional(TypedDict, total=False):
    # The offset relative to the start of the bufferView in bytes. Must be aligned.
    byteOffset: int
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AccessorSparseIndices(
    AccessorSparseIndicesRequired, AccessorSparseIndicesOptional
):
    pass


class AccessorSparseValuesRequired(TypedDict):
    # The index of the bufferView with sparse values. Referenced bufferView can't have ARRAY_BUFFER or ELEMENT_ARRAY_BUFFER target.
    bufferView: int


class AccessorSparseValuesOptional(TypedDict, total=False):
    # The offset relative to the start of the bufferView in bytes. Must be aligned.
    byteOffset: int
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AccessorSparseValues(AccessorSparseValuesRequired, AccessorSparseValuesOptional):
    pass


class AccessorSparseRequired(TypedDict):
    # Number of entries stored in the sparse array.
    count: int
    # Indices of those attributes that deviate from their initialization value.
    indices: AccessorSparseIndices
    # Array of size `accessor.sparse.count` times number of components storing the displaced accessor attributes pointed by `accessor.sparse.indices`.
    values: AccessorSparseValues


class AccessorSparseOptional(TypedDict, total=False):
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AccessorSparse(AccessorSparseRequired, AccessorSparseOptional):
    pass


class AccessorRequired(TypedDict):
    # The datatype of components in the attribute.
    """
    BYTE = 5120
    UNSIGNED_BYTE = 5121
    SHORT = 5122
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125
    FLOAT = 5126
    """
    componentType: Literal[5120, 5121, 5122, 5123, 5125, 5126]
    # The number of attributes referenced by this accessor.
    count: int
    # Specifies if the attribute is a scalar, vector, or matrix.
    type: Literal["SCALAR", "VEC2", "VEC3", "VEC4", "MAT2", "MAT3", "MAT4"]


class AccessorOptional(TypedDict, total=False):
    # The index of the bufferView.
    bufferView: int
    # The offset relative to the start of the bufferView in bytes.
    byteOffset: int
    # Specifies whether integer data values should be normalized.
    normalized: bool
    # Maximum value of each component in this attribute.
    max: List[float]
    # Minimum value of each component in this attribute.
    min: List[float]
    # Sparse storage of attributes that deviate from their initialization value.
    sparse: AccessorSparse
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Accessor(AccessorRequired, AccessorOptional):
    pass


class AnimationChannelTargetPath(StrEnum):
    translation = "translation"
    rotation = "rotation"
    scale = "scale"
    weights = "weights"


class AnimationChannelTargetRequired(TypedDict):
    # The name of the node's TRS property to modify, or the "weights" of the Morph Targets it instantiates. For the "translation" property, the values that are provided by the sampler are the translation along the x, y, and z axes. For the "rotation" property, the values are a quaternion in the order (x, y, z, w), where w is the scalar. For the "scale" property, the values are the scaling factors along the x, y, and z axes.
    path: AnimationChannelTargetPath


class AnimationChannelTargetOptional(TypedDict, total=False):
    # The index of the node to target.
    node: int
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AnimationChannelTarget(
    AnimationChannelTargetRequired, AnimationChannelTargetOptional
):
    pass


class AnimationChannelRequired(TypedDict):
    # The index of a sampler in this animation used to compute the value for the target.
    sampler: int
    # The index of the node and TRS property that an animation channel targets.
    target: AnimationChannelTarget


class AnimationChannelOptional(TypedDict, total=False):
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AnimationChannel(AnimationChannelRequired, AnimationChannelOptional):
    pass


class AnimationSamplerInterpolation(StrEnum):
    LINEAR = "LINEAR"
    STEP = "STEP"
    CUBICSPLINE = "CUBICSPLINE"


class AnimationSamplerRequired(TypedDict):
    # The index of an accessor containing keyframe input values, e.g., time.
    input: int
    # The index of an accessor, containing keyframe output values.
    output: int


class AnimationSamplerOptional(TypedDict, total=False):
    # Interpolation algorithm.
    # default=LINEAR
    interpolation: AnimationSamplerInterpolation
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class AnimationSampler(AnimationSamplerRequired, AnimationSamplerOptional):
    pass


class AnimationRequired(TypedDict):
    # An array of channels, each of which targets an animation's sampler at a node's property. Different channels of the same animation can't have equal targets.
    channels: List[AnimationChannel]
    # An array of samplers that combines input and output accessors with an interpolation algorithm to define a keyframe graph (but not its target).
    samplers: List[AnimationSampler]


class AnimationOptional(TypedDict, total=False):
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Animation(AnimationRequired, AnimationOptional):
    pass


class AssetRequired(TypedDict):
    # The glTF version that this asset targets.
    version: str


class AssetOptional(TypedDict, total=False):
    # A copyright message suitable for display to credit the content creator.
    copyright: str
    # Tool that generated this glTF model.  Useful for debugging.
    generator: str
    # The minimum glTF version that this asset targets.
    minVersion: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Asset(AssetRequired, AssetOptional):
    pass


class BufferRequired(TypedDict):
    # The length of the buffer in bytes.
    byteLength: int


class BufferOptional(TypedDict, total=False):
    # The uri of the buffer.
    uri: str
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Buffer(BufferRequired, BufferOptional):
    pass


class BufferViewTarget(IntEnum):
    ARRAY_BUFFER = 34962
    ELEMENT_ARRAY_BUFFER = 34963


class BufferViewRequired(TypedDict):
    # The index of the buffer.
    buffer: int
    # The total byte length of the buffer view.
    byteLength: int


class BufferViewOptional(TypedDict, total=False):
    # The offset into the buffer in bytes.
    byteOffset: int
    # The stride, in bytes.
    byteStride: int
    # The target that the GPU buffer should be bound to.
    target: BufferViewTarget
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class BufferView(BufferViewRequired, BufferViewOptional):
    pass


class CameraOrthographicRequired(TypedDict):
    # The floating-point horizontal magnification of the view. Must not be zero.
    xmag: float
    # The floating-point vertical magnification of the view. Must not be zero.
    ymag: float
    # The floating-point distance to the far clipping plane. `zfar` must be greater than `znear`.
    zfar: float
    # The floating-point distance to the near clipping plane.
    znear: float


class CameraOrthographicOptional(TypedDict, total=False):
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class CameraOrthographic(CameraOrthographicRequired, CameraOrthographicOptional):
    pass


class CameraPerspectiveRequired(TypedDict):
    # The floating-point vertical field of view in radians.
    yfov: float
    # The floating-point distance to the near clipping plane.
    znear: float


class CameraPerspectiveOptional(TypedDict, total=False):
    # The floating-point aspect ratio of the field of view.
    aspectRatio: float
    # The floating-point distance to the far clipping plane.
    zfar: float
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class CameraPerspective(CameraPerspectiveRequired, CameraPerspectiveOptional):
    pass


class CameraType(StrEnum):
    perspective = "perspective"
    orthographic = "orthographic"


class CameraRequired(TypedDict):
    # Specifies if the camera uses a perspective or orthographic projection.
    type: CameraType


class CameraOptional(TypedDict, total=False):
    # An orthographic camera containing properties to create an orthographic projection matrix.
    orthographic: CameraOrthographic
    # A perspective camera containing properties to create a perspective projection matrix.
    perspective: CameraPerspective
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Camera(CameraRequired, CameraOptional):
    pass


class ImageMimeType(StrEnum):
    ImageJpeg = "image/jpeg"
    ImagePng = "image/png"


class ImageRequired(TypedDict):
    pass


class ImageOptional(TypedDict, total=False):
    # The uri of the image.
    uri: str
    # The image's MIME type. Required if `bufferView` is defined.
    mimeType: ImageMimeType
    # The index of the bufferView that contains the image. Use this instead of the image's uri property.
    bufferView: int
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Image(ImageRequired, ImageOptional):
    pass


class KHR_materials_unlitGlTFExtensionRequired(TypedDict):
    pass


class KHR_materials_unlitGlTFExtensionOptional(TypedDict, total=False):
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class KHR_materials_unlitGlTFExtension(
    KHR_materials_unlitGlTFExtensionRequired, KHR_materials_unlitGlTFExtensionOptional
):
    pass


class materialsItemExtensionRequired(TypedDict):
    pass


class materialsItemExtensionOptional(TypedDict, total=False):
    # glTF extension that defines the unlit material model.
    KHR_materials_unlit: KHR_materials_unlitGlTFExtension


class materialsItemExtension(
    materialsItemExtensionRequired, materialsItemExtensionOptional
):
    pass


class TextureInfoRequired(TypedDict):
    # The index of the texture.
    index: int


class TextureInfoOptional(TypedDict, total=False):
    # The set index of texture's TEXCOORD attribute used for texture coordinate mapping.
    texCoord: int
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class TextureInfo(TextureInfoRequired, TextureInfoOptional):
    pass


class MaterialPBRMetallicRoughnessRequired(TypedDict):
    pass


class MaterialPBRMetallicRoughnessOptional(TypedDict, total=False):
    # The material's base color factor.
    # default=[1.0, 1.0, 1.0, 1.0]
    baseColorFactor: List[float]
    # Reference to a texture.
    baseColorTexture: TextureInfo
    # The metalness of the material.
    # default=1.0
    metallicFactor: float
    # The roughness of the material.
    # default=1.0
    roughnessFactor: float
    # Reference to a texture.
    metallicRoughnessTexture: TextureInfo
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class MaterialPBRMetallicRoughness(
    MaterialPBRMetallicRoughnessRequired, MaterialPBRMetallicRoughnessOptional
):
    pass


class MaterialNormalTextureInfoRequired(TypedDict):
    # The index of the texture.
    index: int


class MaterialNormalTextureInfoOptional(TypedDict, total=False):
    # The set index of texture's TEXCOORD attribute used for texture coordinate mapping.
    texCoord: int
    # The scalar multiplier applied to each normal vector of the normal texture.
    # default=1.0
    scale: float
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class MaterialNormalTextureInfo(
    MaterialNormalTextureInfoRequired, MaterialNormalTextureInfoOptional
):
    pass


class MaterialOcclusionTextureInfoRequired(TypedDict):
    # The index of the texture.
    index: int


class MaterialOcclusionTextureInfoOptional(TypedDict, total=False):
    # The set index of texture's TEXCOORD attribute used for texture coordinate mapping.
    texCoord: int
    # A scalar multiplier controlling the amount of occlusion applied.
    # default=1.0
    strength: float
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class MaterialOcclusionTextureInfo(
    MaterialOcclusionTextureInfoRequired, MaterialOcclusionTextureInfoOptional
):
    pass


class MaterialAlphaMode(StrEnum):
    OPAQUE = "OPAQUE"
    MASK = "MASK"
    BLEND = "BLEND"


class MaterialRequired(TypedDict):
    pass


class MaterialOptional(TypedDict, total=False):
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]
    # A set of parameter values that are used to define the metallic-roughness material model from Physically-Based Rendering (PBR) methodology.
    pbrMetallicRoughness: MaterialPBRMetallicRoughness
    # Reference to a texture.
    normalTexture: MaterialNormalTextureInfo
    # Reference to a texture.
    occlusionTexture: MaterialOcclusionTextureInfo
    # Reference to a texture.
    emissiveTexture: TextureInfo
    # The emissive color of the material.
    # default=[0.0, 0.0, 0.0]
    emissiveFactor: List[float]
    # The alpha rendering mode of the material.
    # default=OPAQUE
    alphaMode: MaterialAlphaMode
    # The alpha cutoff value of the material.
    # default=0.5
    alphaCutoff: float
    # Specifies whether the material is double sided.
    doubleSided: bool


class Material(MaterialRequired, MaterialOptional):
    pass


class MeshPrimitiveMode(IntEnum):
    POINTS = 0
    LINES = 1
    LINE_LOOP = 2
    LINE_STRIP = 3
    TRIANGLES = 4
    TRIANGLE_STRIP = 5
    TRIANGLE_FAN = 6


class MeshPrimitiveRequired(TypedDict):
    # A dictionary object, where each key corresponds to mesh attribute semantic and each value is the index of the accessor containing attribute's data.
    attributes: Dict[
        Literal["POSITION", "NORMAL", "TEXCOORD_0", "JOINTS_0", "WEIGHTS_0"],
        int,
    ]


class MeshPrimitiveOptional(TypedDict, total=False):
    # The index of the accessor that contains the indices.
    indices: int
    # The index of the material to apply to this primitive when rendering.
    material: int
    # The type of primitives to render.
    # default=4
    mode: MeshPrimitiveMode
    # An array of Morph Targets, each  Morph Target is a dictionary mapping attributes (only `POSITION`, `NORMAL`, and `TANGENT` supported) to their deviations in the Morph Target.
    targets: List[Dict[str, int]]
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class MeshPrimitive(MeshPrimitiveRequired, MeshPrimitiveOptional):
    pass


class MeshRequired(TypedDict):
    # An array of primitives, each defining geometry to be rendered with a material.
    primitives: List[MeshPrimitive]


class MeshOptional(TypedDict, total=False):
    # Array of weights to be applied to the Morph Targets.
    weights: List[float]
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Mesh(MeshRequired, MeshOptional):
    pass


class NodeRequired(TypedDict):
    pass


class NodeOptional(TypedDict, total=False):
    # The index of the camera referenced by this node.
    camera: int
    # The indices of this node's children.
    children: List[int]
    # The index of the skin referenced by this node.
    skin: int
    # A floating-point 4x4 transformation matrix stored in column-major order.
    # default=[1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    matrix: List[float]
    # The index of the mesh in this node.
    mesh: int
    # The node's unit quaternion rotation in the order (x, y, z, w), where w is the scalar.
    # default=[0.0, 0.0, 0.0, 1.0]
    rotation: List[float]
    # The node's non-uniform scale, given as the scaling factors along the x, y, and z axes.
    # default=[1.0, 1.0, 1.0]
    scale: List[float]
    # The node's translation along the x, y, and z axes.
    # default=[0.0, 0.0, 0.0]
    translation: List[float]
    # The weights of the instantiated Morph Target. Number of elements must match number of Morph Targets of used mesh.
    weights: List[float]
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Node(NodeRequired, NodeOptional):
    pass


class SamplerMagFilter(IntEnum):
    NEAREST = 9728
    LINEAR = 9729


class SamplerMinFilter(IntEnum):
    NEAREST = 9728
    LINEAR = 9729
    NEAREST_MIPMAP_NEAREST = 9984
    LINEAR_MIPMAP_NEAREST = 9985
    NEAREST_MIPMAP_LINEAR = 9986
    LINEAR_MIPMAP_LINEAR = 9987


class SamplerWrapS(IntEnum):
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    REPEAT = 10497


class SamplerWrapT(IntEnum):
    CLAMP_TO_EDGE = 33071
    MIRRORED_REPEAT = 33648
    REPEAT = 10497


class SamplerRequired(TypedDict):
    pass


class SamplerOptional(TypedDict, total=False):
    # Magnification filter.
    magFilter: SamplerMagFilter
    # Minification filter.
    minFilter: SamplerMinFilter
    # s wrapping mode.
    # default=10497
    wrapS: SamplerWrapS
    # t wrapping mode.
    # default=10497
    wrapT: SamplerWrapT
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Sampler(SamplerRequired, SamplerOptional):
    pass


class SceneRequired(TypedDict):
    pass


class SceneOptional(TypedDict, total=False):
    # The indices of each root node.
    nodes: List[int]
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Scene(SceneRequired, SceneOptional):
    pass


class SkinRequired(TypedDict):
    # Indices of skeleton nodes, used as joints in this skin.
    joints: List[int]


class SkinOptional(TypedDict, total=False):
    # The index of the accessor containing the floating-point 4x4 inverse-bind matrices.  The default is that each matrix is a 4x4 identity matrix, which implies that inverse-bind matrices were pre-applied.
    inverseBindMatrices: int
    # The index of the node used as a skeleton root.
    skeleton: int
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Skin(SkinRequired, SkinOptional):
    pass


class TextureRequired(TypedDict):
    pass


class TextureOptional(TypedDict, total=False):
    # The index of the sampler used by this texture. When undefined, a sampler with repeat wrapping and auto filtering should be used.
    sampler: int
    # The index of the image used by this texture. When undefined, it is expected that an extension or other mechanism will supply an alternate texture source, otherwise behavior is undefined.
    source: int
    # The user-defined name of this object.
    name: str
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class Texture(TextureRequired, TextureOptional):
    pass


class glTFRequired(TypedDict):
    # Metadata about the glTF asset.
    asset: Asset


class glTFOptional(TypedDict, total=False):
    # Names of glTF extensions used somewhere in this asset.
    extensionsUsed: List[str]
    # Names of glTF extensions required to properly load this asset.
    extensionsRequired: List[str]
    # An array of accessors.
    accessors: List[Accessor]
    # An array of keyframe animations.
    animations: List[Animation]
    # An array of buffers.
    buffers: List[Buffer]
    # An array of bufferViews.
    bufferViews: List[BufferView]
    # An array of cameras.
    cameras: List[Camera]
    # An array of images.
    images: List[Image]
    # An array of materials.
    materials: List[Material]
    # An array of meshes.
    meshes: List[Mesh]
    # An array of nodes.
    nodes: List[Node]
    # An array of samplers.
    samplers: List[Sampler]
    # The index of the default scene.
    scene: int
    # An array of scenes.
    scenes: List[Scene]
    # An array of skins.
    skins: List[Skin]
    # An array of textures.
    textures: List[Texture]
    # Dictionary object with extension-specific objects.
    extensions: Dict[str, Any]
    # Application-specific data.
    extras: Dict[str, Any]


class glTF(glTFRequired, glTFOptional):
    pass


if __name__ == "__main__":
    pass
