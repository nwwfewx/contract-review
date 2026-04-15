# Loading Map And Dependencies

## Context Loading Map
1. Intake routing and parameters:
- `references/input_schema.md`
- `references/mode_selection.md`
2. Workflow and phase rules:
- `references/workflow_phases.md`
3. Hard constraints:
- `protocols/hard_constraints.md`
- `protocols/hard_rules.md`
4. Evidence schema and veto boundary:
- `protocols/evidence_schema.md`
- `protocols/veto_list.md`
5. Version conflict handling:
- `protocols/version_priority.md`
6. Route-specific review checklists:
- `references/checklist_basic.md`
- `references/checklist_strategic.md`
- `references/checklist_investment_advisor.md`
- `references/checklist_custody_agreement_2026.md`
- `references/checklist_issuance.md`
- `references/checklist_financial.md`
- `references/checklist_standardized.md`
7. Output contracts and templates:
- `references/output_requirements.md`
- `templates/output_templates.md`
- `templates/playbook_template.md`
- `templates/docx_revision_style.md`
- `templates/docx_comment_style.md`
- `templates/email_feedback_templates.md`
- `templates/risk_grading_template.md`
- `templates/meeting_brief_template.md`
- `templates/panoramic_analysis_template.md`
- `templates/delta_rationale_template.md`
- `templates/nda_triage_template.md`
- `references/compliance_mini_checklist.md`
- `references/general_clauses_checklist.md`
8. External sync modules:
- `references/external_sync_legal_workflows.md`
- `references/aml_trigger.md`
- `references/aml_anti_bribery_checklist.md`
9. _AltsReview bridge (asset_mgmt routes only):
- `references/interface_altsreview.md`
10. High-frequency failure correction:
- `GOTCHAS.md`
11. Delivery gates:
- `checklists/delivery_gate.md`
- `checklists/evidence_completeness.md`
- `checklists/veto_gate.md`
- `checklists/output_style_gate.md`
12. Knowledge index:
- `knowledge_base/KNOWLEDGE_INDEX.md`
13. Script tools:
- `scripts/extract_contract_structure.py`
- `scripts/docx_track_changes.py`
- `scripts/docx_commenter.py`

## Skill Dependencies
1. `docx`: parse and revise DOCX contracts.
2. `pdf`: extract text/OCR fallback for PDF contracts.
3. `notebooklm`: optional deep legal/policy lookup for complex disputes.
4. `_AltsReview`: required for `asset_mgmt:issuance` and `asset_mgmt:investment:alternative`.
