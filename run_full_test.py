#!/usr/bin/env python3
"""
ノートブックの各ステップを順番に実行して、何が起きているか確認するスクリプト
"""

import sys
import os

# ワーキングディレクトリを設定
os.chdir('/Users/ev230063/programing/ギンダー研')

print("=" * 70)
print("STEP 1: ライブラリのインポート")
print("=" * 70)

try:
    import pandas as pd
    import geopandas as gpd
    import numpy as np
    from sklearn.neighbors import BallTree
    print("✓ All libraries imported successfully")
except Exception as e:
    print(f"✗ Error importing libraries: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("STEP 2: API Key")
print("=" * 70)
API_KEY = "AIzaSyA6-5p7Ev6HxOLZOc-vEh83gzYRzZsvM20"
print(f"✓ API Key set: {API_KEY[:20]}...")

print("\n" + "=" * 70)
print("STEP 3 & 4: データ読み込み")
print("=" * 70)

# データがあるフォルダを探す
target_folder = "L01-25_13_GML"

# フォルダ内のファイルを探す
if os.path.exists(target_folder):
    files = os.listdir(target_folder)
    geojson_file = next((f for f in files if f.endswith('.geojson')), None)
    shp_file = next((f for f in files if f.endswith('.shp')), None)
    
    file_path = None
    if geojson_file:
        file_path = os.path.join(target_folder, geojson_file)
    elif shp_file:
        file_path = os.path.join(target_folder, shp_file)
        
    if file_path:
        print(f"Loading geospatial data from: {file_path}")
        gdf = gpd.read_file(file_path)
        
        # デバッグ: カラム一覧を表示
        print("--- Detected Columns ---")
        print(gdf.columns.tolist())
        print("------------------------")
        
        # 座標の抽出
        gdf["lat"] = gdf.geometry.y
        gdf["lon"] = gdf.geometry.x
        
        # 価格カラムの特定
        # L01_008: 公示価格(円) - GeoJSONの中身を確認して特定
        possible_price_cols = ["L01_008", "L01_006", "price", "価格", "公示価格"]
        price_col = next((c for c in possible_price_cols if c in gdf.columns), None)
        
        # 住所カラムの特定
        # L01_025: 住居表示 (例: 東京都 千代田区...) - GeoJSONの中身を確認して特定
        possible_addr_cols = ["L01_025", "L01_022", "address", "住居表示", "所在", "所在地"]
        addr_col = next((c for c in possible_addr_cols if c in gdf.columns), None)
        
        print(f"Selected Price Column: {price_col}")
        print(f"Selected Address Column: {addr_col}")

        if price_col:
            gdf["price"] = gdf[price_col].astype(float)
            
            cols_to_keep = ["lat", "lon", "price"]
            if addr_col:
                gdf["address"] = gdf[addr_col].astype(str)
                cols_to_keep.append("address")
            else:
                gdf["address"] = "不明"
                cols_to_keep.append("address")

            land = gdf[cols_to_keep].copy()
            land = land.dropna(subset=["lat", "lon", "price"]).reset_index(drop=True)
            print(f"Data loaded successfully. {len(land)} records.")
            print("\n最初の5行:")
            print(land.head())
        else:
            print(f"Error: Price column not found. Available columns: {gdf.columns}")
            sys.exit(1)
    else:
        print(f"No .geojson or .shp file found in {target_folder}")
        sys.exit(1)
else:
    print(f"Folder '{target_folder}' not found.")
    sys.exit(1)

print("\n" + "=" * 70)
print("STEP 7: 最近傍マッチング")
print("=" * 70)

land_coords = np.radians(land[["lat", "lon"]].values)
tree = BallTree(land_coords, metric="haversine")

def get_nearest_price(lat, lon):
    dist, idx = tree.query([np.radians([lat, lon])], k=1)
    nearest_record = land.iloc[idx[0][0]]
    nearest_price = nearest_record.price
    nearest_addr = nearest_record.address
    distance_m = dist[0][0] * 6371000
    return nearest_price, nearest_addr, distance_m

print("✓ Nearest neighbor search function created")

print("\n" + "=" * 70)
print("STEP 8: テスト実行（画像取得なし）")
print("=" * 70)

# 解析対象の地点リスト
locations = [
    (35.6655, 139.7496),
    (35.6648, 139.7501),
    (35.6660, 139.7485),
]

records = []

print("Starting batch processing...\n")

for i, (lat, lon) in enumerate(locations):
    print(f"[{i+1}/{len(locations)}] Processing: {lat}, {lon}")
    
    # Google Maps URL
    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
    print(f"  📍 Google Maps: {maps_url}")

    # 画像取得はスキップ（テストのため）
    green, sky, ped, car = 0, 0, 0, 0

    price, addr, dist = get_nearest_price(lat, lon)
    print(f"  💰 Nearest Land Price: {price:,.0f} 円/m² (Location: {addr}, Distance: {dist:.1f}m)")

    records.append({
        "lat": lat,
        "lon": lon,
        "green_ratio": green,
        "sky_ratio": sky,
        "pedestrians": ped,
        "cars": car,
        "nearest_price": price,
        "nearest_address": addr,
        "distance_to_price_point_m": dist,
        "maps_url": maps_url
    })

print("\n" + "=" * 70)
print("最終結果")
print("=" * 70)

df_result = pd.DataFrame(records)
print(df_result)

# CSVに保存
df_result.to_csv("streetview_analysis_dataset_test.csv", index=False)
print(f"\n✓ Saved to: streetview_analysis_dataset_test.csv")
