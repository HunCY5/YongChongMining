# src/preprocess.py
import glob
from pathlib import Path
import pandas as pd
import numpy as np
from utils import classify, unify

DATA_DIR = Path("data/csv")
OUT_DIR  = Path("outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 2013~2023 CSV 일괄 로드 & 3분류
paths = sorted(DATA_DIR.glob("mining_*12.csv"))
dfs = []
for p in paths:
    yy = int(p.stem.split('_')[-1][:2]) + 2000
    tmp = pd.read_csv(p, encoding='cp949')
    tmp['연도']   = yy
    tmp['그룹3'] = tmp['장애유형'].astype(str).apply(classify)
    dfs.append(tmp[tmp['그룹3'].notna()])

df3 = pd.concat(dfs, ignore_index=True)

# 2013, 2023 pivot
pt13 = df3[df3['연도']==2013].pivot_table(
    index='통계시도명', columns='그룹3',
    values='등록장애인수', aggfunc='sum', fill_value=0
)
pt23 = df3[df3['연도']==2023].pivot_table(
    index='통계시도명', columns='그룹3',
    values='등록장애인수', aggfunc='sum', fill_value=0
)

# 약칭 통일(강원도↔강원특별자치도 등 묶기)
pt13_u = unify(pt13)
pt23_u = unify(pt23)

# 증가율(%) = (pt23 - pt13) / pt13 * 100
growth_u = (pt23_u - pt13_u).div(pt13_u).mul(100).round(1).replace([np.inf,-np.inf],0)

# 저장
pt13_u.to_parquet(OUT_DIR/"pt13_u.parquet")
pt23_u.to_parquet(OUT_DIR/"pt23_u.parquet")
growth_u.to_parquet(OUT_DIR/"growth_u.parquet")

print("Saved parquet:", OUT_DIR)
