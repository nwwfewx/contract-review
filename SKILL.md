---
name: contract-review
description: "Contract and institutional-document review with evidence-backed risk findings and revision-ready outputs. Trigger when user asks for 合同审查, 条款修改, 合规评估, 评审意见, 制度审查, 托管协议审查, or provides contract .docx/.pdf/.md files. Supports canonical routes: general, asset_mgmt:issuance, asset_mgmt:investment:alternative, asset_mgmt:investment:standardized. Auto-stack custody-agreement overlay when text includes 托管协议/托管合同/托管人职责/投资监督/估值复核/不当营销/单方终止."
---

# Contract Review

## Overview
Provide structured contract review with strict evidence discipline, explicit risk prioritization, and revision-ready outputs.

## Quick Contract
1. Findings must be evidence-backed (file + location) with explicit risk priority.
2. No fabricated legal basis; uncertain basis must be marked `【需人工复核】`.
3. Use non-endorsement language; provide push-forward prerequisites and fallback conditions.
4. Keep default output as fixed markdown table unless user explicitly asks another format.
5. For DOCX delivery, apply dual-mode: strict layout-lock requests use baseline save-as + in-place edit first; revision semantics stay Track Changes (modification) + Comments (advisory).
6. Do not proceed from Phase 0 to Phase 1 until intake parameters are complete (or explicit manual override is recorded).
7. Delivery release must pass gate checklists, or be explicitly marked as fail-soft manual override.

## Context Loading Rules
| Trigger | Load |
|---|---|
| Any review start | `references/input_schema.md`, `references/mode_selection.md`, `references/workflow_phases.md` |
| Phase 0 intake ambiguity / recurring failures | `GOTCHAS.md` |
| `general` route | `references/checklist_basic.md` (+ `references/checklist_strategic.md` when complexity is high) |
| `asset_mgmt:issuance` route | `references/checklist_issuance.md`, `references/interface_altsreview.md` |
| `asset_mgmt:investment:alternative` route | `references/checklist_financial.md`, `references/interface_altsreview.md` |
| `asset_mgmt:investment:standardized` route | `references/checklist_standardized.md` |
| Investment advisor agreement / 投资顾问协议 | `references/checklist_investment_advisor.md` (+ keep route base checklist loaded) |
| Custody agreement / 托管协议 / 托管合同 | `references/checklist_custody_agreement_2026.md` (+ keep route base checklist loaded) |
| DOCX revision requested | `references/output_requirements.md`, `templates/docx_revision_style.md`, `templates/docx_comment_style.md` |
| AML / anti-bribery clause appears | `references/aml_trigger.md`, `references/aml_anti_bribery_checklist.md` |
| Final delivery before release | `checklists/delivery_gate.md`, `checklists/evidence_completeness.md`, `checklists/veto_gate.md`, `checklists/output_style_gate.md` |
| Full dependency map needed | `references/loading_map_and_dependencies.md` |

## Mode Routing
1. Decide canonical mode key: `general` / `asset_mgmt:issuance` / `asset_mgmt:investment:alternative` / `asset_mgmt:investment:standardized`.
2. Collect and lock intake parameters before Phase 1.
3. Load route-specific checklist stack and `_AltsReview` bridge when required.
4. Keep output mode explicit: `delivery_only` (default) or `dual_layer` (only on explicit request).

Load `references/mode_selection.md` before Phase execution.

## Custody Overlay
1. Custody agreement review is an overlay module, not a new canonical mode.
2. If text contains 托管协议/托管合同/托管银行/托管人职责/投资监督/估值复核/不当营销/单方终止, stack `references/checklist_custody_agreement_2026.md`.
3. Keep base route checklist active and perform cross-check between product contract disclosures and custody clauses.

## Hard Gate: Intake Collection
DO NOT proceed to Phase 1 until all required parameters are confirmed in `references/input_schema.md`:
- `business_type`
- `client_position`
- `contract_status`
- if `business_type=asset_mgmt`: `business_side`
- if `business_side=investment`: `product_type`

If user insists on incomplete inputs, enter explicit fail-soft mode:
1. list missing fields,
2. state risk of proceeding,
3. continue under `manual_override`.

## Workflow
### Phase 0: Intake and Precheck
- Confirm file completeness, version priority, playbook availability, and trigger-dependent modules.

### Phase 1: Position and Scope
- Clarify objective, counterparty profile, and regulatory constraints.

### Phase 2: Clause Review Execution
- Review core/process/protection clauses and apply route-specific template stacking.
- If custody overlay is triggered, apply the 2026 custody-agreement supplementation checklist before producing final risk priorities.

### Phase 3: Scenario Completion
- Validate five scenario elements and enforceability gaps.

### Phase 4: Delivery
- Output risk table and revision proposals; add optional appendices only on explicit request.
- If DOCX output is needed, decide mode first: strict layout-lock (`分毫不差/沿用最新版/交付件`) vs standard revision-docx.
- Run all gate checklists before release. If any gate fails, either fix or mark fail-soft manual override explicitly.

For detailed phase actions and trigger outputs, load `references/workflow_phases.md`.

## Hard Constraints
- Legal basis, language boundary, and compliance-bottom-line rules are mandatory.
- De-identification for consult/interview records is default behavior.
- Corporate-separateness and related-party risk checks are always required.

Load and apply full rules from `protocols/hard_constraints.md`.

## Output Protocol
- Default output uses fixed document block + single main risk table schema.
- If user requests DOCX revision, apply dual-mode delivery:
  - `layout-lock`: latest approved baseline `.doc/.docx` save-as + native-engine in-place editing, while keeping Track Changes + Comments semantics.
  - `revision-docx` (default): use scripted Track Changes + Comments flow.
- Default output mode is `delivery_only`; dual-layer output and appendices are opt-in only.

Load full output contract from `references/output_requirements.md`.

## AML / Anti-Bribery
- Trigger only when contract text includes AML/anti-bribery clauses or user explicitly requests.
- Keep minimum checklist and wording guidance aligned with `references/aml_anti_bribery_checklist.md`.
- Also follow `references/aml_trigger.md`.

## References And Dependencies
Load `references/loading_map_and_dependencies.md` for the complete resource index and skill dependency matrix.
