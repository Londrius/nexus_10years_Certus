import subprocess
import sys
from PIL import Image

# Function to install a package
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Example: Install numpy and requests
install("numpy")
install("requests")
install("pandas")
install("Pillow")

# Open a picture
image_path = r"C:\NEXUS_10years_Certus\nexus_10years_Certus\Tsunami_by_hokusai_19th_century.jpg"
image = Image.open(image_path)
image.show()

# inserted code


plate_rows, plate_cols = 32, 48
max_total_ul = 2.0
output_csv = "certus_dispense_bcmy.csv"

# Load and resize image
img = r"C:\NEXUS_10years_Certus\nexus_10years_Certus\Tsunami_by_hokusai_19th_century.jpg"
img_resized = img.resize((plate_cols, plate_rows), Image.LANCZOS)
img_np = np.asarray(img_resized) / 255.0  # Normalize to [0,1]

# Convert to CMY and add derived Blue channel
R = img_np[:, :, 0]
G = img_np[:, :, 1]
B = img_np[:, :, 2]

C = 1 - R
M = 1 - G
Y = 1 - B
# Approximate Blue intensity as Cyan+Magenta contribution
Blue = (C + M) / 2  

# Stack into one array and normalize
channels = {'C': C, 'M': M, 'Y': Y, 'B': Blue}
all_data = []

rows = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:plate_rows]

for i in range(plate_rows):
    for j in range(plate_cols):
        well = f"{rows[i]}{j+1}"
        values = {ch: channels[ch][i, j] for ch in channels}
        total = sum(values.values())
        scale = max_total_ul / total if total > 0 else 0

        for ch in ['B', 'C', 'M', 'Y']:
            volume_ul = round(values[ch] * scale, 3)
            all_data.append([well, ch, volume_ul])

# Export
df = pd.DataFrame(all_data, columns=["Well", "Channel", "Volume(ul)"])
df.to_csv(output_csv, index=False)
print(f"Done! CSV saved as: {output_csv}")

print("END OF SCRIPT!")