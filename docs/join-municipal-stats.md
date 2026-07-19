---
title: 郵便番号から市区町村統計につなげる
order: 1
---

手元の顧客リストや店舗リストに入っている郵便番号を住所と自治体コードに解決し、市区町村単位の統計データと結合する「名寄せの基本形」です。郵便番号 → 自治体コード → 統計、という流れは他の統計データセットにもそのまま応用できます。

## 郵便番号から住所と自治体コードを引く

`mart_zipcode` は郵便番号(ハイフンなし7桁)をキーに、住所と `lg_code`(全国地方公共団体コード)を返します。

```sql
SELECT zipcode, prefecture, city, town, lg_code
FROM zipcode.main.mart_zipcode
WHERE zipcode = '1500041'
```

`lg_code` は6桁で、末尾の1桁は検査数字です。統計データセット側の市区町村コードは検査数字を除いた5桁なので、結合するときは `substr(lg_code, 1, 5)` で先頭5桁を取り出します。

## 市区町村統計に JOIN する

e-Stat の市区町村統計(`e_stat.ssds.*`)は5桁の市区町村コードを `area` 列に持ちます。郵便番号1つから、その市区町村の総人口と世帯数を引いてみます。

```sql
SELECT
  z.zipcode,
  z.prefecture || z.city AS municipality,
  MAX(CASE WHEN p.item_name = 'A1101_総人口' THEN p.value END) AS population,
  MAX(CASE WHEN p.item_name = 'A7101_世帯数' THEN p.value END) AS households
FROM zipcode.main.mart_zipcode z
JOIN e_stat.ssds.a_municipal_population p
  ON substr(z.lg_code, 1, 5) = p.area AND p.year = 2020
WHERE z.zipcode = '1500041'
GROUP BY ALL
```

SSDS の統計テーブルは同じ指標が複数の出典統計表から重複して入ることがあるため、集計は `MAX(value)` で行うのが安全です。

## 手元の顧客リストとつなげる

ここからが実務の本番です。郵便番号列を持つ CSV を手元の DuckDB で読み込めば、顧客リストを市区町村単位に名寄せして統計と並べられます(接続方法は[DuckDB CLI からの接続](https://docs.queria.io/connection/duckdb-cli)を参照)。

```text
-- customers.csv: zipcode 列(例 "150-0041")を持つ手元のファイル
CREATE TABLE customers AS FROM read_csv('customers.csv');

-- 郵便番号→市区町村コードの対応表は DISTINCT で1対1にしてから結合する
WITH zip_to_city AS (
  SELECT DISTINCT zipcode, substr(lg_code, 1, 5) AS city_code,
         prefecture || city AS municipality
  FROM zipcode.main.mart_zipcode
)
SELECT
  z.city_code,
  z.municipality,
  COUNT(*) AS customers
FROM customers c
JOIN zip_to_city z ON replace(c.zipcode, '-', '') = z.zipcode
GROUP BY ALL
ORDER BY customers DESC;
```

1つの郵便番号が複数の町域にまたがることがあるため(`has_multiple_towns` 列で判別できます)、市区町村単位の名寄せでは `DISTINCT` で対応表を1郵便番号1行にしてから結合します。これを忘れると顧客数が水増しされます。

## 応用: 顧客カバー率を出す

名寄せした顧客数を市区町村人口で割れば、「人口あたりの顧客カバー率」が市区町村別に出せます。世帯向けサービスなら世帯数(`A7101_世帯数`)を分母にします。政令指定都市の `lg_code` は区単位なので、区別の集計がそのまま得られます。
