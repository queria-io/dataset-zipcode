"""dbt ビルド + メタデータ生成パイプライン。"""

import io
import urllib.request
import zipfile
from pathlib import Path

from dbt.cli.main import dbtRunner

URL = "https://www.post.japanpost.jp/service/search/zipcode/download/utf/zip/utf_ken_all.zip"
CSV = Path("data/utf_ken_all.csv")


def download() -> None:
    """日本郵便の ZIP を取得し、中の CSV を data/ に展開する。"""
    with urllib.request.urlopen(URL, timeout=300) as res:
        body = res.read()
    CSV.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        CSV.write_bytes(z.read(CSV.name))


def main():
    download()
    dbt = dbtRunner()

    result = dbt.invoke(["deps"])
    if not result.success:
        raise SystemExit("dbt deps failed")

    result = dbt.invoke(["run"])
    if not result.success:
        raise SystemExit("dbt run failed")

    result = dbt.invoke(["docs", "generate"])
    if not result.success:
        raise SystemExit("dbt docs generate failed")


if __name__ == "__main__":
    main()
