# 共同家計簿アプリ

Dash ベースの家計簿アプリです。支出データを管理・可視化できます。

バックエンドDBには、Supabaseを利用します。

---

## 🚀 セットアップ方法

### 1. リポジトリをクローン
```bash
git clone https://github.com/yuki-ara/shared-kakeibo-dash.git
cd shared-kakeibo-dash
```

### 2. 仮想環境を作成して有効化
```bash
python3 -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. 必要なライブラリをインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`config/secrets.env` にデータベース接続情報などを記載してください。

例:
```env
SUPABASE_URL=<SupabaseプロジェクトのURL>
SUPABASE_KEY=<Subabase DB接続のための認証キー>
```

### 5. アプリを起動
```bash
python run.py
```
ブラウザで http://ホスト名:8050 を開くとアプリが表示されます。

## 📂 ディレクトリ構成
```
.
├── app/              # Dash アプリ本体
├── db/               # DB 接続・CRUD
├── config/           # 設定ファイル・環境変数
├── assets/           # CSS / 画像
├── run.py            # エントリーポイント
├── requirements.txt  # 依存関係
└── README.md
```

## ✨ 機能
- 入力フォームから支出を登録
- データベースに保存
- 可視化グラフ（折れ線/円グラフなど）
- データテーブルで編集

## ⚠️ 注意
- backup/, rakuten-card-analysis/, tmp/ は Git 管理外です
- config/secrets.env も .gitignore 済み（絶対に公開しないでください）

