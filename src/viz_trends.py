# src/viz_trends.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils import unify

DATA_DIR = Path("data/csv")
OUT_DIR  = Path("outputs"); OUT_DIR.mkdir(exist_ok=True)

year_files = {
    2013: DATA_DIR/"mining_1312.csv",
    2018: DATA_DIR/"mining_1812.csv",
    2023: DATA_DIR/"mining_2312.csv",
}

def agg_type(pattern):
    recs = []
    for yr, path in year_files.items():
        df_ = pd.read_csv(path, encoding='cp949')
        df_sel = df_[df_['장애유형'].astype(str).str.contains(pattern, regex=True, na=False)]
        recs.append(df_sel.groupby('통계시도명')['등록장애인수'].sum().rename(yr))
    df_all = pd.concat(recs, axis=1).fillna(0)
    return unify(df_all)

dfs = {
    '시각장애': agg_type('시각'),
    '보행장애': agg_type('뇌병변|뇌전증'),
    '청각장애': agg_type('청각')
}

fig, axes = plt.subplots(3, 1, figsize=(8,15), sharey=True)
for ax, (typ, df_typ) in zip(axes, dfs.items()):
    for yr in [2013, 2018, 2023]:
        ax.plot(df_typ.index, df_typ[yr], marker='o', label=f'{yr}년')
    ax.set_title(f'시도별 {typ} 등록장애인 수 (2013·2018·2023)')
    ax.set_ylabel('등록장애인 수'); ax.set_ylim(0, 100000)
    ax.legend(title='')
    ax.set_xticks(range(len(df_typ.index)))
    ax.set_xticklabels(df_typ.index, rotation=45, ha='center', rotation_mode='anchor')
    ax.tick_params(axis='x', pad=10)
axes[-1].set_xlabel('시도명')

plt.tight_layout()
fig.savefig(OUT_DIR/"trends_by_type.png", dpi=150)
print("Saved:", OUT_DIR/"trends_by_type.png")
