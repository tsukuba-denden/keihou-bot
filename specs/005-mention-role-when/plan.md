# Implementation Plan: 登校時間変更時のロールメンション

**Branch**: `005-mention-role-when` | **Date**: 2025-09-14 | **Spec**: /specs/005-mention-role-when/spec.md
**Input**: Feature specification from `/specs/005-mention-role-when/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
目的は、通常の登校開始時刻と当日の登校開始時刻が異なる場合のみ、Discord の指定ロールをメンションして通知すること。技術方針（詳細は research.md）:
- 既存の discord.py Webhook 送信を活用し、メッセージ先頭にロールメンション（例: `<@&ROLE_ID>`）を付与
- 連投抑制は「通知キー」（例: 日付×通知タイプ×チャンネル、または通知ID）で管理し、短時間の重複メンションを防止
- 通常時刻の基準は既存ポリシー情報を優先し、未定義時はメンションなしで告知のみ（安全側）

## Technical Context
**Language/Version**: Python >= 3.10  
**Primary Dependencies**: discord.py >= 2.4.0, requests, lxml, APScheduler  
**Storage**: 既存の `src/storage.py`（ファイル/JSON ベース想定）  
**Testing**: pytest（tests/unit, tests/integration）  
**Target Platform**: Docker コンテナ  
**Project Type**: single（src/ と tests/）  
**Performance Goals**: 通常通知の範囲（特筆なし）  
**Constraints**: Discord レートリミット順守、メンション乱発の抑制  
**Scale/Scope**: 学校単位の Discord 運用規模

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1（src, tests）
- Using framework directly?: Yes（discord.py を直接使用）
- Single data model?: Yes（DTO は不要）
- Avoiding patterns?: Yes（過度なパターンは導入しない）

**Architecture**:
- EVERY feature as library?: N/A（単一アプリ内の機能拡張）
- Libraries listed: N/A（新規ライブラリなし）
- CLI per library: N/A
- Library docs: N/A

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced?: Yes（先にテスト作成）
- Order: Contract→Integration→Unit 順: Yes  
- Real dependencies used?: Yes（discord 送出は Webhook モック/DRY-RUN を併用）
- Integration tests for contract changes?: Yes

**Observability**:
- Structured logging included?: 既存ロギングを活用（INFO/ERROR）
- Error context sufficient?: Yes（抑制/無効ロール時の警告を明示）

**Versioning**:
- Version number assigned?: N/A（機能追加の範囲）
- Breaking changes handled?: N/A

## Project Structure

### Documentation (this feature)
```
specs/005-mention-role-when/
├── plan.md              # This file (/plan)
├── research.md          # Phase 0 output (/plan)
├── data-model.md        # Phase 1 output (/plan)
├── quickstart.md        # Phase 1 output (/plan)
├── contracts/           # Phase 1 output (/plan)
└── tasks.md             # Phase 2 output (/tasks - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Option 1（Single project）を継続採用

## Phase 0: Outline & Research
1. Unknowns（NEEDS CLARIFICATION）と調査項目の抽出
   - メンション設定の単位（サーバー/チャンネル/通知タイプ別）
   - 抑制ポリシー（時間窓/通知ID/当日1回）と去重キー設計
   - 通常時刻の定義源と例外日扱い
   - 対象限定（学年/クラス）のロール粒度
   - 無効ロール時の運用者通知方法
2. Best Practices 調査
   - discord.py Webhook でのロールメンション取り扱い（Allowed mentions と content 整形）
   - 連投抑制の一般的戦略（時間窓 or イベントID 去重）
3. Consolidate findings → `research.md`（Decision/Rationale/Alternatives）

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. Entities を `data-model.md` に定義（RoleMentionSetting, ScheduleBaseline, ArrivalTimeChangeNotification）
2. Discord 通知の契約を `/contracts/discord_role_mention.md` に定義（いつ/どのようにメンションするか）
3. Contract/Integration テスト方針を quickstart に記述（RED 前提）
4. Agent context 更新は別途（スクリプト有）

**Output**: data-model.md, /contracts/*, failing tests (to be added in tasks), quickstart.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- contracts → contract test tasks [P]
- entities → model/update tasks [P]
- user stories → integration test tasks
- 実装をテストに合わせて最小限で進める

**Ordering Strategy**:
- TDD: Tests → Impl → Refactor
- 依存順: Models → Services（通知/抑制） → Integration
- [P] は独立ファイル単位で並列可

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

## Complexity Tracking
（現在なし）

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*