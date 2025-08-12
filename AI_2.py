import numpy as np
import pandas as pd
from PIL import Image
import string
from pathlib import Path

# --- Config ---
input_image = r"C:\Anniversary\nexus_10years_Certus\Tsunami_by_hokusai_19th_century.jpg"
rows, cols = 16, 24          # 384‑well
max_volume_ul = 100.0          # total per well across C+M+Y+K
out_dir = Path("out"); out_dir.mkdir(exist_ok=True)

# --- Load & resize to 384 grid ---
img = Image.open(input_image).convert("RGB")
img = img.resize((cols, rows), Image.Resampling.LANCZOS)
rgb = np.asarray(img, dtype=np.float32) / 255.0

# --- RGB → CMYK ---
R, G, B = rgb[...,0], rgb[...,1], rgb[...,2]
K = 1.0 - np.max(rgb, axis=2)
den = (1.0 - K + 1e-8)
C = np.clip((1.0 - R - K) / den, 0.0, 1.0)
M = np.clip((1.0 - G - K) / den, 0.0, 1.0)
Y = np.clip((1.0 - B - K) / den, 0.0, 1.0)
K = np.clip(K, 0.0, 1.0)

# --- Scale so C+M+Y+K == max_volume_ul per well ---
stack = np.stack([C, M, Y, K], axis=0)   # (4, rows, cols)
totals = stack.sum(axis=0)               # (rows, cols)
scale = np.divide(max_volume_ul, totals, out=np.zeros_like(totals), where=totals>0)
scaled = stack * scale

# --- Save per‑channel CSVs ---
row_labels = list(string.ascii_uppercase[:rows])   # A..P
col_labels = [str(i) for i in range(1, cols+1)]    # 1..24
names = ["C","M","Y","K"]

for i, name in enumerate(names):
    df = pd.DataFrame(scaled[i], index=row_labels, columns=col_labels).round(3)
    df.to_csv(out_dir / f"certus_384_{name}.csv")
    # Matrix‑only (no headers, no index), handy for copy‑paste
    df.to_csv(out_dir / f"certus_384_{name}_matrix_only.csv", header=False, index=False)
