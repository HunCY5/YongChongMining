# src/viz_bar_counts.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT_DIR = Path("outputs"); OUT_DIR.mkdir(exist_ok=True)

pt23 = pd.read_parquet(OUT_DIR/"pt23_u.parquet")
count_cols = ['보행장애','시각장애','청각장애']
plot_df = pt23[count_cols].copy()
plot_df['전체장애인수'] = plot_df.sum(axis=1)

fig, ax = plt.subplots(figsize=(12,6))
plot_df[['전체장애인수'] + count_cols].plot.bar(
    ax=ax, rot=45, width=0.8, title='2023년 시도별 유형별 등록장애인 수'
)
ax.legend(title=''); ax.set_ylabel('등록장애인 수')
plt.tight_layout()
fig.savefig(OUT_DIR/"disabled_count_2023.png", dpi=150)
print("Saved:", OUT_DIR/"disabled_count_2023.png")
