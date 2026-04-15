# Mode Selection

## Mode Selection 模式选择

### Step 1: 业务类型
| 模式 | 适用场景 | 输出风格 |
|------|----------|----------|
| `general` | 通用合同（采购/服务/委托/租赁等非业务性质） | 风险清单 + 修改建议 |
| `asset_mgmt` | 资管业务合同（发行或投资） | 合规评估 + 尽调清单 |

### Canonical Mode IDs（唯一模式标识）
- `general`
- `asset_mgmt:issuance`
- `asset_mgmt:investment:alternative`
- `asset_mgmt:investment:standardized`

### Step 2: 资管业务分支（仅 `asset_mgmt` 模式）

```
asset_mgmt
├── issuance（发行端）：我方作为管理人发行
│   └── 保险资管产品（中保登登记，私募）
│       ├── 组合类
│       ├── 债权投资计划
│       ├── 股权投资计划
│       └── 资产支持计划（ABS）
│
└── investment（投资端）：我方作为受托人/投资人
    ├── alternative（另类）
    │   ├── 保险资管产品（他方发行）
    │   ├── 信托
    │   ├── 私募基金
    │   └── 交易所 ABS
    └── standardized（标准化）
        └── 债券/股票/ETF 等（受托或产品方式）
```

### 参数收集流程

```
1. 业务类型 → general / asset_mgmt
2. [仅 asset_mgmt] 业务端 → issuance / investment
3. [仅 investment] 产品类型 → alternative / standardized
4. 客户立场 → 甲方 / 乙方 / 中立
5. 合同状态 → 草稿 / 待签 / 已签 / 用印
6. 输出模式 → 交付版（默认） / 双层输出（仅用户明确要求）
```

### Legacy Alias Compatibility（兼容映射）
- `basic` → `general`
- `strategic` → `general`（并叠加 `checklist_strategic.md`）
- `financial` + `issuance` side hint → `asset_mgmt:issuance`
- `financial` + `investment` side hint → `asset_mgmt:investment:alternative`

### 资源路由

| 路径 | 加载清单 | 接口调用 | 立场 |
|------|----------|----------|------|
| `general` | `references/checklist_basic.md`（复杂场景可叠加 `references/checklist_strategic.md`） | — | — |
| `asset_mgmt/issuance` | `references/checklist_issuance.md` | 可选：`references/interface_asset_mgmt.md` | **管理人**：顺利发行 |
| `asset_mgmt/investment/alternative` | `references/checklist_financial.md` | 可选：`references/interface_asset_mgmt.md` | **投资人**：投资安全 |
| `asset_mgmt/investment/standardized` | `references/checklist_standardized.md` | — | 投资人 |

> **立场差异说明**：issuance 与 investment/alternative 可共用同一套产品审查模板，但输出时需从管理人视角重述（关注产品合规、管理人权责、投资者保护），而非投资人视角（关注投资安全、交易对手、底层资产）。

## Special Overlay Modules（不改变 canonical_mode）

### `custody_overlay`（托管协议专项）
- 触发关键词：`托管协议` / `托管合同` / `托管银行` / `托管人职责` / `投资监督` / `估值复核` / `不当营销` / `单方终止`
- 叠加资源：`references/checklist_custody_agreement_2026.md`
- 叠加方式：保持原 canonical mode（`general` 或 `asset_mgmt:*`）不变，仅增加托管专项核查
- 立场要求：默认从管理人侧审查“托管人应履职范围 + 免责边界是否越界”
