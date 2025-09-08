import numpy as np
import pandas as pd
from PIL import Image
import os

# --- Config ---
input_image = r"C:\nexus_10years_Certus\nexus_slack_logo.jpg"
rows, cols = 16, 24  # 384-well plate
max_volume_ul = 40.0  # total volume per well
output_csv = "AIcertus_cmyk_output.csv"

# --- Output folder: where this script is located ---
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(script_dir, "csv_outputs")
os.makedirs(csv_folder, exist_ok=True)

# --- Load image and resize ---
img = Image.open(input_image).convert('RGB')
img = img.resize((cols, rows), Image.LANCZOS)
rgb = np.asarray(img) / 255.0  # normalize to [0,1]

# --- Convert RGB to CMYK ---
R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
K = 1 - np.max(rgb, axis=2)
C = (1 - R - K) / (1 - K + 1e-8)
M = (1 - G - K) / (1 - K + 1e-8)
Y = (1 - B - K) / (1 - K + 1e-8)

C = np.clip(C, 0, 1)
M = np.clip(M, 0, 1)
Y = np.clip(Y, 0, 1)
K = np.clip(K, 0, 1)

# --- Create CSV data ---
stack = np.stack([C, M, Y, K], axis=0)          # shape: (4, rows, cols)
totals = stack.sum(axis=0)                       # shape: (rows, cols)
scale = np.divide(max_volume_ul, totals, out=np.zeros_like(totals), where=totals > 0)
scaled = stack * scale                           # broadcast scale to each channel

# --- Per‑channel CSVs in plate layout (one file per channel) ---
import string
def excel_row_labels(n):
    """Generate Excel-style row labels (A, B, ..., Z, AA, AB, ...)"""
    labels = []
    for i in range(n):
        label = ''
        x = i
        while True:
            label = chr(65 + (x % 26)) + label
            x = x // 26 - 1
            if x < 0:
                break
        labels.append(label)
    return labels

row_labels = [chr(65 + i) for i in range(rows)]  # 'A' to 'P'
col_labels = [str(i) for i in range(1, cols + 1)]  # '1' to '24'
channel_names = ["C", "M", "Y", "K"]

for idx, name in enumerate(channel_names):
    # With headers (row letters + column numbers) — good for auditing
    df = pd.DataFrame(scaled[idx], index=row_labels, columns=col_labels).round(3)
    df.to_csv(os.path.join(csv_folder, f"certus_{rows}x{cols}_{name}.csv"))

    # Matrix‑only (no headers/indices) — best for strict copy‑paste into the dispenser
    df.to_csv(os.path.join(csv_folder, f"certus_{rows}x{cols}_{name}_matrix_only.csv"), header=False, index=False)

# --- Export all channels to a single Excel file with separate sheets ---
excel_output = os.path.join(script_dir, f"certus_{rows}x{cols}_CMYK.xlsx")
with pd.ExcelWriter(excel_output) as writer:
    # Add info sheet with max volume
    info_df = pd.DataFrame({
        "Parameter": ["Max Volume (uL)"],
        "Value": [max_volume_ul]
    })
    info_df.to_excel(writer, sheet_name="Info", index=False)
    # Add CMYK sheets
    for idx, name in enumerate(channel_names):
        df = pd.DataFrame(scaled[idx], index=row_labels, columns=col_labels).round(3)
        df.to_excel(writer, sheet_name=name)

print(f"Excel file saved as {excel_output}")
