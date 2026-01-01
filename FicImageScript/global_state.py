from typing import TypedDict, Literal

ImageFormat = Literal["webp", "jpeg", "jpg", "png"]


class State(TypedDict):
    compress_images: bool
    default_image_format: ImageFormat
    max_image_size: int
    verbose: bool
    zip_embed_images: bool
    version: str


state: State = {
    "compress_images": True,
    "default_image_format": "webp",
    "max_image_size": 100_000,
    "verbose": False,
    "zip_embed_images": False,
    "version": "5.0.0",
}
