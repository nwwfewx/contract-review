# examples

本目录用于放置 `contract-review` 的脱敏示例，帮助新用户快速理解“怎么提问、会得到什么”。

说明：
- 仅放脱敏文本和说明，不放真实合同。
- 不放二进制大文件（如 `.docx` 测试产物）。
- 示例与 `SKILL.md` 冲突时，以 `SKILL.md` 为准。

## 示例清单

| 示例 | 模式 | 目的 |
|---|---|---|
| Example A | `general` | 演示通用合同最小触发与主表输出 |
| Example B | `asset_mgmt:issuance` | 演示资管发行口径 |
| Example C | `asset_mgmt:issuance` + `custody_overlay` | 演示托管协议叠加检查 |

## Example A（general）

输入模板：

```text
请按 contract-review 审查这份服务合同。
模式：general
立场：甲方
合同状态：待签
输出：delivery_only

[粘贴合同正文或给出文件路径]
```

期望输出（最小）：
- 风险主表，包含：`条款位置`、`风险描述`、`严重度`、`依据`、`建议改写`
- 若证据不足，明确标注缺口与补证建议

## Example B（asset_mgmt:issuance）

输入模板：

```text
请按 contract-review 审查这份资管产品合同。
模式：asset_mgmt:issuance
立场：管理人（甲方）
合同状态：草稿
输出：delivery_only

[粘贴合同正文或给出文件路径]
```

期望输出（最小）：
- 资管口径风险主表
- 一票否决项（如触发）
- 补证清单

## Example C（托管协议叠加）

输入模板：

```text
请按 contract-review 审查这份托管协议。
模式：asset_mgmt:issuance
立场：管理人
合同状态：待签
并启用托管协议专项检查。

[粘贴合同正文或给出文件路径]
```

期望输出（最小）：
- 基础资管审查结果
- 托管专项补充问题清单（职责边界、监督机制、估值复核、信披衔接等）

## 脱敏规则（建议）

- 主体名称替换为 `甲方/乙方/管理人/托管人`。
- 金额、账号、联系方式、地址等敏感信息做区间化或掩码。
- 保留条款结构与编号，便于复现审查逻辑。
