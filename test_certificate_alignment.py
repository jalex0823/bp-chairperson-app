"""Test certificate alignment with your custom PNG template"""
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Load your certificate template
cert_image_path = os.path.join('static', 'img', 'certificate_template.png')

if not os.path.exists(cert_image_path):
    print(f"❌ Certificate template not found at: {cert_image_path}")
    exit(1)

# Open the certificate template
img = Image.open(cert_image_path)
draw = ImageDraw.Draw(img)

# Get image dimensions
img_width, img_height = img.size
print(f"📐 Certificate dimensions: {img_width}x{img_height}")

# ===== CERTIFICATE POSITIONING CONFIGURATION =====
NAME_LINE_POSITION = 0.48   # Where the name line appears on your template
DATE_LINE_POSITION = 0.78   # Where the date line appears on your template (moved down)
PROGRAM_TEXT_POSITION = 0.72  # Additional program text position
BP_ID_POSITION = 0.88        # BP ID position (moved down to avoid overlap)
# =================================================

# Try to load fonts
try:
    name_font = ImageFont.truetype("arial.ttf", 56)
    date_font = ImageFont.truetype("arial.ttf", 40)
    detail_font = ImageFont.truetype("arial.ttf", 18)
    print("✅ Using Arial font")
except:
    name_font = ImageFont.load_default()
    date_font = ImageFont.load_default()
    detail_font = ImageFont.load_default()
    print("⚠️ Using default font")

# Text color (black)
text_color = (0, 0, 0)

# Sample data
user_name = "Jeff The Genius"
completion_date = datetime.now().strftime('%B %d, %Y')
bp_id = "BP-1002"

# NAME LINE
name_bbox = draw.textbbox((0, 0), user_name, font=name_font)
name_width = name_bbox[2] - name_bbox[0]
name_height = name_bbox[3] - name_bbox[1]
name_x = (img_width - name_width) // 2
name_y = int(img_height * NAME_LINE_POSITION) - name_height
draw.text((name_x, name_y), user_name, fill=text_color, font=name_font)
print(f"✍️ Name positioned at: x={name_x}, y={name_y}")

# DATE LINE
date_bbox = draw.textbbox((0, 0), completion_date, font=date_font)
date_width = date_bbox[2] - date_bbox[0]
date_height = date_bbox[3] - date_bbox[1]
date_x = int(img_width * 0.18)  # Position at 18% from left edge
date_y = int(img_height * DATE_LINE_POSITION) - date_height
draw.text((date_x, date_y), completion_date, fill=text_color, font=date_font)
print(f"📅 Date positioned at: x={date_x}, y={date_y}")

# PROGRAM TEXT - removed to avoid overlapping emblem
# The certificate template already has the program information

# BP ID
bp_id_text = f"BP ID: {bp_id}"
bp_id_bbox = draw.textbbox((0, 0), bp_id_text, font=detail_font)
bp_id_width = bp_id_bbox[2] - bp_id_bbox[0]
bp_id_x = (img_width - bp_id_width) // 2
bp_id_y = int(img_height * BP_ID_POSITION)
draw.text((bp_id_x, bp_id_y), bp_id_text, fill=text_color, font=detail_font)
print(f"🆔 BP ID positioned at: x={bp_id_x}, y={bp_id_y}")

# Save the result
output_path = "certificate_preview.png"
img.save(output_path)
print(f"\n✅ Certificate preview saved: {output_path}")
print("📂 Open this file to check alignment!")
