# _AltsReview Interface Mapping

Use this file as the only path mapping source for `asset_mgmt:issuance` and `asset_mgmt:investment:alternative`.

## Base Rule
1. Load 通用字段模板 first.
2. Stack product template second.
3. If product is mixed, select stricter template.

## Perspective Rule (Important)
- **Investment Side (Default)**: Use templates to check for *investment safety* and *counterparty risks*. 
- **Issuance Side**: Use the SAME templates, but interpret findings for *product design compliance* and *manager exemption*.
  - e.g., "Investment Scope" in template → Check if we (Issuer) defined it broadly enough.
  - e.g., "Credit Enhancement" in template → Check if our guarantee structure is legally valid.

## Template Paths
1. 通用字段模板:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_通用字段_低权重.md`

2. 债权投资计划:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_债权投资计划_低权重.md`

3. 私募股权基金:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_私募股权基金_低权重.md`

4. 集合资金信托计划:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_集合资金信托计划_低权重.md`

5. 资产支持计划（中保登）:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_资产支持计划_中保登_低权重.md`

6. 交易所ABS:
- `_Skills/alts-review/knowledge_base/05-Templates/合规评估表_交易所ABS_低权重.md`

## Required Output Fields in Asset-Management Routes
1. 口径冲突清单
2. 一票否决项
3. 补证清单
4. 条款修订建议
