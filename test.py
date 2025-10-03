
"""
Testcases for image and pixel

To run these tests, simply run test.py
"""

import os
from pixel import Pixel
from image import Image
import util as util

# Whether or not to write images to image_tests
WRITE_IMAGES = True

# Set WRITE_IMAGES to False (uncomment the following line
#   if you want your tests to run faster, since writing images takes forever
# WRITE_IMAGES = False


def test_pixel_init():
    print("\t\t" + "Testing Pixel initialization")
    # Basics
    p = Pixel(10, 20, 30)
    assert 10 == p._red
    assert 20 == p._green
    assert 30 == p._blue

    # Clamping
    p = Pixel(-5, 300, 100)
    assert 0 == p._red
    assert 255 == p._green
    assert 100 == p._blue


def test_pixel_reprs():
    print("\t\t" + "Testing Pixel representations")
    p1 = Pixel(3, 5, 7)
    p2 = Pixel(100, 200, 300)

    print("\t\t\t" + "pixel str")
    # __str__
    assert "(3, 5, 7)" == str(p1)
    assert "(100, 200, 255)" == str(p2)

    print("\t\t\t" + "pixel repr")
    # __repr__
    assert "Pixel(3, 5, 7)" == repr(p1)
    assert "Pixel(100, 200, 255)" == repr(p2)


def test_pixel_binary():
    print("\t\t" + "Testing Pixel binary operations")
    p0 = Pixel(0, 0, 0)
    p1 = Pixel(10, 10, 10)
    p2 = Pixel(300, 0, 100)

    print("\t\t\t" + "pixel eq")
    # Equality
    assert p0 == p0
    assert Pixel(0, 0, 0) == p0
    assert Pixel(10, 10, 10) == p1
    # Also testing clamping
    assert Pixel(255, 0, 100) == p2

    print("\t\t\t" + "pixel add")
    # Addition
    # Since we already tested equality, we can use it!
    assert Pixel(0, 0, 0) == p0 + p0
    # Zero addition
    assert Pixel(10, 10, 10) == p0 + p1
    # Testing commutativity
    assert Pixel(10, 10, 10) == p1 + p0
    assert Pixel(20, 20, 20) == p1 + p1
    # Clamping, once again
    assert Pixel(255, 10, 110) == p1 + p2
    # Commutativity
    assert Pixel(255, 10, 110) == p2 + p1
    # Chaining
    assert Pixel(30, 30, 30) == p1 + p1 + p1
    assert Pixel(255, 20, 220) == (p1 + p2) + (p2 + p1)

    print("\t\t\t" + "pixel mul")
    # Multiplication
    # Multiply with/by 0
    assert Pixel(0, 0, 0) == p0 * 2.0
    assert Pixel(0, 0, 0) == p1 * 0.0
    # Multiply by integer with clamping
    assert Pixel(20, 255, 0) == Pixel(10, 200, 0) * 2
    # Multiply by float with rounding
    assert Pixel(20, 255, 0) == Pixel(10, 200, 0) * 2.01
    # Rounding down
    assert Pixel(10, 21, 32) == Pixel(5, 10, 15) * 2.15


def test_image_init():
    print("\t\t" + "Testing Image initialization")

    # Basics
    data = [[Pixel(0, 0, 0)]]
    image = Image(data, [1, 1])
    assert Pixel(0, 0, 0) == image._data[0][0]
    assert [1, 1] == image._resolution

    # Rectangular data
    data = [[Pixel(0, 0, 0), Pixel(0, 0, 0)],
            [Pixel(1, 1, 1), Pixel(1, 1, 1)],
            [Pixel(2, 2, 2), Pixel(2, 2, 2)]]
    image = Image(data, [1, 2])
    assert data == image._data
    assert [1, 2] == image._resolution

    # Baseline image data
    image = util.read_image("resources/simple.bmp")
    data = [[Pixel(0, 0, 0), Pixel(255, 0, 0)],
            [Pixel(0, 255, 0), Pixel(0, 0, 255)]]
    resolution = [100, 100]
    assert data == image._data
    assert resolution == image._resolution

    # Large image data
    image = util.read_image("resources/python_logo.bmp")
    resolution = [3779, 3779]
    assert 101 == len(image._data)
    assert 300 == len(image._data[0])
    assert resolution == image._resolution


