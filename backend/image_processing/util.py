"""
Author: Jay Rao (updated for Pillow)

Utility functions for Image and Pixel
"""

from PIL import Image as PILImage
from .pixel import Pixel
from .image import Image

_INCH_TO_METER = 0.0254

def _dpi_to_ppm(xdpi: float, ydpi: float) -> list[int]:
    return [int(xdpi / _INCH_TO_METER), int(ydpi / _INCH_TO_METER)]

def _ppm_to_dpi(xppm: int, yppm: int) -> tuple[float, float]:
    return (xppm * _INCH_TO_METER, yppm * _INCH_TO_METER)

def read_image(filename: str) -> Image:
    """
    Returns an Image built from the given file.
    Preserves the project's lower-left origin convention.
    _resolution stores pixels-per-meter when available; defaults to 3779 (~96 DPI).
    """
    assert isinstance(filename, str)

    with PILImage.open(filename) as pil_img:
        pil_img = pil_img.convert("RGB")
        width, height = pil_img.size

        data: list[list[Pixel]] = []
        for r in range(height): 
            y = height - 1 - r   
            row: list[Pixel] = []
            for x in range(width):
                r8, g8, b8 = pil_img.getpixel((x, y))
                row.append(Pixel(r8, g8, b8))
            data.append(row)

        info = getattr(pil_img, "info", {}) or {}
        if isinstance(info.get("dpi"), tuple) and len(info["dpi"]) == 2:
            xdpi, ydpi = info["dpi"]
            resolution = _dpi_to_ppm(float(xdpi), float(ydpi))
        else:
            resolution = [3779, 3779]

        return Image(data, resolution)

def write_image(filename: str, image: Image):
    """
    Writes the given Image to 'filename' (format inferred from extension).
    Preserves the project's lower-left origin and attempts to store DPI from _resolution.
    """
    assert isinstance(filename, str)
    assert isinstance(image, Image)

    height = len(image._data)
    assert height > 0
    width = len(image._data[0])
    assert width > 0
    for row in image._data:
        assert len(row) == width

    pil_img = PILImage.new("RGB", (width, height))

    for r, row in enumerate(image._data):
        y = height - 1 - r 
        for x, p in enumerate(row):
            pil_img.putpixel((x, y), (p._red, p._green, p._blue))

    dpi_arg = None
    try:
        if (isinstance(image._resolution, list) and len(image._resolution) == 2
                and all(isinstance(v, int) for v in image._resolution)):
            xppm, yppm = image._resolution
            dpi_arg = _ppm_to_dpi(xppm, yppm)
    except Exception:
        dpi_arg = None

    save_kwargs = {}
    if dpi_arg:
        save_kwargs["dpi"] = dpi_arg  

    pil_img.save(filename, **save_kwargs)
