import os
import pandas as pd
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

# 🔹 Path to Element Icons
element_icons = {
    "Fire": "fire.png",
    "Earth": "earth.png",
    "Wind": "wind.png",
    "Water": "water.png",
    "Void": "void.png",
    "Rainbow": "rainbow.png"
}

# 🔹 Function to Draw Rounded Rectangles with Shadow
def draw_rounded_rectangle(draw, xy, radius, fill, outline=None, outline_width=5, shadow_offset=(4, 4)):
    """
    Draws a rounded rectangle with a fill color, outline, and shadow.
    """
    x0, y0, x1, y1 = xy
    shadow_color = (0, 0, 0, 120)  # Stronger shadow

    # Draw shadow
    draw.rounded_rectangle(
        (x0 + shadow_offset[0], y0 + shadow_offset[1], x1 + shadow_offset[0], y1 + shadow_offset[1]),
        radius=radius, fill=shadow_color
    )

    # Draw main rectangle
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=outline_width)

# 🔹 Function to Draw Attack Circle
def draw_attack_circle(draw, xy, fill, attack_value="6"):
    x0, y0, x1, y1 = xy
    draw.ellipse(xy, fill=fill)

    attack_value_font = ImageFont.truetype(FONT_PATH, 40)
    atk_label_font = ImageFont.truetype(FONT_PATH, 20)

    draw.text(((x0 + x1) // 2, (y0 + y1) // 2 - 10), attack_value, fill="black", font=attack_value_font, anchor="mm")
    draw.text(((x0 + x1) // 2, (y0 + y1) // 2 + 25), "DEF", fill="black", font=atk_label_font, anchor="mm")

# 🔹 Function to Draw Card Overlay
def draw_card_overlay(background, spell_name, element, effect_lore, attack):
    card_width, card_height = 744, 1040
    background = background.resize((card_width, card_height))

    overlay = Image.new("RGBA", (card_width, card_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Ensure all text values are strings and handle NaN values
    spell_name = str(spell_name) if pd.notna(spell_name) else ""
    element = str(element) if pd.notna(element) else ""
    effect_lore = str(effect_lore) if pd.notna(effect_lore) else ""
    attack = str(attack) if pd.notna(attack) else ""

    if not spell_name or any(emoji in spell_name for emoji in ["⚫", "🌈"]):
        return background

    # 🔹 Spell Name Box
    draw_rounded_rectangle(draw, (100, 30, 644, 110), radius=50, fill=(255, 223, 186), outline=(151, 120, 45))
    draw.text((372, 70), spell_name, fill="black", font=font_large, anchor="mm")  # Centered text

    # 🔹 Element Icons (Move Above the Lore Box, Aligned Left)
    elements = element.split(", ") if element else []
    icon_x = 50  # Left-aligned with the lore box
    icon_y = 730  # Above the lore box
    icon_spacing = 65  # Space between icons

    if "None" in elements or not elements:
        elements = []
    elif "Rainbow" in elements:
        elements = ["Rainbow"]

    # Draw "Resistant:" text with stronger shadow
    if elements:
        resistance_text = "Resistant:"
        shadow_offset = (4, 4)  # Stronger shadow effect

        # Stronger Shadow Effect
        for i in range(3):  # Multiple layers to make shadow stronger
            draw.text((icon_x + shadow_offset[0] - i, icon_y + shadow_offset[1] - i), resistance_text, fill="black", font=font_medium, anchor="lm")

        # White text
        draw.text((icon_x, icon_y), resistance_text, fill="white", font=font_medium, anchor="lm")

        icon_y += 40  # Move icons down so they don't overlap the "Resistant:" text

    # Add Element Icons with Shadows
    for elem in elements:
        icon_path = element_icons.get(elem)
        if icon_path and os.path.exists(icon_path):
            icon = Image.open(icon_path).convert("RGBA").resize((60, 60))

            # Create shadow effect for icons
            shadow = Image.new("RGBA", icon.size, (0, 0, 0, 120))  # Dark semi-transparent shadow
            overlay.paste(shadow, (icon_x + 5, icon_y + 5), mask=shadow)  # Offset slightly for shadow
            overlay.paste(icon, (icon_x, icon_y), mask=icon)  # Actual icon
            icon_x += icon_spacing  # Move right for each icon

    # 🔹 Attack Circle
    draw_attack_circle(draw, (580, 700, 680, 800), fill=(255, 223, 186), attack_value=attack)

    # 🔹 Lore Box
    draw_rounded_rectangle(draw, (50, 850, 694, 980), radius=50, fill=(255, 223, 186), outline=(151, 120, 45))

    # 🔹 Effect Lore Text (Inside Lore Box)
    if effect_lore.strip():
        draw.text((372, 915), effect_lore, fill="black", font=font_small, anchor="mm")

    return Image.alpha_composite(background.convert("RGBA"), overlay)
