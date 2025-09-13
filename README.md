# 東京23区向け気象庁警報Bot

## 概要

これは、気象庁（JMA）から気象警報・注意報を取得し、東京23区に関する情報を指定されたDiscordチャンネルに通知するPythonベースのDiscordボットです。

## 主な機能

- 定期的に最新の気象庁XMLフィードを取得します。
- XMLデータを解析し、警報情報を抽出します。
- 東京23区に関連する警報のみをフィルタリングします。
- 整形された警報メッセージをDiscordチャンネルにWebhook経由で送信します。
- 送信済みメッセージのIDを保存することで、重複した警報の送信を防ぎます。

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

ボットを実行するには、`main.py`スクリプトを実行します:

```bash
source .venv/bin/activate  # Windowsの場合は `.venv\Scripts\activate` を使用します
python -m src.main
```

ボットが起動し、デフォルトで5分ごとに気象庁のフィードからデータを取得し、新しい警報をDiscordに投稿します。

## 設定

設定は環境変数で管理されます。

| 変数名                   | 説明                                                                                                    | デフォルト値                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `DISCORD_WEBHOOK_URL`    | **必須。** 警報を送信するDiscordのWebhook URL。                                                         | `None`                                                      |
| `JMA_FEED_URL`           | 監視対象の気象庁XMLフィードのURL。                                                                      | `https://www.data.jma.go.jp/developer/xml/feed/extra.xml`   |
| `FETCH_INTERVAL_MIN`     | ボットが新しい警報をチェックする間隔（分）。                                                            | `5`                                                         |
| `DATA_DIR`               | 送信済み警報IDのリストなど、永続的なデータを保存するディレクトリ。                                      | `data/`                                                     |

ルートディレクトリに`.env`ファイルを作成して、これらの変数を管理します:

```
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook_url"
FETCH_INTERVAL_MIN=10
```

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は`LICENSE`ファイルを参照してください。
