"""
Author: Jay Rao
Starting Date: 6/7/2025

Definition of an Image class for storing and manipulating single images
"""

from pixel import Pixel

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
          
        Example:
          str(Image([[Pixel(1, 2, 3)], [Pixel(4, 3, 2)]], [1, 1]))
            -> "2x1 Image"
        """
        return f"{len(self._data)}x{len(self._data[0])} Image"


    def __repr__(self) -> str:
        """
        Returns the debugging representation of this Image
        Includes both the raw data matrix and the resolution of this Image
          (Hint: don't overthink this method, it should be simple)

        Example:
          repr(Image([[Pixel(1, 2, 3)], [Pixel(4, 3, 2)]], [2, 3]))
            -> "Image([[Pixel(1, 2, 3)], [Pixel(4, 3, 2)]], [2, 3])"
        """
        return f"Image({self._data}, {self._resolution})"
        

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
        # Hint: the "lower-left" Pixel of an image is actually at self._data[0][0]
        #  This is because we use the convention where (0, 0) is the lower-left of the image
          
        # Hint: there are a lot of ways to get the "current tile"
        #   I found integer division (//) to be particularly helpful though

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
        # Hint: consider building a new matrix of Pixels to avoid
        #   modifying the results of future Pixels when calculating a given Pixel
        
        # Hint: be careful of "edge" cases (teehee)

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