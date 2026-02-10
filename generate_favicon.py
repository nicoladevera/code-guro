#!/usr/bin/env python3
"""
Generate favicon files from the Code Guro logo.
Removes text and centers the icon.
"""

import os

from PIL import Image

# Paths
INPUT_LOGO = "/Users/nicoladevera/Developer/code-guro/assets/logo-code-guro-dark-small.png"
OUTPUT_DIR = "/Users/nicoladevera/Developer/code-guro/assets"


def create_favicon():
    """Create favicon files from the logo."""

    # Load the original image
    print(f"Loading logo from: {INPUT_LOGO}")
    img = Image.open(INPUT_LOGO)
    print(f"Original size: {img.size}")

    # Get image dimensions
    width, height = img.size

    # The original image is 120x120 with the icon in the top portion
    # and "Code Guro" text at the bottom
    # We need to find the bounds of just the icon and crop tightly

    # Manual crop coordinates based on the logo layout
    # The icon (book with speech bubble) appears to be roughly:
    # - Top margin: ~8px
    # - Bottom of icon (before text): ~75px
    # - Left/right margins: ~10px each side

    # Crop to the icon only (removing text and excess margins)
    crop_box = (10, 8, width - 10, 75)  # (left, top, right, bottom)
    img_cropped = img.crop(crop_box)
    print(f"Cropped size: {img_cropped.size}")

    # Create a square canvas
    # Use the larger dimension to make it square
    square_size = max(img_cropped.size)

    # Create a new square image with the same background color
    # Extract the background color from a corner pixel
    bg_color = img.getpixel((0, 0))
    square_img = Image.new("RGBA", (square_size, square_size), bg_color)

    # Calculate position to paste the cropped image (perfectly centered)
    paste_x = (square_size - img_cropped.width) // 2
    paste_y = (square_size - img_cropped.height) // 2

    # Paste the cropped image onto the square canvas
    square_img.paste(img_cropped, (paste_x, paste_y))
    print(f"Square canvas size: {square_img.size}")

    # Generate different favicon sizes
    sizes = [16, 32, 48]
    png_files = []

    for size in sizes:
        # Resize with high-quality resampling
        resized = square_img.resize((size, size), Image.Resampling.LANCZOS)

        # Save as PNG
        output_file = os.path.join(OUTPUT_DIR, f"favicon-{size}x{size}.png")
        resized.save(output_file, "PNG")
        png_files.append(output_file)
        print(f"✓ Created: favicon-{size}x{size}.png")

    # Create a multi-size ICO file
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_images = [square_img.resize(size, Image.Resampling.LANCZOS) for size in ico_sizes]

    ico_file = os.path.join(OUTPUT_DIR, "favicon.ico")
    ico_images[0].save(ico_file, format="ICO", sizes=ico_sizes)
    print("✓ Created: favicon.ico (contains 16x16, 32x32, 48x48)")

    # Also save a base favicon.png at 32x32 (common default)
    favicon_png = os.path.join(OUTPUT_DIR, "favicon.png")
    square_img.resize((32, 32), Image.Resampling.LANCZOS).save(favicon_png, "PNG")
    print("✓ Created: favicon.png (32x32)")

    print(f"\n✅ All favicons generated successfully in: {OUTPUT_DIR}")
    print("\nGenerated files:")
    print("  - favicon-16x16.png")
    print("  - favicon-32x32.png")
    print("  - favicon-48x48.png")
    print("  - favicon.png (32x32 default)")
    print("  - favicon.ico (multi-size)")


if __name__ == "__main__":
    create_favicon()
