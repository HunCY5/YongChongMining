# src/viz_growth.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT_DIR = Path("outputs"); OUT_DIR.mkdir(exist_ok=True)

growth = pd.read_parquet(OUT_DIR/"growth_u.parquet")
cols = ['보행장애','시각장애','청각장애']

fig, ax = plt.subplots(figsize=(12,6))
growth[cols].plot.bar(
    ax=ax, rot=45, width=0.8, title='2013→2023 시도별 장애유형별 누적 증가율(%)'
)
ax.legend(title=''); ax.set_ylabel('증가율(%)')
plt.tight_layout()
fig.savefig(OUT_DIR/"growth_rate.png", dpi=150)
print("Saved:", OUT_DIR/"growth_rate.png")
