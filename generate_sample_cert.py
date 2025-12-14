"""Generate a sample certificate to preview the design"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime

# Create PDF
c = canvas.Canvas("sample_certificate.pdf", pagesize=letter)
width, height = letter

# Background border
c.setStrokeColorRGB(0.06, 0.43, 0.46)  # Back Porch teal color
c.setLineWidth(10)
c.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)

# Inner decorative border
c.setStrokeColorRGB(0.8, 0.8, 0.8)
c.setLineWidth(2)
c.rect(50, 50, width - 100, height - 100, stroke=1, fill=0)

# Title
c.setFont("Helvetica-Bold", 32)
c.setFillColorRGB(0.06, 0.43, 0.46)
c.drawCentredString(width / 2, height - 120, "CERTIFICATE OF COMPLETION")

# Subtitle
c.setFont("Helvetica", 16)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability
c.drawCentredString(width / 2, height - 150, "Back Porch Online AA Meetings")

# Decorative line
c.setStrokeColorRGB(0.06, 0.43, 0.46)
c.setLineWidth(2)
c.line(150, height - 170, width - 150, height - 170)

# "This certifies that"
c.setFont("Helvetica", 14)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability
c.drawCentredString(width / 2, height - 220, "This certifies that")

# User name (sample)
c.setFont("Helvetica-Bold", 28)
c.setFillColorRGB(0.06, 0.43, 0.46)
c.drawCentredString(width / 2, height - 260, "Jeff The Genius")

# Achievement text
c.setFont("Helvetica", 14)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability
c.drawCentredString(width / 2, height - 300, "has successfully completed")

# Training program title
c.setFont("Helvetica-Bold", 20)
c.setFillColorRGB(0.06, 0.43, 0.46)
c.drawCentredString(width / 2, height - 335, "Back Porch Chairperson Training Program")

# Both videos completed
c.setFont("Helvetica", 13)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability
c.drawCentredString(width / 2, height - 365, "Registration & Hosting Video Training")

y_offset = 365

# Score and details
c.setFont("Helvetica", 12)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability
c.drawCentredString(width / 2, height - y_offset - 40, 
                   f"Score: 100% (10/10 correct)")
c.drawCentredString(width / 2, height - y_offset - 60, 
                   f"ChairPoints Earned: 50")

# Date
c.setFont("Helvetica-Oblique", 11)
c.drawCentredString(width / 2, height - y_offset - 90, 
                   f"Completed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

# Bottom section - BP ID and signature line
c.setFont("Helvetica", 10)
c.setFillColorRGB(0, 0, 0)  # Pure black for readability

# Left side - BP ID
c.drawString(100, 120, f"Back Porch ID: BP-1002")

# Right side - Signature line
c.line(width - 250, 135, width - 100, 135)
c.drawString(width - 250, 120, "Authorized by Back Porch")

# Footer
c.setFont("Helvetica-Oblique", 9)
c.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray (more readable than light gray)
c.drawCentredString(width / 2, 80, "The Real Back Porch - therealbackporch.com")
c.drawCentredString(width / 2, 65, "Alcoholics Anonymous Online Meetings")

# Certificate ID for verification
c.setFont("Helvetica", 8)
c.setFillColorRGB(0.3, 0.3, 0.3)  # Medium gray for verification ID
c.drawString(50, 50, f"Certificate ID: 123-1002-BP")

c.save()
print("✅ Sample certificate generated: sample_certificate.pdf")
print("Open this file to preview the certificate design with the new colors!")
