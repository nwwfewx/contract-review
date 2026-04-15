# Asset Management Interface Mapping

Use this file as the optional mapping contract for `asset_mgmt:issuance` and `asset_mgmt:investment:alternative`.

## Standalone-First Rule
1. The repository must remain runnable with in-repo checklists only.
2. External template libraries are enhancement, not required dependency.
3. If an external template is missing, continue with local checklist and mark:
   - `【外部模板未加载，已使用内置清单】`

## Base Mapping Rule
1. Load route base checklist first:
   - `references/checklist_issuance.md` or `references/checklist_financial.md`
2. Then stack product-specific focus points.
3. For mixed product attributes, apply the stricter regulatory bucket.

## Product Focus Map
| Product Type | Primary Focus |
|---|---|
| 债权投资计划 | 还款来源、增信结构、资金用途穿透 |
| 私募股权基金 | 出资义务、治理条款、退出机制、信息披露 |
| 集合资金信托计划 | 受托职责、投资限制、风险揭示、费用口径 |
| 资产支持计划（中保登） | 基础资产真实性、现金流归集、增信与触发机制 |
| 交易所 ABS | 交易结构合规、专项计划文件一致性、持续披露责任 |

## Perspective Rule
- **Investment side**: emphasize investment safety, counterparty risk, and enforceability.
- **Issuance side**: emphasize product compliance, manager duty boundary, and investor protection consistency.

## Required Output Fields in Asset-Management Routes
1. 口径冲突清单
2. 一票否决项
3. 补证清单
4. 条款修订建议
