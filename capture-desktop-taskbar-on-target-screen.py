import os
import mss
from PIL import Image

get_screen_id = 1
get_image_width = 37
get_image_height = 37
get_image_offset_x = 935
get_image_offset_y = 1034
get_debug_out_image_name = f"monitor_${get_screen_id}_offset_${get_image_width}x${get_image_height}.png"


def capture_with_offset_and_resize():
    with mss.mss() as sct:
        # Capture only the first monitor
        print(f"Capturing screenshot of monitor {get_screen_id}...")
        screenshot = sct.grab(sct.monitors[get_screen_id])  # Assuming monitor is the one you want
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

        print(f"Captured image dimensions: {screenshot.width}x{screenshot.height}")

        # Define the desired offset (get_image_offset_x right, IMAGE_OFFSET_Y down)
        offset_x = get_image_offset_x  # Horizontal offset (move image right)
        offset_y = get_image_offset_y  # Vertical offset (move image down)

        # Get the dimensions of the captured image
        width, height = img.size
        print(f"Image size: {width}x{height}")

        # Check if the offsets are within bounds
        if offset_x + get_image_width > width or offset_y + get_image_width > height:
            print(
                f"Warning: Cropping area is out of bounds. Image size: {width}x{height}, offset_x: {offset_x}, offset_y: {offset_y}"
            )

        # Adjust the cropping coordinates to reflect the offset
        print(
            f"Cropping the image starting from ({offset_x}, {offset_y}) to ({offset_x + get_image_width}, {offset_y + get_image_width})")
        img_offset = img.crop((offset_x, offset_y, offset_x + get_image_width, offset_y + get_image_width))

        # Resize the image to get_image_width by get_image_height (if necessary, this step may be redundant in this case)
        print(f"Resizing cropped image to {get_image_width}x{get_image_height}...")
        img_resized = img_offset.resize((get_image_width, get_image_height))

        # Save the adjusted image
        img_resized.save(get_debug_out_image_name)
        print(
            f"Screenshot with offset and resized to {get_image_width} by {get_image_height} as {get_debug_out_image_name}")


if __name__ == "__main__":
    capture_with_offset_and_resize()