def test_image_reprs():
    print("\t\t" + "Testing Image representations")
    image1 = Image([[Pixel(0, 0, 0)]], [1, 1])
    image2 = Image([[Pixel(1, 2, 3)], [Pixel(4, 3, 2)]], [2, 3])

    print("\t\t\t" + "image str")
    # __str__
    assert "1x1 Image" == str(image1)
    assert "2x1 Image" == str(image2)

    print("\t\t\t" + "image repr")
    # __repr__
    assert "Image([[Pixel(0, 0, 0)]], [1, 1])" == repr(image1)
    assert "Image([[Pixel(1, 2, 3)], [Pixel(4, 3, 2)]], [2, 3])" == repr(
        image2)


def assert_image_equals(expected: Image, result: Image):
    """
    Helper function for checking if two images have entirely equal components

    In particular, we are interested in seeing if the data and resolutions are the same 
    """
    # Give a reasonable error message using repr with a newline
    data_msg = f'\nExpected:\t{expected._data}\nGot:\t\t{result._data}'
    res_msg = f'Expected resolution: {expected._resolution}, got: {result._resolution}'
    # We can just compare the data since Pixels have __eq__ defined and tested
    assert expected._data == result._data, data_msg
    assert expected._resolution == result._resolution, res_msg


def test_image_shifts():
    print("\t\t" + "Testing Image Shifts")

    # add_color
    print("\t\t\t" + "add_color")

    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.add_color(Pixel(0, 50, 80))
        util.write_image("image_tests/dragon_add_color.bmp", image)

    # unit tests
    image1 = Image([[Pixel(0, 0, 0)]], [1, 1])
    image1.add_color(Pixel(0, 0, 0))
    assert_image_equals(Image([[Pixel(0, 0, 0)]], [1, 1]), image1)

    image2 = Image([[Pixel(10, 10, 10)]], [1, 1])
    image2.add_color(Pixel(5, 5, 5))
    assert_image_equals(Image([[Pixel(15, 15, 15)]], [1, 1]), image2)

    image3 = Image([[Pixel(10, 0, 255), Pixel(5, 5, 5)]], [2, 1])
    image3.add_color(Pixel(0, 0, 50))
    assert_image_equals(Image([[Pixel(10, 0, 255), Pixel(5, 5, 55)]], [2, 1]), image3)

    # red shift
    print("\t\t\t" + "red_shift")

    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.red_shift(50)
        util.write_image("image_tests/dragon_red_shift.bmp", image)

    # unit tests
    image1 = Image([[Pixel(0, 0, 0)]], [1, 1])

    image1.red_shift(0)
    assert_image_equals(Image([[Pixel(0, 0, 0)]], [1, 1]), image1)

    image2 = Image([[Pixel(10, 0, 0)]], [1, 1])
    image2.red_shift(50)
    assert_image_equals(Image([[Pixel(60, 0, 0)]], [1, 1]), image2)

    image3 = Image([[Pixel(250, 0, 0)]], [1, 1])
    image3.red_shift(100)
    assert_image_equals(Image([[Pixel(255, 0, 0)]], [1, 1]), image3)

    # shift_brightness
    print("\t\t\t" + "shift_brightness")

    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.shift_brightness(0.5)
        util.write_image("image_tests/dragon_darker.bmp", image)

    # unit tests
    image1 = Image([[Pixel(10, 20, 30)]], [1, 1])
    image1.shift_brightness(1.0)
    assert_image_equals(Image([[Pixel(10, 20, 30)]], [1, 1]), image1)

    image2 = Image([[Pixel(20, 40, 60)]], [1, 1])
    image2.shift_brightness(0.5)
    assert_image_equals(Image([[Pixel(10, 20, 30)]], [1, 1]), image2)

    image3 = Image([[Pixel(20, 40, 60)]], [1, 1])
    image3.shift_brightness(1.5)
    assert_image_equals(Image([[Pixel(30, 60, 90)]], [1, 1]), image3)


