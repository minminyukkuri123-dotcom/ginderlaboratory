# Ginder Laboratory

東京都の地価とStreet View画像を用いた景観分析プロジェクト

## ⚠️ セキュリティ警告

このプロジェクトではGoogle Maps APIを使用します。**APIキーは絶対にGitHubにコミットしないでください。**

## セットアップ

### 1. APIキーの設定

Google Cloud ConsoleでAPIキーを作成し、環境変数に設定してください：

```bash
export GOOGLE_MAPS_API_KEY="your-api-key-here"
```

または、`.env`ファイルを作成：

```
GOOGLE_MAPS_API_KEY=your-api-key-here
```

### 2. 必要なライブラリのインストール

```bash
pip install pandas numpy requests pillow matplotlib opencv-python scikit-learn ultralytics geopandas python-dotenv
```

### 3. データの準備

地価公示データ（GeoJSON形式）を`L01-25_13_GML/`フォルダに配置してください。

## ファイル構成

- `street_view_analysis.ipynb` - Street View × 地価分析メインノートブック
- `create_voronoi_300.py` - ボロノイ図作成（300サンプル、59駅）
- `create_voronoi_diagram_nogui.py` - ボロノイ図作成（200サンプル）

## 使い方

### Street View分析

1. `street_view_analysis.ipynb`を開く
2. APIキーを環境変数に設定（上記参照）
3. すべてのセルを順番に実行

### ボロノイ図の作成

```bash
python3 create_voronoi_300.py
```

出力：
- `land_price_300samples.csv` - 300地点のデータ
- `land_price_voronoi_300.png` - ボロノイ図

## 注意事項

- APIキーは`.env`ファイルまたは環境変数で管理してください
- `.env`ファイルは`.gitignore`で除外されています
- 大容量のデータファイルはGitHubにプッシュしないでください
