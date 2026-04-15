# Input Schema 输入参数规范

> P0 必须项：技能启动时强制收集或确认

## Required Parameters 必填参数

### 基础参数（所有模式）
| 参数 | 字段名 | 类型 | 选项 | 说明 |
|------|--------|------|------|------|
| 业务类型 | `business_type` | enum | `general` / `asset_mgmt` | 通用合同 vs 资管业务 |
| 客户立场 | `client_position` | enum | `party_a` / `party_b` / `neutral` | 甲方/乙方/中立审校 |
| 合同状态 | `contract_status` | enum | `draft` / `pending_sign` / `signed` / `sealed` | 草稿/待签/已签/用印 |

### 资管业务参数（仅 `asset_mgmt`）
| 参数 | 字段名 | 类型 | 选项 | 说明 |
|------|--------|------|------|------|
| 业务端 | `business_side` | enum | `issuance` / `investment` | 发行端/投资端 |
| 产品类型 | `product_type` | enum | `alternative` / `standardized` | 仅投资端：另类/标准化 |

### Canonical Mode Key（建议落盘字段）
| 参数 | 字段名 | 类型 | 选项 | 说明 |
|------|--------|------|------|------|
| 路由主键 | `canonical_mode` | enum | `general` / `asset_mgmt:issuance` / `asset_mgmt:investment:alternative` / `asset_mgmt:investment:standardized` | 统一路由输出与检查项加载 |

## Optional Parameters 可选参数

| 参数 | 字段名 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| 行业类型 | `industry` | string | 自动识别 | 如：房地产、金融、建设工程 |
| 托管专项叠加 | `custody_overlay` | enum | `auto` | `auto` / `on` / `off`；当识别为托管协议时建议 `on` |
| 下一场景 | `next_scenario` | string | null | 合同签署后的预期使用场景 |
| 交易对手 | `counterparty_profile` | string | null | 交易对手基本信息/信用画像 |
| 紧急程度 | `urgency` | enum | `normal` | `urgent` / `normal` / `low` |
| 输出模式 | `output_mode` | enum | `delivery_only` | `delivery_only` / `dual_layer` |
| 审查风格 | `review_style` | enum | `balanced` | `balanced` / `efficiency_first` / `compliance_closure` |

## Perspective Parameters 立场参数

> 默认立场预设为保险资管公司风险合规人员，每次输出时显示。用户可通过 `/切换立场` 命令修改。

| 参数 | 字段名 | 类型 | 默认值 | 可选值 |
|------|--------|------|--------|--------|
| 机构类型 | `org_type` | enum | `insurance_am` | `insurance_am`（保险资管）/ `insurance_company`（保险公司）/ `bank`（银行）/ `trust`（信托）/ `fund`（基金）/ `other` |
| 部门角色 | `dept_role` | enum | `risk_compliance` | `front_office`（前台业务）/ `risk_compliance`（风险合规）/ `back_office`（后台运营）/ `legal`（法务） |
| 职级定位 | `job_level` | enum | `staff` | `staff`（一般员工）/ `manager`（部门负责人）/ `executive`（管理层） |

### 立场对审查的影响

| 维度 | 影响 |
|------|------|
| **机构类型** | 决定适用的监管规则层级（保险/银行/信托/基金监管体系不同） |
| **部门角色** | 决定审查侧重点：前台关注商业条款，风控关注合规红线，后台关注执行可操作性 |
| **职级定位** | 决定输出措辞：一般员工输出"建议上报"，管理层输出"建议决策" |

### 立场切换命令

```
/切换立场 [org_type] [dept_role] [job_level]

示例：
  /切换立场 trust front_office manager
  → 切换为：信托公司 | 前台业务 | 部门负责人
```

## Canonical Mode Derivation 路由主键推导

如果用户未直接指定 `canonical_mode`，按以下规则推导：

```
IF business_type == general:
    → general
ELIF business_type == asset_mgmt AND business_side == issuance:
    → asset_mgmt:issuance
ELIF business_type == asset_mgmt AND business_side == investment AND product_type == alternative:
    → asset_mgmt:investment:alternative
ELIF business_type == asset_mgmt AND business_side == investment AND product_type == standardized:
    → asset_mgmt:investment:standardized
ELSE:
    → BLOCK and request missing routing parameters
```

Overlay 推导规则（与 canonical_mode 并行）：

```
IF custody_overlay == on:
    → stack references/checklist_custody_agreement_2026.md
ELIF custody_overlay == auto AND 合同文本包含托管关键词:
    → custody_overlay=on and stack checklist_custody_agreement_2026.md
ELSE:
    → no custody overlay
```

托管关键词默认包括：
`托管协议` / `托管合同` / `托管银行` / `托管人职责` / `投资监督` / `估值复核` / `不当营销` / `单方终止`

## Legacy Alias Compatibility（兼容映射）
- `review_mode=basic` → `canonical_mode=general`
- `review_mode=strategic` → `canonical_mode=general` + stack `checklist_strategic`
- `review_mode=financial` + `business_side=issuance` → `canonical_mode=asset_mgmt:issuance`
- `review_mode=financial` + `business_side=investment` → `canonical_mode=asset_mgmt:investment:alternative`

## Prompt Template 参数收集提示（Inversion 门禁）

当参数缺失时，使用以下提示收集：

```
在开始审查之前，请确认以下信息：

1. **业务类型与路由**：
   - [ ] 通用合同（general）
   - [ ] 资管发行端（asset_mgmt:issuance）
   - [ ] 资管投资端-另类（asset_mgmt:investment:alternative）
   - [ ] 资管投资端-标准化（asset_mgmt:investment:standardized）

2. **您的立场**：
   - [ ] 甲方（合同提供方）
   - [ ] 乙方（合同接收方）
   - [ ] 中立审校

3. **合同状态**：
   - [ ] 草稿（可大幅修改）
   - [ ] 待签（仅可小幅调整）
   - [ ] 已签/用印（仅做风险提示）

4. **输出偏好**：
   - [ ] 交付版（默认）
   - [ ] 双层输出（仅在我明确要求时）

5. **可选信息**：
   - 行业类型：
   - 下一场景：
   - 托管专项叠加（auto/on/off）：
```

若用户坚持不补齐参数，则必须显式标注：
1. 缺失参数清单；
2. 继续执行的风险；
3. `manual_override` 标记。