def test_image_monochrome():
    # make_monochrome
    print("\t\t" + "Testing Image Monochrome")
    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.make_monochrome()
        util.write_image("image_tests/dragon_monochrome.bmp", image)

    # unit tests
    image1 = Image([[Pixel(10, 20, 30)]], [1, 1])
    image1.make_monochrome()
    assert_image_equals(Image([[Pixel(20, 20, 20)]], [1, 1]), image1)

    image2 = Image([[Pixel(30, 60, 90)]], [1, 1])
    image2.make_monochrome()
    assert_image_equals(Image([[Pixel(60, 60, 60)]], [1, 1]), image2)

    image3 = Image([[Pixel(255, 0, 0)]], [1, 1])
    image3.make_monochrome()
    assert_image_equals(Image([[Pixel(85, 85, 85)]], [1, 1]), image3)


def test_image_mirrors():

    print("\t\t" + "Testing Image Mirroring")

    print("\t\t\t" + "mirror_horizontal")
    # mirror_horizontal
    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.mirror_horizontal()
        util.write_image("image_tests/dragon_mirrored_horizontal.bmp", image)

    # unit tests
    image1 = Image([[Pixel(0, 0, 0)]], [1, 1])
    image1.mirror_horizontal()
    assert_image_equals(Image([[Pixel(0, 0, 0)]], [1, 1]), image1)

    image2 = Image([[Pixel(1,1,1)], [Pixel(2,2,2)], [Pixel(3,3,3)]], [1, 3])
    image2.mirror_horizontal()
    assert_image_equals(Image([[Pixel(3,3,3)], [Pixel(2,2,2)], [Pixel(1,1,1)]], [1, 3]), image2)

    image3 = Image([[Pixel(1,1,1), Pixel(2,2,2)]], [2, 1])
    image3.mirror_horizontal()
    assert_image_equals(Image([[Pixel(1,1,1), Pixel(2,2,2)]], [2, 1]), image3)

    print("\t\t\t" + "mirror_vertical")
    # mirror_vertical
    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.mirror_vertical()
        util.write_image("image_tests/dragon_mirrored_vertical.bmp", image)

    # unit tests
    image1 = Image([[Pixel(0, 0, 0)]], [1, 1])
    image1.mirror_vertical()
    assert_image_equals(Image([[Pixel(0, 0, 0)]], [1, 1]), image1)

    image2 = Image([[Pixel(1,1,1), Pixel(2,2,2)]], [2, 1])
    image2.mirror_vertical()
    assert_image_equals(Image([[Pixel(2,2,2), Pixel(1,1,1)]], [2, 1]), image2)

    image3 = Image([[Pixel(1,1,1)], [Pixel(2,2,2)]], [1, 2])
    image3.mirror_vertical()
    assert_image_equals(Image([[Pixel(1,1,1)], [Pixel(2,2,2)]], [1, 2]), image3)


def test_image_tile():

    print("\t\t" + "Testing Image Tile")

    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        image.tile(16)
        util.write_image("image_tests/dragon_tiled.bmp", image)

    image1 = Image([[Pixel(10, 20, 30)]], [1, 1])
    image2 = Image([[Pixel(1, 2, 3), Pixel(1, 2, 3)],
                    [Pixel(1, 2, 3), Pixel(1, 2, 3)]], [2, 3])

    # a single pixel gets darkened
    image1.tile(1)
    assert_image_equals(Image([[Pixel(5, 10, 15)]], [1, 1]), image1)

    # 2x2 image tiling
    image2.tile(1)
    assert_image_equals(Image([[Pixel(0, 1, 1), Pixel(2, 4, 6)],
                               [Pixel(2, 4, 6), Pixel(0, 1, 1)]], [2, 3]), image2)

    image3 = Image([[Pixel(4,4,4), Pixel(4,4,4), Pixel(4,4,4)],
                    [Pixel(4,4,4), Pixel(4,4,4), Pixel(4,4,4)],
                    [Pixel(4,4,4), Pixel(4,4,4), Pixel(4,4,4)]], [3, 3])
    image3.tile(1)
    expected_data = [
        [Pixel(2,2,2), Pixel(8,8,8), Pixel(2,2,2)],
        [Pixel(8,8,8), Pixel(2,2,2), Pixel(8,8,8)],
        [Pixel(2,2,2), Pixel(8,8,8), Pixel(2,2,2)]
    ]
    assert_image_equals(Image(expected_data, [3, 3]), image3)

    image4 = Image([[Pixel(10,10,10) for _ in range(4)] for _ in range(4)], [4, 4])
    image4.tile(2)
    expected_data = [
        [Pixel(5,5,5), Pixel(5,5,5), Pixel(20,20,20), Pixel(20,20,20)],
        [Pixel(5,5,5), Pixel(5,5,5), Pixel(20,20,20), Pixel(20,20,20)],
        [Pixel(20,20,20), Pixel(20,20,20), Pixel(5,5,5), Pixel(5,5,5)],
        [Pixel(20,20,20), Pixel(20,20,20), Pixel(5,5,5), Pixel(5,5,5)]
    ]
    assert_image_equals(Image(expected_data, [4, 4]), image4)


