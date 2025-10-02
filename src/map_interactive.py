# src/map_interactive.py
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPolygon
import plotly.graph_objects as go
from utils import unify, abbr, classify

DATA_DIR = Path("data/csv")
GEOJSON  = Path("data/geo/법정구역_시도_simplified.geojson")
OUT_DIR  = Path("outputs"); OUT_DIR.mkdir(exist_ok=True)

# ---------- 1) CSV → 2013/2023 pivot & 증가율 ----------
# 모든 연도 로드 & 3분류
paths = sorted(DATA_DIR.glob("mining_*12.csv"))
dfs = []
for p in paths:
    yy = int(p.stem.split('_')[-1][:2]) + 2000
    tmp = pd.read_csv(p, encoding='cp949')
    tmp['연도'] = yy
    tmp['그룹3'] = tmp['장애유형'].astype(str).apply(classify)
    dfs.append(tmp[tmp['그룹3'].notna()])
df3 = pd.concat(dfs, ignore_index=True)

pt13 = df3[df3['연도']==2013].pivot_table(
    index='통계시도명', columns='그룹3',
    values='등록장애인수', aggfunc='sum', fill_value=0
)
pt23 = df3[df3['연도']==2023].pivot_table(
    index='통계시도명', columns='그룹3',
    values='등록장애인수', aggfunc='sum', fill_value=0
)

pt13_u = unify(pt13)
pt23_u = unify(pt23)
growth_u = (pt23_u - pt13_u).div(pt13_u).mul(100).round(1).replace([float("inf"), float("-inf")], 0)

df_stats = pd.DataFrame({
    '시도명':          pt23_u.index,
    '보행장애_수':     pt23_u['보행장애'],
    '시각장애_수':     pt23_u['시각장애'],
    '청각장애_수':     pt23_u['청각장애'],
    '보행장애_증가율': growth_u['보행장애'],
    '시각장애_증가율': growth_u['시각장애'],
    '청각장애_증가율': growth_u['청각장애'],
})

# ---------- 2) GeoJSON 로드 & 시도 dissolve & 외곽 정리 ----------
gdf = gpd.read_file(GEOJSON)
# 반드시 'CTP_KOR_NM'이 한글 시도명
gdf = gdf.rename(columns={'CTP_KOR_NM':'시도명'})[['시도명','geometry']]
gdf['시도명'] = gdf['시도명'].replace(abbr)

# topology clean + 시도 단위 dissolve
gdf['geometry'] = gdf.geometry.buffer(0)
gdf = gdf.dissolve(by='시도명', as_index=False)

# MultiPolygon이면 가장 큰 본섬만 사용 (울릉·북한 무인도 영향 최소화)
def keep_main(geom):
    if isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda p: p.area)
    return geom
gdf['geometry'] = gdf['geometry'].apply(keep_main)

# ---------- 3) 병합 & 맵 ----------
gdf_stats = gdf.merge(df_stats, on='시도명', how='left')

fields = ['보행장애_수','시각장애_수','청각장애_수',
          '보행장애_증가율','시각장애_증가율','청각장애_증가율']
customdata = gdf_stats[fields].values

# 등록수 / 증가율 z 범위(고정)
COUNT_MIN, COUNT_MAX = 0, 40000
PCT_MIN,   PCT_MAX   = 0, 100

fig = go.Figure(go.Choroplethmapbox(
    geojson = json.loads(gdf_stats.to_json()),
    locations = gdf_stats['시도명'],
    featureidkey = "properties.시도명",
    z = gdf_stats['보행장애_수'],
    colorscale = "Reds",
    zmin = COUNT_MIN, zmax = COUNT_MAX,
    marker_line_width=0.5,
    customdata=customdata,
    hovertemplate=(
        "<b>%{location}</b><br>"
        "보행장애 수: %{customdata[0]:,}<br>"
        "시각장애 수: %{customdata[1]:,}<br>"
        "청각장애 수: %{customdata[2]:,}<br><br>"
        "보행장애 증가율: %{customdata[3]:.1f}%<br>"
        "시각장애 증가율: %{customdata[4]:.1f}%<br>"
        "청각장애 증가율: %{customdata[5]:.1f}%<extra></extra>"
    )
))
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.0, mapbox_center={"lat":36.5,"lon":127.8},
    margin={"r":0,"t":50,"l":0,"b":0},
    title="2023년 시도별 보행·시각·청각 등록수·증가율"
)

# 드롭다운(청각→시각→보행 순)
buttons = []
for grp in ['청각장애','시각장애','보행장애']:
    # 등록수
    buttons.append(dict(
        label=f"{grp} 등록수",
        method="restyle",
        args=[
            {"z":           [ df_stats[f"{grp}_수"] ],
             "colorscale":  ["Reds"],
             "zmin":        [ COUNT_MIN ],
             "zmax":        [ COUNT_MAX ]},
            [0]
        ]
    ))
    # 증가율 (%)
    buttons.append(dict(
        label=f"{grp} 증가율",
        method="restyle",
        args=[
            {"z":           [ df_stats[f"{grp}_증가율"] ],
             "colorscale":  ["Reds"],
             "zmin":        [ PCT_MIN ],
             "zmax":        [ PCT_MAX ]},
            [0]
        ]
    ))

fig.update_layout(
    updatemenus=[dict(buttons=buttons, direction="down", x=0.01, y=0.99)]
)

out_html = OUT_DIR/"interactive_map.html"
fig.write_html(str(out_html), include_plotlyjs='cdn')
print("Saved:", out_html)
