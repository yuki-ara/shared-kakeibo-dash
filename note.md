## Cheat Sheet
変数定義
```bash
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1dWlybmV3bXNtbmJmc2RzcWRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1MjQzNjMsImV4cCI6MjA2NDEwMDM2M30.4CHCkWmMHYcPYJQ17QH4DDBZBV75T3KXweK_zIZKu-k
```

全データを取得(backup用)
```bash
curl 'https://yuuirnewmsmnbfsdsqdn.supabase.co/rest/v1/shared_kakeibo?select=*' \
    -H "apikey: ${SUPABASE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_KEY}"
```

楽天カードのレコードを全て削除する
```bash
curl -X DELETE 'https://yuuirnewmsmnbfsdsqdn.supabase.co/rest/v1/shared_kakeibo?payment=eq.1' \
    -H "apikey: ${SUPABASE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_KEY}"
```

## Routine作業: 楽天カード利用明細を家計簿に登録
### 1. 明細をダウンロード
毎月12日くらいに確定メールが届く。[楽天e-navi](https://www.rakuten-card.co.jp/e-navi/members/index.xhtml?l-id=enavi_all_navi_top)にログインし、最新の確定後明細をcsvでダウンロードする。
### 2. CSVファイルを所定ディレクトリに移動させる
```bash
mv /Users/arakawayuki/Downloads/enavi*.csv /Users/arakawayuki/Documents/my-code/python/new_shared_kakeibo/rakuten-card-analysis/credit-statement/
```
### 3. CSVファイルのフォーマット
`shared_kakeibo`にインサート可能なデータにするために、必要なカラムを追加するスクリプトを実行する。
```bash
cd /Users/arakawayuki/Documents/my-code/python/new_shared_kakeibo/rakuten-card-analysis
python3 process-credit-statement.py credit-statement/enavi202503\(1314\).csv 
```
### 4. 手動でCSVファイルを編集する
- `item`列を埋める。レシートを参考に。
- `category`, `shop`を埋める。databaseを適宜参照しながら、`id`の番号を入れていく。
- CLIでもダブルチェック。
```bash
vi /Users/arakawayuki/Documents/my-code/python/new_shared_kakeibo/rakuten-card-analysis/credit-statement/processed_enavi*.csv
```
### 5. 家計簿DBに登録
```bash
cd ../
python3 -m rakuten-card-analysis.bulk-insert-csv rakuten-card-analysis/credit-statement/processed_enavi202503\(1314\).csv
```