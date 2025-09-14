# Quickstart: 登校時間変更時のロールメンション

## What you’ll build
- 登校開始時刻が通常と異なる日のみ、Discord の指定ロールにメンションを付けて通知します。

## Prerequisites
- DISCORD_WEBHOOK_URL を設定
- ROLE_ID を設定（サーバー単位）

## Steps (TDD)
1) 契約テスト: `contracts/discord_role_mention.md` に基づき、変更時のみ `<@&ROLE_ID>` が含まれることを検証
2) 統合テスト: `SchoolGuidance` 通知で baseline 差分があるケース/ないケースを追加
3) 実装: `DiscordNotifier` に content 先頭のロールメンション付与ロジックと抑制チェックを追加
4) 検証: DRY_RUN=1 でログ出力を確認

## Run (Dry Run)
- 環境変数: `DRY_RUN=1`, `DISCORD_WEBHOOK_URL`, `ROLE_ID`
- 実行: 既存 main のテスト送信または統合テストを実行
