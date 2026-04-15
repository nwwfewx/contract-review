# Delivery Gate

用途：Phase 4 最终交付前的总门禁。  
执行方式：逐项判断 `PASS / FAIL / WAIVED`，并记录证据。

## Gate Items
- [ ] G1 Route locked (`canonical_mode` 已明确，且与实际加载的 checklist 一致)  
  PASS 标准：模式键唯一且无冲突映射。
- [ ] G2 Intake closure complete（必填参数齐全，或已显式 `manual_override`）  
  PASS 标准：`business_type/client_position/contract_status` 均已确认；资管场景补齐条件字段。
- [ ] G3 Main deliverable contract matched  
  PASS 标准：主表字段顺序符合 `references/output_requirements.md`，无私改列。
- [ ] G4 Output mode explicit  
  PASS 标准：`delivery_only`（默认）或 `dual_layer`（用户明确要求）已标注。
- [ ] G5 DOCX channel policy respected（若有 DOCX）  
  PASS 标准：修改型动作使用 Track Changes，提示型动作使用 Comments。
- [ ] G6 Gate checklist execution complete  
  PASS 标准：evidence / veto / style 三个子 gate 已执行并记录结果。
- [ ] G7 Unresolved risks disclosed  
  PASS 标准：未闭环问题已在交付文中显式列示（不能静默跳过）。

## Fail-Soft Rule
若任一项 FAIL：
1. 优先修复后重跑 gate。  
2. 若业务要求继续，必须输出 `manual_override`，并附未闭环风险清单。
