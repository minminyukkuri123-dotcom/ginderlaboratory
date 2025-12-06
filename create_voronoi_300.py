#!/usr/bin/env python3
"""
東京都の地価データからボロノイ図を作成（300サンプル、主要駅追加版）
"""

import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi
from matplotlib.colors import LogNorm
import matplotlib.cm as cm

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Hiragino Sans', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

print("Loading data...")
gdf = gpd.read_file('L01-25_13_GML/L01-25_13.geojson')
gdf['lat'] = gdf.geometry.y
gdf['lon'] = gdf.geometry.x
gdf['price'] = gdf['L01_008'].astype(float)

# 300サンプルを均等にサンプリング
land_sorted = gdf.sort_values('price').reset_index(drop=True)
n_samples = 300
indices = np.linspace(0, len(land_sorted)-1, n_samples, dtype=int)
selected = land_sorted.iloc[indices][['lat', 'lon', 'price']].copy()

print(f"Selected {len(selected)} samples")
print(f"Price range: {selected['price'].min():,.0f} - {selected['price'].max():,.0f} 円/m²")

# CSVに保存
output_csv = 'land_price_300samples.csv'
selected.to_csv(output_csv, index=False, 
                columns=['lat', 'lon', 'price'],
                header=['緯度', '経度', '値段'])
print(f"✓ Saved data to: {output_csv}")

# 主要駅（急行停車駅 + 主要ターミナル駅）
major_stations = {
    # 山手線主要駅
    '東京': (35.6812, 139.7671),
    '有楽町': (35.6751, 139.7630),
    '新橋': (35.6660, 139.7577),
    '浜松町': (35.6556, 139.7574),
    '田町': (35.6458, 139.7476),
    '品川': (35.6284, 139.7387),
    '大崎': (35.6197, 139.7287),
    '五反田': (35.6257, 139.7238),
    '目黒': (35.6337, 139.7157),
    '恵比寿': (35.6467, 139.7100),
    '渋谷': (35.6580, 139.7016),
    '原宿': (35.6702, 139.7026),
    '代々木': (35.6832, 139.7020),
    '新宿': (35.6895, 139.7006),
    '新大久保': (35.7011, 139.7006),
    '高田馬場': (35.7126, 139.7038),
    '目白': (35.7214, 139.7063),
    '池袋': (35.7295, 139.7109),
    '大塚': (35.7312, 139.7286),
    '巣鴨': (35.7339, 139.7394),
    '駒込': (35.7363, 139.7470),
    '田端': (35.7378, 139.7608),
    '西日暮里': (35.7320, 139.7668),
    '日暮里': (35.7277, 139.7707),
    '鶯谷': (35.7206, 139.7784),
    '上野': (35.7138, 139.7774),
    '御徒町': (35.7078, 139.7745),
    '秋葉原': (35.6984, 139.7731),
    '神田': (35.6916, 139.7707),
    
    # その他主要駅
    '大手町': (35.6862, 139.7655),
    '銀座': (35.6717, 139.7650),
    '六本木': (35.6627, 139.7306),
    '表参道': (35.6654, 139.7129),
    '赤坂': (35.6734, 139.7360),
    '四ツ谷': (35.6859, 139.7301),
    '飯田橋': (35.7021, 139.7459),
    '市ヶ谷': (35.6950, 139.7384),
    '水道橋': (35.7022, 139.7531),
    '後楽園': (35.7056, 139.7518),
    '護国寺': (35.7202, 139.7420),
    '早稲田': (35.7021, 139.7238),
    '高円寺': (35.7046, 139.6499),
    '中野': (35.7058, 139.6659),
    '荻窪': (35.7049, 139.6206),
    '吉祥寺': (35.7033, 139.5797),
    '三鷹': (35.6832, 139.5596),
    '調布': (35.6514, 139.5408),
    '府中': (35.6696, 139.4777),
    '立川': (35.6982, 139.4136),
    
    # 私鉄主要駅
    '北千住': (35.7749, 139.8046),
    '西新井': (35.7567, 139.7844),
    '綾瀬': (35.7494, 139.8257),
    '亀有': (35.7619, 139.8485),
    '錦糸町': (35.6969, 139.8139),
    '押上': (35.7101, 139.8133),
    '曳舟': (35.7183, 139.8174),
    '小岩': (35.7321, 139.8819),
    '葛西': (35.6643, 139.8648),
    '船堀': (35.6802, 139.8661),
}

print(f"\n主要駅数: {len(major_stations)} 駅")
print("\nCreating Voronoi diagram...")

# ボロノイ図の作成
fig, ax = plt.subplots(figsize=(18, 14))

# 座標データ
points = selected[['lon', 'lat']].values
prices = selected['price'].values

# ボロノイ図を計算
vor = Voronoi(points)

# カラーマップ
norm = LogNorm(vmin=prices.min(), vmax=prices.max())
cmap = cm.get_cmap('RdYlGn_r')

# ボロノイ領域を描画
for i, region_index in enumerate(vor.point_region):
    region = vor.regions[region_index]
    if -1 not in region and len(region) > 0:
        polygon = [vor.vertices[j] for j in region]
        color = cmap(norm(prices[i]))
        ax.fill(*zip(*polygon), alpha=0.6, color=color, edgecolor='black', linewidth=0.3)

# データポイント
scatter = ax.scatter(points[:, 0], points[:, 1], c=prices, 
                    cmap='RdYlGn_r', norm=norm, s=8, 
                    edgecolor='black', linewidth=0.3, zorder=5)

# カラーバー
cbar = plt.colorbar(scatter, ax=ax, label='地価 (円/m²)', pad=0.01)
cbar.ax.tick_params(labelsize=9)

# 主要駅をプロット
for station_name, (lat, lon) in major_stations.items():
    ax.plot(lon, lat, 'k*', markersize=12, markeredgewidth=0.8, 
           markeredgecolor='white', zorder=10)
    ax.text(lon, lat, f'  {station_name}', fontsize=9, fontweight='bold',
           color='black', ha='left', va='center',
           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                    edgecolor='black', alpha=0.75, linewidth=0.5), zorder=11)

# 軸範囲
ax.set_xlim(139.4, 140.0)
ax.set_ylim(35.55, 35.85)

# ラベル
ax.set_xlabel('経度', fontsize=14, fontweight='bold')
ax.set_ylabel('緯度', fontsize=14, fontweight='bold')
ax.set_title('東京都の地価分布（ボロノイ図）\\n300サンプル、主要駅60駅表示', 
            fontsize=16, fontweight='bold', pad=20)

# グリッド
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

plt.tight_layout()

output_png = 'land_price_voronoi_300.png'
plt.savefig(output_png, dpi=300, bbox_inches='tight')
print(f"✓ Saved visualization to: {output_png}")

plt.close()

print("\n✅ Complete!")
print(f"  - Data: {output_csv} ({len(selected)} rows)")
print(f"  - Visualization: {output_png}")
print(f"  - Stations: {len(major_stations)} stations")
