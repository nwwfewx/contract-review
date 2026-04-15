# Workflow Phases

## Workflow
### Phase 0: Intake and Precheck
1. Confirm all files are uploaded.
2. List file inventory and missing critical documents.
3. Complete intake parameter collection from `references/input_schema.md`.
   - Do NOT proceed to Phase 1 until required parameters are complete.
   - If user insists on proceeding with missing inputs, enter explicit fail-soft `manual_override` and list missing fields.
4. Record version priority using this order:
- 用印/签署版 > 最新补充协议 > 草稿/批注 > 推介材料
5. Check for a playbook file; if missing, ask whether to proceed without it.
6. NDA/保密协议仅在出现该类合同或条款时触发快速筛查；否则不触发。
7. DPA/个人信息处理条款仅在合同已包含相关条款时触发小清单；否则不触发。
8. 通用合同条款（责任限制/争议解决等）仅在合同包含相关条款或用户明确要求时触发小清单。
9. Default review style = `平衡`, unless user explicitly requests `效率优先` or `合规闭环`.
   - Styles: `平衡` / `效率优先` / `合规闭环`
   - Apply style rules from `references/review_style_guidance.md`.
10. If input includes咨询纪要/聊天记录, trigger Q&A extraction with strict de-identification before reuse in reports/emails.
11. If input includes法条/案例原文粘贴文本, trigger legal-text normalization before analysis to remove marketing noise and preserve legal substance.
12. If input includes起诉状/判决书/庭审笔录, switch to litigation-analysis branch and output a separate litigation appendix.
13. If output quotes laws/regulations/judicial interpretations as key basis, run legal-basis verification (effectiveness + hierarchy + time applicability) before final delivery.
14. If source text includes 托管协议/托管合同/托管银行/托管人职责/投资监督/估值复核/不当营销/单方终止, enable `custody_overlay` and load `references/checklist_custody_agreement_2026.md`.

### Phase 1: Position and Scope
1. Identify user objective and deal outcome constraints.
2. Identify transaction type and counterpart profile.
3. Identify whether listed-company or financial/ quasi-financial entity constraints apply.

### Phase 2: Clause Review Execution
1. Execute target clauses review (price/payment/delivery/core obligations).
2. Execute process clauses review (conditions precedent, notices, timeline, approvals).
3. Execute protection clauses review (breach/termination/liability/dispute/security).
4. In `asset_mgmt:issuance` or `asset_mgmt:investment:alternative`, load `_AltsReview` interface mapping and apply product template stacking.
5. For any comparative statement, run comparability check: same object layer, metric meaning, time window, and scenario. If not comparable, mark as parallel observation.
6. If `custody_overlay=on`, run custody-specific 10-point supplementation checks and output separate custody gap summary.

### Phase 3: Scenario Completion
1. Check the five scenario elements:
- 时间 / 地点 / 主体 / 交易情节 / 背景约束
2. Identify enforceability gaps and execution bottlenecks.

### Phase 4: Delivery
1. Output risk table + revision proposals.
2. If requested, generate strategy memo or compliance working paper.
3. If docx edits are needed, decide mode first:
   - `layout-lock` trigger: user explicitly requests “分毫不差 / 沿用最新版 / 交付件 / 版式锁定”。
   - `revision-docx` trigger: normal review-edit delivery.
4. `layout-lock` mode:
   - Use latest approved same-type `.doc/.docx` baseline, save-as first, then edit in native engines (LibreOffice/Word/WPS) in place.
   - Keep existing layout skeleton; do not run markdown/docx conversion reflow.
   - Within edited file, keep rule split: modification actions -> **Track Changes**; advisory tips -> **Comments**.
   - Run residue scan for old project/entity/asset names and spot-check cover, table of contents, and core tables before release.
5. `revision-docx` mode:
   - Apply **Track Changes**（修订模式）for all modification actions（改为/删除/新增），and inject advisory tips as **Comments**（批注）.
   - 默认只生成一个修订稿文件；除非用户明确要求，不额外生成纯批注版。
   - 优先使用 `scripts/docx_commenter.py --mode track-changes --clear-existing`。如需兼容旧模式，使用 `--mode comments-only --force-comments-only`。
6. Ask if any optional appendices are needed: Risk grading, Email feedback, Meeting brief.
7. Default to 交付版（单主表输出）. Only add 双层输出 when user explicitly requests “全景/双层输出”.
8. Non-comparable comparisons must be downgraded to conditional/parallel wording; avoid winner/loser language.
9. Before final release, run delivery gates:
- `checklists/delivery_gate.md`
- `checklists/evidence_completeness.md`
- `checklists/veto_gate.md`
- `checklists/output_style_gate.md`
10. If any gate fails, either:
- fix and rerun gates, or
- mark explicit fail-soft `manual_override` and include unresolved risk list in output.

## External Method Sync（2026-03）
Use `references/external_sync_legal_workflows.md` as the operating contract for externally synced methods.

### Trigger Matrix
- Q&A extraction + de-identification: trigger when source is咨询记录/沟通纪要 and output is knowledge/email/training material.
- Legal-text normalization: trigger when source is pasted legal provisions/case texts with heavy non-legal noise.
- Litigation branch: trigger when source contains complaint/judgment/hearing transcript.
- Legal-basis verification: trigger when key conclusions depend on explicit statutory basis.

### Required Outputs (when triggered)
1. De-identification note: confirm whether names/entities/addresses were masked.
2. Verification note: list each key cited legal basis with effective status and applicability (new/old law rule).
3. Branch artifact note: if litigation branch is triggered, produce a separate section "诉讼分支分析（独立）".
