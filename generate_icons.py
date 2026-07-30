# generate_icons.py
from PIL import Image, ImageDraw
import os

# Create icons folder
os.makedirs('static/icons', exist_ok=True)

def create_icon(size, filename):
    # Create image with gradient
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Gradient background (purple-blue)
    for i in range(size):
        r = int(102 + (i/size) * 20)
        g = int(126 - (i/size) * 20)
        b = int(234 - (i/size) * 40)
        draw.rectangle([(0, i), (size, i+1)], fill=(r, g, b))
    
    # Draw QR pattern
    qr_size = size // 2
    start = (size - qr_size) // 2
    box_size = qr_size // 6
    
    for row in range(6):
        for col in range(6):
            is_position = (row < 2 and col < 2) or (row < 2 and col > 3) or (row > 3 and col < 2)
            if is_position or (row + col) % 2 == 0:
                x1 = start + col * box_size
                y1 = start + row * box_size
                draw.rectangle([(x1, y1), (x1 + box_size - 1, y1 + box_size - 1)], fill='white')
    
    img.save(filename)
    print(f'✅ Created: {filename}')

# Generate all sizes
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    create_icon(size, f'static/icons/icon-{size}x{size}.png')

print('\n✅ All icons created in static/icons/')