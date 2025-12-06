#!/usr/bin/env python3
"""
東京都の地価データからボロノイ図を作成
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.font_manager as fm

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic']
plt.rcParams['axes.unicode_minus'] = False

print("Loading data...")
gdf = gpd.read_file('L01-25_13_GML/L01-25_13.geojson')
gdf['lat'] = gdf.geometry.y
gdf['lon'] = gdf.geometry.x
gdf['price'] = gdf['L01_008'].astype(float)

# 200サンプルを均等にサンプリング
land_sorted = gdf.sort_values('price').reset_index(drop=True)
n_samples = 200
indices = np.linspace(0, len(land_sorted)-1, n_samples, dtype=int)
selected = land_sorted.iloc[indices][['lat', 'lon', 'price']].copy()

print(f"Selected {len(selected)} samples")
print(f"Price range: {selected['price'].min():,.0f} - {selected['price'].max():,.0f} 円/m²")

# CSVに保存
selected.to_csv('land_price_200samples.csv', index=False, 
                columns=['lat', 'lon', 'price'],
                header=['緯度', '経度', '値段'])
print("Saved to: land_price_200samples.csv")

# 主要駅（急行停車駅）の座標
major_stations = {
    '東京': (35.6812, 139.7671),
    '品川': (35.6284, 139.7387),
    '渋谷': (35.6580, 139.7016),
    '新宿': (35.6895, 139.7006),
    '池袋': (35.7295, 139.7109),
    '上野': (35.7138, 139.7774),
    '新橋': (35.6660, 139.7577),
    '有楽町': (35.6751, 139.7630),
    '秋葉原': (35.6984, 139.7731),
    '六本木': (35.6627, 139.7306),
    '恵比寿': (35.6467, 139.7100),
    '目黒': (35.6337, 139.7157),
    '大崎': (35.6197, 139.7287),
    '五反田': (35.6257, 139.7238),
    '大手町': (35.6862, 139.7655),
    '銀座': (35.6717, 139.7650),
}

print("\nCreating Voronoi diagram...")

# ボロノイ図の作成
fig, ax = plt.subplots(figsize=(16, 12))

# 座標データ
points = selected[['lon', 'lat']].values
prices = selected['price'].values

# ボロノイ図を計算
vor = Voronoi(points)

# 価格で色分け
from matplotlib.colors import LogNorm
import matplotlib.cm as cm

# カラーマップ
norm = LogNorm(vmin=prices.min(), vmax=prices.max())
cmap = cm.get_cmap('RdYlGn_r')  # 赤（高い）→黄→緑（安い）

# ボロノイ領域を描画
for i, region_index in enumerate(vor.point_region):
    region = vor.regions[region_index]
    if -1 not in region and len(region) > 0:
        polygon = [vor.vertices[i] for i in region]
        color = cmap(norm(prices[i]))
        ax.fill(*zip(*polygon), alpha=0.6, color=color, edgecolor='black', linewidth=0.5)

# データポイントをプロット
scatter = ax.scatter(points[:, 0], points[:, 1], c=prices, 
                    cmap='RdYlGn_r', norm=norm, s=10, 
                    edgecolor='black', linewidth=0.5, zorder=5)

# カラーバー
cbar = plt.colorbar(scatter, ax=ax, label='地価 (円/m²)', pad=0.01)
cbar.ax.tick_params(labelsize=10)

# 主要駅をプロット
for station_name, (lat, lon) in major_stations.items():
    ax.plot(lon, lat, 'k*', markersize=15, markeredgewidth=1, 
           markeredgecolor='white', zorder=10)
    ax.text(lon, lat, f'  {station_name}', fontsize=11, fontweight='bold',
           color='black', ha='left', va='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                    edgecolor='black', alpha=0.8), zorder=11)

# 軸範囲を東京都に限定
ax.set_xlim(139.5, 139.95)
ax.set_ylim(35.55, 35.85)

# ラベル
ax.set_xlabel('経度', fontsize=14, fontweight='bold')
ax.set_ylabel('緯度', fontsize=14, fontweight='bold')
ax.set_title('東京都の地価分布（ボロノイ図）\n200サンプル、主要駅表示', 
            fontsize=16, fontweight='bold', pad=20)

# グリッド
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('land_price_voronoi.png', dpi=300, bbox_inches='tight')
print("\nSaved visualization to: land_price_voronoi.png")

plt.show()

print("\n✅ Complete!")
print(f"  - Data: land_price_200samples.csv ({len(selected)} rows)")
print(f"  - Visualization: land_price_voronoi.png")
