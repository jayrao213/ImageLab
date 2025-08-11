"""
Author: Jay Rao

Definition of a Pixel class for storing and manipulating individual pixels
"""

class Pixel:
    """
    A Pixel object represents a single pixel on screen with RGB colors
    """

    _red : int
    """
    _red represents the red value of the pixel (higher is more red)
    requires that 0 <= _red <= 255
    """

    _green : int
    """
    _green represents the green value of the pixel (higher is more green)
    requires that 0 <= _green <= 255
    """

    _blue : int
    """
    b represents the blue value of the pixel (higher is more blue)
    requires that 0 <= _blue <= 255
    """

    def __init__(self, red : int, green : int, blue : int):
        """
        Instantiates a Pixel with the given attributes
        Note that if any attribute is outside the allowed range
          this initialization should _clamp_ it within the valid range

        That is:
          if any value (red, green, or blue) is negative, set that attribute to 0
          similarly, if any value is above 255, set it to 255
        """
        assert type(red) == int
        assert type(green) == int
        assert type(blue) == int
        self._red = min(255, max(0, red))
        self._green = min(255, max(0, green))
        self._blue = min(255, max(0, blue))

    def __str__(self) -> str:
        """
        Returns a string representation of this Pixel

        Example:
          str(Pixel(1, 2, 3)) -> "(1, 2, 3)"
        """
        return f"({self._red}, {self._green}, {self._blue})"

    def __repr__(self) -> str:
        """
        Returns a debugging representation of this Pixel

        Example:
          repr(Pixel(1, 2, 3)) -> "Pixel(1, 2, 3)"
        """
        return f"Pixel({self._red}, {self._green}, {self._blue})"

    def __eq__(self, other : 'Pixel') -> bool:
        """
        Returns True if this Pixel and other have all of the same RGBA values
        Returns False otherwise
        Neither this pixel nor other are modified
        """
        return (self._red == other._red and 
            self._green == other._green and 
            self._blue == other._blue)

    def __add__(self, other : 'Pixel') -> 'Pixel':
        """
        Returns the Pixel resulting from adding this Pixel to another
        Neither this pixel nor other are modified
        Note that the resulting pixel will be clamped as usual

        Example:
          Pixel(0, 255, 0) + Pixel(255, 255, 0) -> Pixel(255, 255, 0)
        """
        return Pixel(
            self._red + other._red,
            self._green + other._green,
            self._blue + other._blue
        )

    def __mul__(self, amount : float) -> 'Pixel':
        """
        Returns the Pixel resulting from multiplying 
          each RGB component of this Pixel by "amount"
        This pixel is not modified
        When a non-integer value would be produced, the result is rounded down
          
        Example:
          Pixel(10, 200, 0) * 2.01
            -> Pixel(20, 255, 0)
        """
        return Pixel(
            int(self._red * amount),
            int(self._green * amount),
            int(self._blue * amount)
        ) 