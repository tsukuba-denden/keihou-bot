# 東京23区向け気象庁警報Bot

## 概要

これは、気象庁（JMA）から気象警報・注意報を取得し、東京23区に関する情報を指定されたDiscordチャンネルに通知するPythonベースのDiscordボットです。

## 主な機能

- 定期的に最新の気象庁XMLフィードを取得します。
- XMLデータを解析し、警報情報を抽出します。
- 東京23区に関連する警報のみをフィルタリングします。
- 整形された警報メッセージをDiscordチャンネルにWebhook経由で送信します。
- 送信済みメッセージのIDを保存することで、重複した警報の送信を防ぎます。
- 解除電文（取消/解除）を検知し、解除用のDiscord埋め込みメッセージを送信します。

## 要件

- Python 3.10以上
- パッケージ管理のための`uv`（または`pip`）

## インストール

1.  **リポジトリをクローンします:**
    ```bash
    git clone https://github.com/tsukuba-denden/keihou-bot.git
    cd keihou-bot
    ```

2.  **`uv` を使用して依存関係をインストールします:**
    ```bash
    uv pip install -r requirements.txt
    ```
    または、`uv` がインストールされている場合は、仮想環境の作成と依存関係のインストールを一度に行うことができます:
    ```bash
    uv venv
    uv sync
    ```

## 使い方

ボットを実行するには、`uv run` を使用して `main.py` スクリプトを実行します。

```bash
uv run python -m src.main
```

このコマンドは、`uv` が管理する仮想環境内で `python -m src.main` を実行するため、仮想環境を事前に有効化する必要がありません。

ボットが起動し、デフォルトで5分ごとに気象庁のフィードからデータを取得し、新しい警報をDiscordに投稿します。

## ローカルでデバッグ（警報が出ていない時）

実際に警報が出ていない時でも、以下の方法でパイプライン全体を検証できます。

1) サンプルXMLでシミュレート


PowerShell (Windows):

```powershell
uv run python -m src.main --once --simulate "samples/tokyo-warning-sample.xml" --dry-run
```

ポイント:

- 解除シナリオの簡易検証は、`--simulate` を2回変えて実行（1回目: 発表、2回目: 解除（Head/InfoType=取消 または Kind/Status=解除 を含むXML））。
- `--force-send` を付けると、保存済みでも送信ロジックを通すことができます（テスト・検証用）。

2) 既存のフィードURLを使いつつドライラン

```powershell
$env:JMA_FEED_URL = "https://www.data.jma.go.jp/developer/xml/feed/extra.xml"
uv run python -m src.main --once --dry-run
```

3) 送信の抑止（環境変数）

`--dry-run` の代わりに、環境変数でも指定できます。

```powershell
$env:DRY_RUN = "true"
uv run python -m src.main --once --simulate "samples/tokyo-warning-sample.xml"
```

4) 重複送信の確認

送信済みIDは `data/sent_ids.json` に保存されます。クリーンな状態で試すときはファイルを削除してください。

```powershell
Remove-Item -Force .\data\sent_ids.json
```

もしくは、保存済みでも送る/保存しないオプションが使えます。


```powershell
uv run python -m src.main --once --simulate "samples/tokyo-warning-sample.xml" --force-send
```


```powershell
uv run python -m src.main --once --simulate "samples/tokyo-warning-sample.xml" --no-store
```

### ストレージ仕様の更新（互換）

`data/sent_ids.json` は、これまで「送信済みIDの配列」でしたが、解除状態の管理のため「`{"<id>": "active|cancelled"}` のマップ」に拡張されました。既存ファイルは自動で後方互換的に読み込まれます（配列はすべて `active` とみなされます）。

解除を受け取った場合は、既存IDの状態が `cancelled` に更新され、解除専用の埋め込み（タイトル「【解除】気象警報・注意報」）が送信されます。

## 設定

設定は環境変数で管理されます（.env 自動読み込み対応）。

| 変数名                   | 説明                                                                                                    | デフォルト値                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `DISCORD_WEBHOOK_URL`    | **必須。** 警報を送信するDiscordのWebhook URL。                                                         | `None`                                                      |
| `JMA_FEED_URL`           | 監視対象の気象庁XMLフィードのURL。                                                                      | `https://www.data.jma.go.jp/developer/xml/feed/extra.xml`   |
| `FETCH_INTERVAL_MIN`     | ボットが新しい警報をチェックする間隔（分）。                                                            | `5`                                                         |
| `DATA_DIR`               | 送信済み警報IDのリストなど、永続的なデータを保存するディレクトリ。                                      | `data/`                                                     |

ルートディレクトリに`.env`ファイルを置くと、起動時に自動で読み込まれます（既にシェルで設定済みの環境変数があれば、そちらが優先されます）。

```
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook_url"
FETCH_INTERVAL_MIN=10
```

PowerShell セッションで一時的に上書きしたい場合は、従来どおり `$env:VAR=value` で設定できます。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は`LICENSE`ファイルを参照してください。
