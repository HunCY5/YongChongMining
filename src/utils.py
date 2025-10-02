# src/utils.py
import numpy as np
import pandas as pd

# 시도명 축약(강원도/강원특별자치도 ⇒ 강원 등)
abbr = {
    '강원도':'강원','강원특별자치도':'강원',
    '서울특별시':'서울','경기도':'경기',
    '전라남도':'전남','전라북도':'전북',
    '충청남도':'충남','충청북도':'충북',
    '경상남도':'경남','경상북도':'경북',
    '부산광역시':'부산','대구광역시':'대구',
    '인천광역시':'인천','광주광역시':'광주',
    '대전광역시':'대전','울산광역시':'울산',
    '세종특별자치시':'세종','제주특별자치도':'제주'
}

def classify(x: str):
    """장애유형 텍스트 → 보행/시각/청각 3분류"""
    if '뇌병변' in x or '뇌전증' in x: return '보행장애'
    if '시각'    in x:                return '시각장애'
    if '청각'    in x:                return '청각장애'
    return np.nan

def unify(df: pd.DataFrame) -> pd.DataFrame:
    """pivot(index=시도명)에서 시도명 약칭 통일 + 그룹합"""
    return df.rename(index=abbr).groupby(level=0).sum()
