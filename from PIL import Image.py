import numpy as np
import pandas as pd
from PIL import Image

# --- Config ---
input_image = r"C:\Anniversary\nexus_10years_Certus\Tsunami_by_hokusai_19th_century.jpg"
rows, cols = 32, 48  # 1536-well plate
max_volume_ul = 100.0  # total volume per well
output_csv = "certus_cmyk_output.csv"

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
well_rows = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  # 64 chars
data = []

for i in range(rows):
    for j in range(cols):
        well = f"{well_rows[i]}{j+1}"
        cmyk_vals = [C[i, j], M[i, j], Y[i, j], K[i, j]]
        total = sum(cmyk_vals)
        scale = max_volume_ul / total if total > 0 else 0

        for channel, val in zip(["C", "M", "Y", "K"], cmyk_vals):
            volume = round(val * scale, 3)
            data.append([well, channel, volume])

# --- Export ---
df = pd.DataFrame(data, columns=["Well", "Channel", "Volume(ul)"])
df.to_csv(output_csv, index=False)
print(f"✔ Done: {output_csv} generated.")

{
  "configurations": [
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch Python File",
      "program": "${workspaceFolder}/${input:pythonFile}"
    }
  ],
  "inputs": [
    {
      "type": "pickString",
      "id": "pythonFile",
      "description": "Select the Python file to debug",
      "options": [
        "from PIL import Image.py",
        "hello world.py"
      ]
    }
  ]
}
