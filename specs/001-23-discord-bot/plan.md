# Implementation Plan: JMA Alert Bot for Tokyo's 23 Wards

**Feature Branch**: 001-23-discord-bot
**Input**: D:\GitHub_tsukuba-denden\keihou-bot\specs\001-23-discord-bot\spec.md
**Status**: Draft
**Last Updated**: 2025-09-04

## Execution Flow (main)
```
1. Parse Input (FEATURE_SPEC)
   → If empty: ERROR "No feature specification provided"
2. Extract key concepts from FEATURE_SPEC
   → Identify: actors, actions, data, constraints, ambiguities
3. Phase 0: Research & Feasibility
   → Generate research.md in $SPECS_DIR
   → If research identifies blockers: ERROR "Research identified blockers"
4. Phase 1: Data Model & Contracts
   → Generate data-model.md in $SPECS_DIR
   → Generate contracts/ in $SPECS_DIR
   → Generate quickstart.md in $SPECS_DIR
   → If data model or contracts are incomplete: ERROR "Data model or contracts incomplete"
5. Phase 2: Task Breakdown
   → Generate tasks.md in $SPECS_DIR
   → If tasks are not granular enough: ERROR "Tasks not granular enough"
6. Review & Acceptance Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Plan has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
7. Return: SUCCESS (plan ready for implementation)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on HOW to implement (tech stack, APIs, code structure)
- ❌ Avoid WHAT users need (that's for the spec)
- 👥 Written for developers, not business stakeholders

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this plan from a feature spec:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the spec doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a developer**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Technical Context *(mandatory)*

### Overview
A bot that fetches JMA weather alerts, filters them for Tokyo's 23 wards, and sends notifications to a configurable Discord channel.

### Chosen Technologies
Python (for ease of development, good for scripting, strong XML parsing libraries), `requests` library (for fetching data), `discord.py` or similar (for Discord integration), `lxml` or `BeautifulSoup` (for XML parsing).

### Architecture
A scheduled job (e.g., using `APScheduler` or a simple `while True` loop with `time.sleep`) will periodically fetch data from the JMA XML feed. The fetched data will be parsed, filtered, and compared against previously sent alerts to prevent duplicates. New alerts will be formatted and sent to Discord via webhooks.

### Data Storage & Management
A simple local file (e.g., JSON or SQLite) to store sent alert IDs/timestamps to prevent duplicates. This will be a lightweight solution suitable for a bot.

### API & Integrations
JMA Disaster Prevention Information XML feed (PULL-based via ATOM feed), Discord Webhooks API.

### Security Considerations
Discord webhook URL should be stored securely (e.g., environment variable). Input validation for JMA data to prevent injection.

### Error Handling & Logging
Robust error handling for network issues (JMA API, Discord API) and XML parsing errors. Logging to console/file for monitoring.

### Testing Strategy
Unit tests for data parsing, filtering logic, and duplicate prevention. Integration tests for JMA data fetching and Discord notification sending.

### Deployment & Operations
Can be deployed as a Docker container or a simple Python script on a server (e.g., Raspberry Pi, cloud VM). Monitoring via logs.

---

## Phase 0: Research & Feasibility *(mandatory)*

### Research Questions
- Exact URL for JMA Disaster Prevention Information XML feed (ATOM feed).
- Structure of the JMA XML for alerts (how to extract alert type, location, and ID).
- How to identify Tokyo's 23 wards from the JMA data (e.g., specific codes or names).
- Discord webhook rate limits and best practices for sending messages.
- How to handle alert updates/cancellations from JMA (if the current spec doesn't cover it, it's an edge case).

### Findings
JMA provides an ATOM feed for various disaster information, including warnings/advisories. The XML structure is well-documented.
Tokyo's 23 wards have specific geographical codes or names in the JMA data.
Discord webhooks have rate limits, but for infrequent JMA alerts, it should not be an issue.

### Feasibility Assessment
Highly feasible. The core components (fetching XML, parsing, filtering, sending Discord messages) are standard tasks. The main challenge will be accurately parsing the JMA XML and mapping locations to Tokyo's 23 wards.

---

## Phase 1: Data Model & Contracts *(mandatory)*

### Data Model
[Define the data structures that will be used. This might include database schemas, API request/response formats, or internal data representations. Use diagrams or code-like structures to illustrate.]

### Contracts
[Define the interfaces and contracts between different components or services. This includes API specifications, message formats for queues, or function signatures for internal modules.]

### Quickstart Guide
[Provide a brief guide on how to set up and run a minimal version of the feature. This should include steps for environment setup, dependency installation, and running a basic example.]

---

## Phase 2: Task Breakdown *(mandatory)*

### High-Level Tasks
[Break down the implementation into high-level tasks. Each task should be a significant piece of work that can be further broken down into smaller sub-tasks.]

### Detailed Tasks
[For each high-level task, provide a more detailed breakdown into smaller, actionable tasks. Estimate the effort for each task (e.g., small, medium, large) and identify any dependencies.]

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Focused on technical implementation details
- [ ] Written for developers
- [ ] All mandatory sections completed

### Plan Completeness
- [ ] All requirements from the feature spec are addressed
- [ ] Technical context is comprehensive
- [ ] Research questions are answered
- [ ] Data model and contracts are defined
- [ ] Task breakdown is granular and actionable
- [ ] Risks and mitigation strategies are identified

---

## Progress Tracking
*Updated by main() during processing*

- [ ] Input parsed
- [ ] Key concepts extracted
- [ ] Phase 0: Research & Feasibility completed
- [ ] Phase 1: Data Model & Contracts completed
- [ ] Phase 2: Task Breakdown completed
- [ ] Review checklist passed

---