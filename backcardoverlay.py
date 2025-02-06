import os
from PIL import Image, ImageDraw, ImageFont

# 🔹 Font Configuration
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

try:
    font_large = ImageFont.truetype(FONT_PATH, 50)
    font_medium = ImageFont.truetype(FONT_PATH, 35)
    font_small = ImageFont.truetype(FONT_PATH, 25)
except OSError:
    print("⚠️ Font not found, using default font.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 🔹 Function to Draw Rounded Rectangles
def draw_rounded_rectangle(draw, xy, radius, fill, shadow_offset=(4, 4)):
    x0, y0, x1, y1 = xy
    shadow_color = (0, 0, 0, 100)  # Semi-transparent black for shadow

    draw.rounded_rectangle(
        (x0 + shadow_offset[0], y0 + shadow_offset[1], x1 + shadow_offset[0], y1 + shadow_offset[1]),
        radius=radius, fill=shadow_color
    )
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

# 🔹 Function to Draw Back Card Overlay
def draw_back_overlay(background, modifier, modifier_description):
    """
    Draws the back of the card with the Modifier at the top and the Modifier Description in the center.
    """
    # Resize background to standard card dimensions (744px x 1040px)
    card_width, card_height = 744, 1040
    background = background.resize((card_width, card_height))

    # Create overlay
    overlay = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Modifier Box at the Top
    draw_rounded_rectangle(draw, (100, 30, 644, 110), radius=50, fill=(255, 223, 186, 230))
    draw.text((372, 70), str(modifier), fill="black", font=font_large, anchor="mm")  # Ensure modifier is a string

    # Modifier Description Box at the Center
    draw_rounded_rectangle(draw, (50, 450, 694, 650), radius=50, fill=(255, 223, 186, 230))
    draw.text((372, 550), str(modifier_description), fill="black", font=font_medium, anchor="mm")  # Ensure description is a string

    # Merge overlay with background
    return Image.alpha_composite(background.convert("RGBA"), overlay)
