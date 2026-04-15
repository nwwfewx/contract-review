# Gotchas

## Legal Basis
- ❌ 直接引用未经确认的法条/监管口径。  
  ✅ 无法确认时标 `【需人工复核】`，并把“待核验依据”写入交付备注。
- ❌ 用失效或被替代规范作为核心依据。  
  ✅ 涉及关键法律结论时，执行生效状态与新旧法适用核验。

## Routing And Stance
- ❌ 混用旧 mode（`basic/strategic/financial`）和 canonical route。  
  ✅ 统一落盘 `canonical_mode`，旧命名只作兼容映射。
- ❌ “中立审校”输出成单边立场。  
  ✅ 输出中显式声明当前立场与适用边界。

## Output Contract
- ❌ 默认输出写成双层全景稿，导致交付冗长。  
  ✅ 默认 `delivery_only`，仅用户明确要求时启用 `dual_layer`。
- ❌ 主表字段漂移或改列。  
  ✅ 无明确用户要求时，保持固定主表 schema。

## DOCX Delivery
- ❌ 修改建议与提示建议混在同一通道。  
  ✅ 修改走 Track Changes，提示走 Comments。
- ❌ 默认场景并行交付“修订版 + 纯批注版”两份衍生文件。  
  ✅ 默认只交付一个修订稿（同一文件内含修订与提示）；仅在用户明确要求时另出纯批注版。
- ❌ 直接覆盖原文件，无法回滚。  
  ✅ 保留“原文 + 修订稿”双文件，并输出未命中清单。

## Evidence And Gates
- ❌ 给结论不带条款锚点。  
  ✅ 每条意见至少包含条款位置、原文摘录、风险后果、建议。
- ❌ 跳过交付门禁直接发版。  
  ✅ 至少执行 delivery/evidence/veto/style 四类 gate；若未通过必须显式 `manual_override`。

## Version Conflicts
- ❌ 低版本草稿覆盖高版本签署口径。  
  ✅ 坚持“用印/签署版 > 补充协议 > 草稿/批注 > 推介材料”。
