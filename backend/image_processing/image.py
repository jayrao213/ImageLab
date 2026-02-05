"""
Author: Jay Rao

Definition of an Image class for storing and manipulating single images
"""

from .pixel import Pixel
import io, requests
from PIL import Image as PILImage

class Image:
    _data : list[list[Pixel]]
    """
    The core pixel data contained in this Image
    
    Every row in _data must be the same length, and no row can have a zero length
    """

    _resolution : list[int]
    """
    The resolution of this Image (which may be different from the size of _data)
    We store the resolution separately for use in the BMP datafile

    The length of _resolution must be 2 ([width and height])
    """

    def __init__(self, image : list[list[Pixel]], resolution : list[int]):
        """
        Initializes this Image with the given matrix of Pixels
          and resolution (the latter is necessary for BMP metedata)

        Image must be a list of list of Pixels
          each row of the image must be of the same length
          neither the image nor any row may be of length 0

        resolution is a list consisting of exactly two integers
        """
        assert type(image) == list
        assert len(image) > 0
        for row in image:
            assert type(row) == list
            assert len(row) > 0
            assert len(row) == len(image[0])
            for pixel in row:
                assert type(pixel) == Pixel

        assert type(resolution) == list
        assert len(resolution) == 2
        assert type(resolution[0]) == int
        assert type(resolution[1]) == int

        self._data = image
        self._resolution = resolution

    
    def __str__(self) -> str:
        """
        Returns a string representation of the dimensions 
          of the pixels matrix forming this Image

        Uses the size of _data rather than the _resolution of this image
        """
        return f"{len(self._data)}x{len(self._data[0])} Image"


    def __repr__(self) -> str:
        """
        Returns the debugging representation of this Image
        Includes both the raw data matrix and the resolution of this Image
          (Hint: don't overthink this method, it should be simple)
        """
        return f"Image({self._data}, {self._resolution})"
    
    
    def resize(self, new_width: int, new_height: int):
        """
        Resize the image to new dimensions using nearest neighbor sampling.
        """
        if new_width < 1 or new_height < 1:
            raise ValueError("Width and height must be at least 1")

        old_height = len(self._data)
        old_width = len(self._data[0])

        pil_img = PILImage.new("RGB", (old_width, old_height))
        for r in range(old_height):
            for c in range(old_width):
                p = self._data[old_height - 1 - r][c]
                pil_img.putpixel((c, r), (p._red, p._green, p._blue))

        resized_pil = pil_img.resize((new_width, new_height), PILImage.LANCZOS)

        new_data: list[list[Pixel]] = []
        for rr in range(new_height):
            y = new_height - 1 - rr
            row: list[Pixel] = []
            for x in range(new_width):
                r8, g8, b8 = resized_pil.getpixel((x, y))
                row.append(Pixel(int(r8), int(g8), int(b8)))
            new_data.append(row)

        self._data = new_data


    def add_color(self, add_color : Pixel):
        """
        Adds the given Pixel "add_color" to each Pixel in this Image 
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                self._data[r][c] = self._data[r][c] + add_color
   

    def red_shift(self, amount : float):
        """
        Adds 'amount' to the red component of each Pixel in this Image
        amount must be an integer >= 0
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                pixel = self._data[r][c]
                self._data[r][c] = Pixel(pixel._red + int(amount), pixel._green, pixel._blue)


    def green_shift(self, amount: float):
        """
        Adds 'amount' to the green component of each Pixel in this Image
        amount must be an integer >= 0
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                pixel = self._data[r][c]
                self._data[r][c] = Pixel(pixel._red, pixel._green + int(amount), pixel._blue)


    def blue_shift(self, amount: float):
        """
        Adds 'amount' to the blue component of each Pixel in this Image
        amount must be an integer >= 0
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                pixel = self._data[r][c]
                self._data[r][c] = Pixel(pixel._red, pixel._green, pixel._blue + int(amount))


    def shift_brightness(self, amount : float):
        """
        Modified this image by shifting the brightness
          of each Pixel in this Image by the given amount

        amount must be a float >= 0

        If amount is greater than 1, the image is brightened
          while if the amount is between 0 and 1, the image is darkened
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                self._data[r][c] = self._data[r][c] * amount

    
    def make_monochrome(self):
        """
        Shifts the pixels in this Image to be Monochrome
          
        This is done by averaging all of the components for the Pixel
        That is, for each pixel, we first calculate
          average = (pixel.red + pixel.green + pixel.blue) // 3
        
        We then update the pixel such that each red, green, and blue
          component contains exactly "average"
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                p = self._data[r][c]
                avg = (p._red + p._green + p._blue) // 3
                self._data[r][c] = Pixel(avg, avg, avg)


    def mirror_horizontal(self):
        """
        Modifies this Image by mirroring it over the x-axis
        """

        rows = len(self._data)
        for i in range(rows // 2):
            self._data[i], self._data[rows - 1 - i] = self._data[rows - 1 - i], self._data[i]


    def mirror_vertical(self):
        """
        Modifies this Image by mirroring it over the y-axis
        """
        cols = len(self._data[0])
        for row in self._data:
            for i in range(cols // 2):
                row[i], row[cols - 1 - i] = row[cols - 1 - i], row[i]


    def tile(self, size : int):
        """
        Modifies this image by darkening and lighting "tiles" of size "size" in the Image

        Specifically, each Pixel in the lower-left tile will be darkened (multiplied by 0.5)
          and each pixel in an alternating tile will be brightened (multiplied by 2.0)

        If the number of rows or columns is not divisible by size,
          the last row or column of tiles will be filled as much as possible

        For example, if we have a 4x5 image and are tiling with size 2
        We can notate Pixels as being darkened with 0 and brightened with 1:
          0 0 1 1 0
          0 0 1 1 0
          1 1 0 0 1
          1 1 0 0 1
        """
        for r in range(len(self._data)):
            for c in range(len(self._data[0])):
                tile_row = (r // size)
                tile_col = (c // size)
                if (tile_row + tile_col) % 2 == 0:
                    self._data[r][c] = self._data[r][c] * 0.5
                else:
                    self._data[r][c] = self._data[r][c] * 2.0


    def blur(self):
        """
        Modifies this Image by blurring each Pixel in the Image

        To blur a Pixel, average the red-green-blue components of 
          this Pixel and every adjacent Pixel

        Note that adjacency for blurring includes Pixels "diagonally" adjacent

        If the average value of a Pixel is not an integer, it should be rounded down
        """
        rows = len(self._data)
        cols = len(self._data[0])
        new_data = []

        for r in range(rows):
            new_row = []
            for c in range(cols):
                red = 0
                green = 0
                blue = 0
                count = 0
                for cr in [-1, 0, 1]:
                    for cc in [-1, 0, 1]:
                        nr, nc = r + cr, c + cc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            p = self._data[nr][nc]
                            red += p._red
                            green += p._green
                            blue += p._blue
                            count += 1
                new_row.append(Pixel(red // count, green // count, blue // count))
            new_data.append(new_row)

        self._data = new_data


    def negative(self):
        """Invert colors (photo negative)."""
        rows, cols = len(self._data), len(self._data[0])
        for r in range(rows):
            for c in range(cols):
                p = self._data[r][c]
                self._data[r][c] = Pixel(255 - p._red, 255 - p._green, 255 - p._blue)


    def sepia(self):
        """Classic sepia tone."""
        rows, cols = len(self._data), len(self._data[0])
        for r in range(rows):
            for c in range(cols):
                p = self._data[r][c]
                tr = 0.393 * p._red + 0.769 * p._green + 0.189 * p._blue
                tg = 0.349 * p._red + 0.686 * p._green + 0.168 * p._blue
                tb = 0.272 * p._red + 0.534 * p._green + 0.131 * p._blue
                self._data[r][c] = Pixel(int(tr), int(tg), int(tb))


    def rotate(self, degrees: int):
        """
        Rotate the image in 90° steps.
        - Positive degrees = clockwise
        - Negative degrees = counter-clockwise
        """
        if not isinstance(degrees, int):
            raise ValueError("degrees must be an int")

        if degrees % 90 != 0:
            raise ValueError("Rotation only supports multiples of 90 degrees")

        steps_cw = (-degrees // 90) % 4  

        if steps_cw == 0:
            return  

        def rot90(data):
            r, c = len(data), len(data[0])
            return [[data[r - 1 - rr][cc] for rr in range(r)] for cc in range(c)]

        new_data = self._data
        for _ in range(steps_cw):
            new_data = rot90(new_data)

        self._data = new_data


    def pixelate(self, block: int = 8):
        """
        Pixelate by averaging non-overlapping block-size tiles.
        block >= 1. Larger = chunkier pixels.
        """
        if block < 1:
            block = 1

        rows, cols = len(self._data), len(self._data[0])

        r0 = 0
        while r0 < rows:
            c0 = 0
            r1 = min(r0 + block, rows)
            while c0 < cols:
                c1 = min(c0 + block, cols)

                sr = sg = sb = 0
                count = 0
                for r in range(r1 - r0):
                    for c in range(c1 - c0):
                        p = self._data[r0 + r][c0 + c]
                        sr += p._red
                        sg += p._green
                        sb += p._blue
                        count += 1
                ar = int(sr / count)
                ag = int(sg / count)
                ab = int(sb / count)

                avg = Pixel(ar, ag, ab)
                for r in range(r1 - r0):
                    for c in range(c1 - c0):
                        self._data[r0 + r][c0 + c] = avg

                c0 = c1
                c1 = min(c0 + block, cols)
            r0 = r1
            r1 = min(r0 + block, rows)
