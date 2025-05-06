from PIL import Image
import pandas as pd
import numpy as np

# Configurable parameters
PLATE_ROWS = 32
PLATE_COLS = 48
MAX_VOLUME_NL = 300  # Max volume per well in nanoliters
OUTPUT_FILE = 'well_plate_dispense_plan.csv'

# Mapping: CMYK to dispenser channels
CMYK_CHANNELS = {
    'C': 1,  # Cyan → Channel 1
    'M': 2,  # Magenta → Channel 2
    'Y': 3,  # Yellow → Channel 3
    'K': 4   # Black → Channel 4
}

def rgb_to_cmyk(r, g, b):
    # Normalize RGB
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 1
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy
    return c, m, y, k

def generate_dispense_plan(image_path):
    # Load and resize image to 48x32
    img = Image.open(image_path).convert('RGB')
    img = img.resize((PLATE_COLS, PLATE_ROWS))

    data = []
    for row in range(PLATE_ROWS):
        for col in range(PLATE_COLS):
            r, g, b = img.getpixel((col, row))
            c, m, y, k = rgb_to_cmyk(r, g, b)
            well_id = f"{chr(65 + row)}{col + 1}"  # e.g. A1, B2

            # Each ink becomes a separate dispense entry if > 0
            for color, value in zip(['C', 'M', 'Y', 'K'], [c, m, y, k]):
                volume = int(value * MAX_VOLUME_NL)
                if volume > 0:
                    data.append({
                        'Well_ID': well_id,
                        'Channel_ID': CMYK_CHANNELS[color],
                        'Volume_nL': volume
                    })

    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Dispense plan saved to: {OUTPUT_FILE}")

# Run the function with your image
generate_dispense_plan('input_image.png')
