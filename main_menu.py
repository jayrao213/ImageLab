from pixel import Pixel
from image import Image
import util as util

def print_menu():
    print("\n" + "="*40)
    print("🖼️  CS150 Image Filter Menu")
    print("="*40)
    print("1. Add Color")
    print("2. Red Shift")
    print("3. Shift Brightness")
    print("4. Make Monochrome")
    print("5. Mirror Horizontally")
    print("6. Mirror Vertically")
    print("7. Tile")
    print("8. Blur")
    print("9. Save and Exit")
    print("="*40)

def main():
    in_file = input("Enter input .bmp file name: ")
    image = util.read_image(in_file)

    while True:
        print_menu()
        choice = input("Choose a filter (1–9): ")

        if choice == '1':
            r = int(input("Red to add: "))
            g = int(input("Green to add: "))
            b = int(input("Blue to add: "))
            image.add_color(Pixel(r, g, b))
        elif choice == '2':
            amount = float(input("Red shift amount: "))
            image.red_shift(amount)
        elif choice == '3':
            factor = float(input("Brightness factor: "))
            image.shift_brightness(factor)
        elif choice == '4':
            image.make_monochrome()
        elif choice == '5':
            image.mirror_horizontal()
        elif choice == '6':
            image.mirror_vertical()
        elif choice == '7':
            size = int(input("Tile size: "))
            image.tile(size)
        elif choice == '8':
            image.blur()
        elif choice == '9':
            out_file = input("Enter output .bmp file name: ")
            util.write_image(out_file, image)
            print(f"😁 Image saved to '{out_file}'. Goodbye!")
            break
        else:
            print("😔 Invalid choice. Try again.")

if __name__ == "__main__":
    main()