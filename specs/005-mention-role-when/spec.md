# Feature Specification: 登校時間変更時のロールメンション

**Feature Branch**: `005-mention-role-when`  
**Created**: 2025-09-14  
**Status**: Draft  
**Input**: User description: "登校時間が普段と異なる場合、指定されたロールにメンションするようにして"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
学校からの「本日の登校開始時刻」が通常と異なる（例: 8:30 → 10:00 に遅延）場合、通知を受け取るべき対象（保護者、学生、教職員など）に確実に届くよう、Discord の指定ロールにメンションを付けて告知したい。

### Acceptance Scenarios
1. **Given** 通常の登校開始時刻が 8:30 と定義されている, **When** 本日の通知が「登校開始を 10:00 に変更」と示している, **Then** 通知メッセージの先頭に設定されたロールへのメンションがちょうど一度だけ含まれる。
2. **Given** 通常の登校開始時刻が 8:30 と定義されている, **When** 本日の通知が「登校開始は通常どおり」と示している, **Then** 通知メッセージにはロールメンションが含まれない。
3. **Given** サーバーに複数の通知チャンネルが存在する, **When** 登校開始時刻変更の通知を送る, **Then** メンションは当該通知を配信するチャンネルでのみ行われる。[NEEDS CLARIFICATION: チャンネルごとのオン/オフや対象ロールの上書き可否]
4. **Given** 通知が同一事象に対する更新（例: 10:00 → 10:30 に再変更）である, **When** 既にメンション付きの初回通知を送っている, **Then** 重複通知のスパムを避けるためのメンション抑制ルールが適用される。[NEEDS CLARIFICATION: 抑制の基準（時間窓/イベントID/当日一回まで など）]

### Edge Cases
- 通常時刻の定義が存在しない（新年度・校時改定直後など）場合はどうするか？[NEEDS CLARIFICATION: メンションの有無/既定動作]
- 役割設定が未指定/無効になっている場合はどうするか？[NEEDS CLARIFICATION: メンションなしで送付 or 送付自体を保留 or 警告]
- 複数学年・学科など対象が限定的な変更（部分的変更）の場合はどう扱うか？[NEEDS CLARIFICATION]
- 臨時休校や自宅学習など「開始時刻」という概念が当てはまらない場合はどうするか？[NEEDS CLARIFICATION]
- 休日・休校日（通常授業なし）における特別登校時刻の扱いは？[NEEDS CLARIFICATION]

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: 「本日の登校開始時刻」が「通常の登校開始時刻」と異なると判断できる通知を送る際、メッセージに指定ロールへのメンションを含めなければならない。
- **FR-002**: メンション対象のロールは Discord サーバー単位で設定可能でなければならない。[NEEDS CLARIFICATION: チャンネルごと設定/上書きの可否]
- **FR-003**: 通常どおりの登校開始時刻である通知では、ロールメンションを含めてはならない。
- **FR-004**: 同一の変更事象に対する再通知や軽微な更新により短時間で複数投稿が発生しても、過度な連続メンションを抑制しなければならない。[NEEDS CLARIFICATION: 抑制ポリシー（同一イベントにつき一度、または一定時間窓内は一度 など）]
- **FR-005**: メンションの位置と形式は受け手の視認性を最優先し、メッセージの冒頭に配置することが望ましい。[NEEDS CLARIFICATION: 固定か可変か]
- **FR-006**: 設定されたロール情報が無効（削除/権限不足/メンバー0 など）の場合の挙動を定義し、通知の失敗やメンション不可をユーザー（運用者）に明確に伝達しなければならない。
- **FR-007**: 設定の変更（対象ロールの追加/削除/無効化）は次回の通知から即時反映されなければならない。
- **FR-008**: 対象となる「通常の登校開始時刻」の定義源（校時表/ポリシー）と、当日の「変更後開始時刻」の情報源が異なる場合でも、利用者にとって一貫した基準で判断されなければならない。[NEEDS CLARIFICATION: 基準の優先順位]
- **FR-009**: 対象学年やグループが限定される変更に対して、メンション対象ロールの粒度（全体ロールか学年ロールか）を選択できるべきである。[NEEDS CLARIFICATION]

*Ambiguities requiring decision:*
- メンション対象の設定単位（サーバー/チャンネル/通知タイプ別）
- メンション抑制ルール（時間窓・イベントID・当日一回など）
- 通常時刻の定義源と更新プロセス（年度更新/例外日/行事）
- 対象限定の扱い（学年/クラス/コースなど）
- 失敗時のユーザー通知方法（ログのみ/管理者へのDM/運用チャンネルでの警告 投稿 など）

### Key Entities *(include if feature involves data)*
- **RoleMentionSetting（ロールメンション設定）**: サーバー/チャンネル単位の対象ロール、メンション抑制ポリシー、有効/無効フラグ。
- **ScheduleBaseline（通常登校時刻の基準）**: 曜日や期間ごとの通常開始時刻、および例外日（行事・試験・休校）管理。[NEEDS CLARIFICATION: 管理主体と更新頻度]
- **ArrivalTimeChangeNotification（登校時刻変更通知）**: 当日の変更後開始時刻、通知種別（遅延/繰上げ/中止）、対象範囲、通知ID（重複判定用）。

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous  
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

---
