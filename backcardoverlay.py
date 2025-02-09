import os
from PIL import Image, ImageDraw, ImageFont

# 🔹 Font Configuration
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"

try:
    font_large = ImageFont.truetype(FONT_PATH, 40)
    font_medium = ImageFont.truetype(FONT_PATH, 30)
    font_small = ImageFont.truetype(FONT_PATH, 20)
except OSError:
    print("⚠️ Font not found, using default font.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

# 🔹 Function to Draw Rounded Rectangles
def draw_rounded_rectangle(draw, xy, radius, fill, outline, outline_width=8):
    """
    Draws a rounded rectangle with a specified fill color and outline.
    """
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=outline_width)


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

    # 🔹 Modifier Box (Top)
    draw_rounded_rectangle(draw, (100, 30, 644, 110), radius=50, 
                           fill=(243, 239, 199), outline=(151, 120, 45))
    draw.text((372, 70), str(modifier), fill="black", font=font_large, anchor="mm")  # Centered text

    # 🔹 Modifier Description Box (Bottom)
    draw_rounded_rectangle(draw, (50, 450, 694, 650), radius=50, 
                           fill=(255, 254, 255), outline=(139, 138, 145))
    draw.text((372, 550), str(modifier_description), fill="black", font=font_medium, anchor="mm")  # Centered text

    # Merge overlay with background
    return Image.alpha_composite(background.convert("RGBA"), overlay)
