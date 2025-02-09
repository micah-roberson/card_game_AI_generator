import os
import pandas as pd
from PIL import Image
from AreaCardoverlay import draw_card_overlay  # Front overlay
from backcardoverlay import draw_back_overlay  # Back overlay
import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from math import floor

# 🔹 Load CSV Data
csv_path = "AreaIdeas.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ CSV file not found: {csv_path}")

df = pd.read_csv(csv_path)

# 🔹 StabilityAI Configuration
API_KEY = "sk-t7eAemO3L4xzSHTEkhMAJjHnEYy5liWzBg9AwhlWGV4cwNwx"
BASE_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

# 🔹 Ensure Output Directory Exists
output_dir = "cards"
os.makedirs(output_dir, exist_ok=True)

# 🔹 Function to Generate AI Backgrounds
def generate_background(spell_name, element, effect_lore):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*"
    }

    prompt = (
        f"Art Nouveau-style drawing of '{spell_name}' "
        f" "
        f"."
    )
    
    data = {
        "prompt": prompt,
        "output_format": "jpeg"
    }

    response = requests.post(BASE_URL, headers=headers, files={"none": ''}, data=data)

    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        print(f"❌ Failed to generate background for spell: {spell_name}")
        print(f"🔍 API Response Code: {response.status_code}")
        try:
            response_json = response.json()
            print(f"📜 Response JSON: {response_json}")
        except requests.exceptions.JSONDecodeError:
            print("⚠️ Response is not valid JSON. Here's the raw text:")
            print(response.text)
        return None

# 🔹 PDF Generator Function (Fixes Left Shift by Adjusting Margins)
def generate_final_pdf(front_images, back_images, filename, card_width=750, card_height=1050, dpi=300):
    """
    Generate a final PDF with alternating pages (Front → Back → Next Front → Back).
    Fixes printer misalignment by shifting content **slightly to the right**.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    page_width, page_height = letter  # Standard letter size (8.5 x 11 inches)

    # Convert card dimensions to inches at 300 DPI
    card_width_inch = card_width / dpi
    card_height_inch = card_height / dpi

    # Convert card dimensions to points (1 inch = 72 points)
    card_width_pts = int(card_width_inch * 72)
    card_height_pts = int(card_height_inch * 72)

    # Set grid parameters
    cols = 2
    rows = 2
    cards_per_page = cols * rows

    # **🔹 Center Grid on the Page + Right Shift to Fix Printer Offset**
    total_grid_width = int((cols * card_width_pts) + ((cols - 1) * 24))  # Spacing included
    total_grid_height = int((rows * card_height_pts) + ((rows - 1) * 24))

    x_start = int((page_width - total_grid_width) / 2) + 2  # **Shift RIGHT by 10 points (~1/7 inch)**
    y_start = int((page_height + total_grid_height) / 2)

    # Go through images in batches of 4 for front and back pages
    for i in range(0, len(front_images), cards_per_page):
        front_batch = front_images[i:i + cards_per_page]
        back_batch = back_images[i:i + cards_per_page]

        # 🔹 Draw Front Page (Shifted Right Slightly)
        for j, image in enumerate(front_batch):
            col = j % cols
            row = j // cols

            x = int(x_start + col * (card_width_pts + 24))
            y = int(y_start - (row + 1) * (card_height_pts + 24))

            temp_path = f"temp_front_{i+j}.jpeg"
            resized_image = image.resize((card_width, card_height))

            # Convert RGBA to RGB to avoid JPEG errors
            if resized_image.mode == "RGBA":
                resized_image = resized_image.convert("RGB")

            resized_image.save(temp_path)
            c.drawImage(temp_path, x, y, width=card_width_pts, height=card_height_pts)

        c.showPage()  # Move to next page for the mirrored back side

        # 🔹 Draw Back Page (Shifted Right Slightly)
        mirrored_positions = [1, 0, 3, 2]  # Correct mirrored layout
        for j in range(len(back_batch)):
            mirror_index = mirrored_positions[j]  # Get correct mirrored position

            col = mirror_index % cols
            row = mirror_index // cols

            x = int(x_start + col * (card_width_pts + 24))  # **Apply same right shift**
            y = int(y_start - (row + 1) * (card_height_pts + 24))

            temp_path = f"temp_back_{i+j}.jpeg"
            resized_image = back_batch[j].resize((card_width, card_height))

            # Convert RGBA to RGB to avoid JPEG errors
            if resized_image.mode == "RGBA":
                resized_image = resized_image.convert("RGB")

            resized_image.save(temp_path)
            c.drawImage(temp_path, x, y, width=card_width_pts, height=card_height_pts)

        c.showPage()  # Move to next page for next batch

    c.save()

    # Cleanup temp images
    for temp_file in os.listdir():
        if temp_file.startswith("temp_front_") or temp_file.startswith("temp_back_"):
            os.remove(temp_file)

# 🔹 Generate Cards
front_images = []
back_images = []

for index, row in df.iterrows():
    spell_name = row.get('Area Name', 'Unknown Spell')
    element = row.get('Element Resistance', 'Unknown Element')
    effect_lore = row.get('Effect/Combo', 'No Effect')
    attack = str(row.get('Defense', 0))  # Ensure it's a string for display
    modifier = row.get('Modifier', 'Unknown Modifier')
    modifier_desc = row.get('Mod. Description', 'No Description')

    # Generate front background
    background = generate_background(spell_name, element, effect_lore)
    if not background:
        continue

    # Draw front overlay
    front_card = draw_card_overlay(background, spell_name, element, effect_lore, attack)
    front_images.append(front_card)

    # Draw back overlay using backing.jpg
    if not os.path.exists("backing.jpg"):
        raise FileNotFoundError("❌ Backing image 'backing.jpg' not found.")
    backing_image = Image.open("backing.jpg")
    back_card = draw_back_overlay(backing_image, modifier, modifier_desc)
    back_images.append(back_card)

# 🔹 Generate Final Duplex PDF (Fixed Right Shift for Perfect Print Alignment)
final_pdf = os.path.join(output_dir, "cards_duplex.pdf")
generate_final_pdf(front_images, back_images, final_pdf)
print(f"✅ Final duplex PDF saved: {final_pdf}")

print(f"🎉 All cards (front and back) have been generated and saved as a **single duplex PDF** in the '{output_dir}' folder!")
