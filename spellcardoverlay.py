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

# 🔹 Path to Element Icons
element_icons = {
    "Fire": "fire.png",
    "Earth": "earth.png",
    "Wind": "wind.png",
    "Water": "water.png",
    "Void": "void.png"
}

# 🔹 Function to Center Crop the Image
def center_crop(image, width, height):
    """
    Center-crops an image to the specified width and height.
    """
    img_width, img_height = image.size
    left = (img_width - width) // 2
    top = (img_height - height) // 2
    right = (img_width + width) // 2
    bottom = (img_height + height) // 2
    return image.crop((left, top, right, bottom))

# 🔹 Function to Draw Rounded Rectangles
def draw_rounded_rectangle(draw, xy, radius, fill, shadow_offset=(4, 4)):
    x0, y0, x1, y1 = xy
    shadow_color = (0, 0, 0, 100)  # Semi-transparent black for shadow

    draw.rounded_rectangle(
        (x0 + shadow_offset[0], y0 + shadow_offset[1], x1 + shadow_offset[0], y1 + shadow_offset[1]),
        radius=radius, fill=shadow_color
    )
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

# 🔹 Function to Draw Attack Circle with "6 ATK"
def draw_attack_circle(draw, xy, fill, attack_value="6"):
    """
    Draws the attack circle with "6" and "ATK" centered inside.
    """
    x0, y0, x1, y1 = xy
    shadow_offset = (4, 4)
    shadow_color = (0, 0, 0, 100)  # Semi-transparent black for shadow

    # Shadow
    draw.ellipse((x0 + shadow_offset[0], y0 + shadow_offset[1], x1 + shadow_offset[0], y1 + shadow_offset[1]), fill=shadow_color)
    draw.ellipse(xy, fill=fill)

    # Text inside circle
    attack_value_font = ImageFont.truetype(FONT_PATH, 40)
    atk_label_font = ImageFont.truetype(FONT_PATH, 20)

    # Center attack value (e.g., "6")
    draw.text(((x0 + x1) // 2, (y0 + y1) // 2 - 10), attack_value, fill="black", font=attack_value_font, anchor="mm")

    # Center "ATK" below the attack value
    draw.text(((x0 + x1) // 2, (y0 + y1) // 2 + 25), "ATK", fill="black", font=atk_label_font, anchor="mm")

# 🔹 Function to Draw Card Overlay
def draw_card_overlay(background, spell_name, element, effect_lore, attack):
    # Resize and crop background to standard card dimensions (744px x 1040px)
    card_width, card_height = 744, 1040
    background = center_crop(background, card_width, card_height)

    # Create overlay
    overlay = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Title Box
    draw_rounded_rectangle(draw, (100, 30, 644, 110), radius=50, fill=(255, 223, 186, 230))
    draw.text((120, 70), spell_name, fill="black", font=font_large, anchor="lm")

    # Element Icon
    element_icon_path = element_icons.get(element)
    if element_icon_path and os.path.exists(element_icon_path):
        icon = Image.open(element_icon_path).convert("RGBA").resize((60, 60))
        icon_position = (584, 45)  # Right-aligned in title box
        overlay.paste(icon, icon_position, mask=icon)

    # Attack Circle (Positioned above the effect/combo box)
    draw_attack_circle(draw, (580, 700, 680, 800), fill=(255, 223, 186, 230), attack_value=attack)

    # Effect Box
    draw_rounded_rectangle(draw, (50, 850, 694, 980), radius=50, fill=(255, 223, 186, 230))
    draw.text((372, 915), effect_lore, fill="black", font=font_small, anchor="mm")

    # Merge overlay with background
    return Image.alpha_composite(background.convert("RGBA"), overlay)

