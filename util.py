"""
Author: Dietrich Geisler
Last Edited: December 2024

Utility functions for Image and Pixel
Includes functions for reading and writing bitmap image files
"""

from pixel import Pixel
from image import Image

def read_image(filename : str):
    """
    Returns the image produced by reading the given bmp file
      specified in https://en.wikipedia.org/wiki/BMP_file_format

    Requires that filename is a string ending with ".bmp"

    This function will fail if the Image and Pixel initializer
      methods have not been implemented

    For simplicity, this method requires that the given bitmap 
      does not use any of the standard encoding methods
    
    If any encoding has been applied to the bitmap, this
      function will raise a ValueError

    As usual, if the file is not found, a FileNotFound error will be raised

    Finally, if the filename is not a bmp file, a ValueError will be raised
    """
    assert isinstance(filename, str)
    if not filename.endswith(".bmp"):
        raise ValueError("Invalid filename, must end with .bmp")

    with open(filename, 'rb') as f:
        # Technically dangerous, but a bit annoying to avoid
        data = f.read()

    # Check the BMP file validity
    validity = data[0x0:0x2].decode('utf-8') # First two bytes to verify image type
    if validity != "BM": # BM == BitMap
        raise ValueError(f"File appears to not be a bitmap file, got {validity}")

    get_bytes = lambda x: int.from_bytes(x, 'little')

    file_size = get_bytes(data[0x2:0x6]) # Next four bytes verify image size
    if file_size != len(data):
        raise ValueError(f"Bitmap header has the wrong size \
of {file_size}, {len(data)} expected")

    # Ignore data[6:10]
    data_offset = get_bytes(data[0xA:0xE]) # The starting point of the pixel data
    
    header_size = get_bytes(data[0xE:0x12])
    if data_offset - header_size != 14:
        raise ValueError(f"Mismatch between data_offset and header_size: \
{data_offset} - {header_size} should be 14")

    # Read the header
    image_width = get_bytes(data[0x12:0x16])
    image_height = get_bytes(data[0x16:0x1A])
    planes = get_bytes(data[0x1A:0x1C])
    if planes != 1:
        raise ValueError(f"Unexpected plane count {planes}")
    pixel_bits = get_bytes(data[0x1C:0x1E])
    if pixel_bits not in (24, 32):
        raise ValueError(f"Unsupported pixel size {pixel_bits}")
    pixel_bytes = pixel_bits // 8
    compression = get_bytes(data[0x1E:0x22])
    if compression != 0:
        raise ValueError(f"Compression factor expected 0, got {compression}")
    # ignore data[0x22:0x26] (image_size is garbage)
    resolution = [get_bytes(data[0x26:0x2A]), get_bytes(data[0x2A:0x2E])]
    colors = get_bytes(data[0x2E:0x32])
    if colors != 0:
        raise ValueError(f"Unexpected color count {colors}")
    # ignore data[0x32:0x36] (garbage)

    # Here we do something very dangerous -- just throw out the rest of the header!
    # This could lose information, but here's hoping it works out
    image_data = data[data_offset:]
    
    # Now get the pixels
    image = []
    image_row = []
    col = 0
    for offset in range(0, len(image_data), pixel_bytes):
        pixel_vals = image_data[offset:offset+pixel_bytes]
        a = 0
        if pixel_bytes == 4:
            a = pixel_vals[3]
        pixel= Pixel(pixel_vals[2], pixel_vals[1], pixel_vals[0])
        image_row.append(pixel)
        col += 1
        if col >= image_width:
            image.append(image_row)
            image_row = []
            col = 0

    # Check properties of the pixels
    if len(image) != image_height:
        raise ValueError(f"Data error: expected a height of {image_height} pixels, \
got a height of {len(image)}")
    for row in image:
        if len(row) != len(image[0]):
            raise ValueError(f"Data error: non-rectangular data has row length {len(row)}")

    # Build and return the image
    return Image(image, resolution)

def write_image(filename : str, image : Image):
    """
    Writes the given Image to "filename"

    Requires that filename ends with .bmp and that image is an Image

    Creates a bmp image using the 40-bit header,
      size of the given Image in pixels
      and the resolution stored in Image
    """
    assert isinstance(filename, str)
    if not filename.endswith(".bmp"):
        raise ValueError("Invalid filename, must end with .bmp")
    assert isinstance(image, Image)

    data = image._data
    # Check the data, just to be sure
    assert len(data) > 0
    assert len(data[0]) > 0
    for row in data:
        assert len(row) == len(data[0])
    itb = lambda s, x : int(x).to_bytes(s, 'little')

    # Build the file header
    validity = "BM".encode('utf-8')
    # Since we're using 32-bit pixels and a header size of 40
    #  should be fine (?)
    file_size = itb(4, 4 * len(data) * len(data[0]) + 54)
    reserved = itb(4, 0)
    offset = itb(4, 54)
    file_header = validity + file_size + reserved + offset

    # Build the info header
    header_size = itb(4, 40)
    image_width = itb(4, len(data[0]))
    image_height = itb(4, len(data))
    planes = itb(2, 1)
    pixel_bits = itb(2, 32)
    compression = itb(4, 0)
    image_size = itb(4, 0)
    res_width = itb(4, image._resolution[0])
    res_height = itb(4, image._resolution[1])
    colors = itb(4, 0)
    ignored = itb(4, 0)
    info_header = header_size + image_width + image_height + planes + pixel_bits \
        + compression + image_size + res_width + res_height + colors + ignored
    
    # Get the data from the image
    data_bytes = b''
    for row in data:
        for pixel in row:
            data_bytes += itb(1, pixel._blue) + itb(1, pixel._green) \
                + itb(1, pixel._red) + itb(1, 255)

    with open(filename, "wb") as f:
        f.write(file_header)
        f.write(info_header)
        f.write(data_bytes)