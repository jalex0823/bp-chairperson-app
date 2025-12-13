# Custom Certificate Image Setup

## Overview
The quiz certificate system can now use a custom image template instead of generating certificates programmatically. Simply place your certificate image in the correct location, and the system will automatically overlay the user's name, completion date, and score on your image.

## Quick Setup

### 1. Prepare Your Certificate Image
- **Filename**: `certificate_template.png`
- **Format**: PNG (recommended for best quality)
- **Recommended Size**: 2550x3300 pixels (8.5" x 11" at 300 DPI)
- **Orientation**: Portrait
- **Design Tips**:
  - Leave blank space in the middle/center area for the user's name
  - Include decorative borders, logos, official seals, etc.
  - Use light/neutral backgrounds where text will appear
  - Consider adding static text like "Certificate of Completion", "Back Porch", etc.

### 2. Place the Image
Copy your certificate image to:
```
static/img/certificate_template.png
```

### 3. That's It!
The system will automatically:
- Detect the custom certificate image
- Overlay the user's name (centered, 45% from top)
- Add the completion date (centered, 65% from top)
- Add the score and ChairPoints (centered, 75% from top)
- Convert to PDF for download

## Text Placement

The system uses percentage-based positioning for flexibility:

| Element | Position | Font Size | Color |
|---------|----------|-----------|-------|
| User's Name | 45% from top, centered | 48pt | Black |
| Completion Date | 65% from top, centered | 24pt | Black |
| Score & Points | 75% from top, centered | 18pt | Black |

### Adjusting Text Position
If you need to adjust where text appears on your certificate, edit these lines in `app.py` (around line 2769):

```python
# NAME position
name_y = int(img_height * 0.45)  # Change 0.45 to adjust (0.0=top, 1.0=bottom)

# DATE position  
date_y = int(img_height * 0.65)  # Change 0.65 to adjust

# SCORE position
score_y = int(img_height * 0.75)  # Change 0.75 to adjust
```

### Adjusting Text Color
If your certificate has a dark background, change the text color in `app.py`:

```python
# Change from black to white
text_color = (255, 255, 255)  # RGB for white

# Or use any color you want
text_color = (6, 110, 117)  # Example: Back Porch teal
```

## Testing Your Certificate

1. **Log in** with test credentials: `test@test.com` / `test123`
2. **Navigate** to Training Quizzes from the dashboard
3. **Take a quiz** and score at least 70%
4. **Download** the certificate to see your custom design

## Fallback Behavior

If the system cannot find `static/img/certificate_template.png`, it will automatically fall back to the programmatically generated certificate (the original design with borders and formatted text).

## Example Certificate Design

Your certificate might include:
- Decorative border with organizational colors
- Back Porch logo or seal
- Title: "Certificate of Completion"
- Subtitle: "Back Porch Online AA Meetings"
- Blank space for dynamic content (name, date, score)
- Footer with website: therealbackporch.com
- Signature line or authorized by text

## Troubleshooting

### Text is cut off or misaligned
- Adjust the percentage values in `app.py` (see above)
- Ensure your image has enough blank space in the center

### Text is hard to read
- Make sure the background is light where text appears
- Change `text_color` in the code if needed

### Certificate looks pixelated
- Use a higher resolution image (300 DPI recommended)
- Ensure image is at least 2550x3300 pixels

### Custom certificate not appearing
- Verify filename is exactly: `certificate_template.png`
- Verify location is: `static/img/certificate_template.png`
- Check Flask logs for any error messages

## Advanced Customization

For more advanced customization (different fonts, multiple colors, additional fields), you can modify the `quiz_certificate` route in `app.py` starting around line 2756. The code uses PIL (Pillow) for image manipulation.

Example modifications:
- Use custom TrueType fonts (`.ttf` files)
- Add multiple text colors for different elements
- Include quiz-specific logos or graphics
- Add QR codes for certificate verification
- Overlay signatures or seals

## Questions?

If you need help adjusting the certificate layout or have questions about customization, please refer to the PIL/Pillow documentation: https://pillow.readthedocs.io/
