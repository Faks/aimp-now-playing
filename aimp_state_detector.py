import pyautogui
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np
import asyncio
import time
import mss
import os
import sys

get_screen_id = 3
get_image_width = 37
get_image_height = 37
get_image_offset_x = 935
get_image_offset_y = 1034
log_file_path = 'C:/Users/faks/Documents/AIMP/state_detector.txt'


class AIMPStateDetector:
    def __init__(self):
        self.debug = False
        # Initialize previous_state with a default value
        self.previous_state = "Stopped"  # Default state
        self.lock = asyncio.Lock()  # Lock for state updates

        # Paths to pre-saved icons for comparison
        self.icons = {
            "stopped": self.load_icon('resources/img/default_idle_icon.png'),
            "paused": self.load_icon('resources/img/paused_icon.png'),
            "playing": self.load_icon('resources/img/playing_icon.png')
        }

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def load_icon(self, icon_path):
        """Load icon and handle errors if the file is not found."""
        full_path = self.resource_path(icon_path)
        try:
            return Image.open(full_path)
        except FileNotFoundError:
            print(f"Error: Icon {full_path} not found.")
            return None

    def capture_taskbar_region(self):
        try:
            with mss.mss() as sct:
                screenshot = sct.grab(sct.monitors[get_screen_id])  # Capture screen
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        except Exception as e:
            if self.debug:
                print(f"Error capturing screenshot: {e}")
            return None

        # Define the desired offset (get_image_offset_x right, IMAGE_OFFSET_Y down)
        offset_x = get_image_offset_x  # Horizontal offset (move image right)
        offset_y = get_image_offset_y  # Vertical offset (move image down)

        # Get the dimensions of the captured image
        width, height = img.size

        # Check if the cropping area is within bounds
        if offset_x + get_image_width > width or offset_y + get_image_height > height:
            if self.debug:
                print(f"Warning: Crop area exceeds image bounds. Image size: {width}x{height}")
            return None

        # Adjust the cropping coordinates and crop the image
        img_offset = img.crop((offset_x, offset_y, offset_x + get_image_width, offset_y + get_image_height))

        # Resize the cropped image
        img_resized = img_offset.resize((get_image_width, get_image_height))

        return img_resized

    def calculate_similarity(self, image1, image2):
        """Calculate similarity between two images using SSIM (Structural Similarity Index)."""

        # Convert images to grayscale for SSIM comparison
        img1_gray = np.array(image1.convert('L'))
        img2_gray = np.array(image2.convert('L'))

        # Ensure both images have the same size
        if img1_gray.shape != img2_gray.shape:
            return 0  # Return 0 similarity if the images don't have the same shape

        # Calculate SSIM between the two images
        similarity_index, _ = ssim(img1_gray, img2_gray, full=True)

        # Return the similarity percentage
        similarity_percentage = similarity_index * 100
        similarity_percentage = int(similarity_percentage)

        if self.debug:
            print(f"calculate_similarity: similarity_percentage {similarity_percentage}%")

        return similarity_percentage

    def compare_images(self, image1, image2, threshold=87):
        """Compare two images and return True if their similarity is above the threshold."""
        similarity = self.calculate_similarity(image1, image2)
        if self.debug:
            print(f"compare_images similarity: {similarity}%")
        return similarity >= threshold

    def detect_aimp_state(self):
        """Detect the state of the AIMP icon."""
        time.sleep(0.05)  # Delay to stabilize state during transitions
        taskbar_image = self.capture_taskbar_region()

        if taskbar_image is None:
            return "Stopped"

        # Compare the captured image with reference icons
        for state, icon in self.icons.items():
            if self.compare_images(taskbar_image, icon):
                return state.capitalize()

        return "Stopped"

    def save_to_log_file(self, state):
        """Save the current state to the log file, replacing the previous content."""
        try:
            with open(log_file_path, "w") as log_file:
                log_file.write(state)
                if self.debug:
                    print(f"Log file updated: {state}")
        except Exception as e:
            if self.debug:
                print(f"Error writing to log file: {e}")

    async def async_scan(self, interval=1):
        """Asynchronously scan the AIMP state at regular intervals."""
        while True:
            current_state = self.detect_aimp_state()

            async with self.lock:
                if current_state != self.previous_state:
                    self.previous_state = current_state
                    self.save_to_log_file(current_state)
                    if self.debug:
                        print(f"Current state: {current_state}")

            await asyncio.sleep(interval)


# Main script
if __name__ == "__main__":
    detector = AIMPStateDetector()
    if detector.debug:
        print("Starting AIMP state detector...")
    asyncio.run(detector.async_scan(interval=1))