def test_image_blur():

    print("\t\t" + "Testing Image Blurring")
    # image test
    if WRITE_IMAGES:
        image = util.read_image("resources/dragon.bmp")
        # Applying this 5 times makes sure there's enough "strength" of blur to see
        image.blur()
        image.blur()
        image.blur()
        image.blur()
        image.blur()
        util.write_image("image_tests/dragon_blur.bmp", image)

    # unit tests
    image1 = Image([[Pixel(10, 20, 30)]], [1, 1])
    image2 = Image([
        [Pixel(1, 1, 1), Pixel(2, 2, 2), Pixel(3, 3, 3)],
        [Pixel(4, 4, 4), Pixel(5, 6, 7), Pixel(6, 6, 6)],
        [Pixel(7, 7, 7), Pixel(8, 8, 8), Pixel(9, 9, 9)]], [2, 3])

    # no change for single pixel
    image1.blur()
    assert_image_equals(Image([[Pixel(10, 20, 30)]], [1, 1]), image1)

    # 3x3 blurring is complex, but this should clarify edge cases (hopefully)
    image2.blur()
    assert_image_equals(Image([
        [Pixel(3, 3, 3), Pixel(3, 3, 3), Pixel(4, 4, 4)],
        [Pixel(4, 4, 4), Pixel(5, 5, 5), Pixel(5, 5, 5)],
        [Pixel(6, 6, 6), Pixel(6, 6, 6), Pixel(7, 7, 7)]], [2, 3]), image2)

    image3 = Image([
        [Pixel(10, 10, 10), Pixel(20, 20, 20), Pixel(30, 30, 30)],
        [Pixel(40, 40, 40), Pixel(50, 50, 50), Pixel(60, 60, 60)],
        [Pixel(70, 70, 70), Pixel(80, 80, 80), Pixel(90, 90, 90)]
    ], [3, 3])

    image3.blur()
    assert_image_equals(Image([
        [Pixel(30,30,30), Pixel(35,35,35), Pixel(40,40,40)],
        [Pixel(45,45,45), Pixel(50,50,50), Pixel(55,55,55)],
        [Pixel(60,60,60), Pixel(65,65,65), Pixel(70,70,70)]
    ], [3, 3]), image3)

    image4 = Image([
        [Pixel(255, 255, 255), Pixel(0, 0, 0), Pixel(255, 255, 255)],
        [Pixel(0, 0, 0), Pixel(0, 0, 0), Pixel(0, 0, 0)],
        [Pixel(255, 255, 255), Pixel(0, 0, 0), Pixel(255, 255, 255)]
    ], [3, 3])

    image4.blur()
    assert_image_equals(Image([
        [Pixel(63,63,63), Pixel(85,85,85), Pixel(63,63,63)],
        [Pixel(85,85,85), Pixel(113,113,113), Pixel(85,85,85)],
        [Pixel(63,63,63), Pixel(85,85,85), Pixel(63,63,63)]
    ], [3, 3]), image4)


def test_pixel():
    """
    Tests all the Pixel class methods
    """
    print("\t" + "Testing Pixel class")
    test_pixel_init()
    test_pixel_reprs()
    test_pixel_binary()
    print("\t" + "Pixel tests passed!")


def test_image():
    """
    Tests all the Image class methods
    """
    # first build the tests folder if needed
    if WRITE_IMAGES:
        if not os.path.exists('image_tests'):
            os.mkdir('image_tests')

    print("\t" + "Testing Image class")
    test_image_init()
    test_image_reprs()
    test_image_shifts()
    test_image_monochrome()
    test_image_mirrors()
    test_image_tile()
    test_image_blur()
    print("\t" + "Image tests passed!")


def main():
    # Driver function
    print("Starting tests")
    test_pixel()
    print()
    test_image()
    print("All tests passed!")


if __name__ == "__main__":
    main()