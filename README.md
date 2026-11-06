# 郵便番号

日本郵便が公開する全国の郵便番号と、都道府県・市区町村・町域の名称（漢字・カナ）、全国地方公共団体コードの対応を収録したデータセットです。郵便番号から `lg_code` を引いて、市区町村単位の統計と結合できます。

## 出典と利用条件

- [日本郵便「郵便番号データダウンロード」](https://www.post.japanpost.jp/zipcode/dl/utf-zip.html)の住所の郵便番号（UTF-8 の CSV）を加工して作成しています
- 郵便番号データは[自由に利用できます](https://www.post.japanpost.jp/zipcode/dl/utf-readme.html)

## テーブル

`main.mart_zipcode` は 1 行が 1 郵便番号 × 1 町域です。

| 列 | 内容 |
| --- | --- |
| `zipcode` | 郵便番号（ハイフンなし 7 桁） |
| `old_zipcode` | 旧郵便番号（5 桁） |
| `lg_code` | 全国地方公共団体コード（6 桁） |
| `prefecture` / `city` / `town` | 都道府県 / 市区町村 / 町域（漢字） |
| `prefecture_kana` / `city_kana` / `town_kana` | 都道府県 / 市区町村 / 町域（カナ） |
| `has_multiple_zipcodes` | 1 つの町域に複数の郵便番号がある（0/1） |
| `has_koaza_banchi` | 小字ごとに番地を振っている町域（0/1） |
| `has_chome` | 丁目がある町域（0/1） |
| `has_multiple_towns` | 1 つの郵便番号が複数の町域を表す（0/1） |
| `update_status` | 0=変更なし、1=変更あり、2=廃止 |
| `update_reason` | 0=変更なし、1=市政施行、2=住居表示、3=区画整理、4=郵便区調整、5=訂正、6=廃止 |

## 使い方

郵便番号から住所と団体コードを引く:

```sql
SELECT zipcode, lg_code, prefecture, city, town
FROM zipcode.main.mart_zipcode
WHERE zipcode = '1910011';
```

統計と結合する手順は [郵便番号から市区町村統計につなげる](docs/join-municipal-stats.md) にあります。

## 注意

- 1 つの郵便番号が複数の町域にまたがると複数行になります。郵便番号で結合するときは、`lg_code` の重複を除くか `has_multiple_towns` を確認してください
- 町域が「以下に掲載がない場合」の行は、その市区町村の既定の郵便番号です
- 事業所の個別郵便番号は収録していません
