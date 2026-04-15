# contract-review

## 文档分工（README vs SKILL）
- 本文件 `README.md`：给人看，说明适用场景、输出形态和协作方式。
- 机器入口 `SKILL.md`：给 agent 看，定义审查流程、模式参数与交付规则。
- 两者冲突时，以 `SKILL.md` 执行契约为准，并同步回写本 README。
- 目录边界以 `DIRECTORY_GUIDE.md` 为准。

## 作用
- 用于合同与制度文件审查，输出可执行的风险清单与修订建议。
- 支持通用合同、资管发行、资管投资等多分支审查口径。
- 支持托管协议专项叠加审查（依据《商业银行托管业务监督管理办法（试行）》）。

## 使用说明（给人直接操作）
1. 先说明业务场景：`general` 或 `asset_mgmt:*`（issuance / investment:alternative / investment:standardized）。
2. 再说明立场：甲方/乙方/中立，以及你希望的交付深度（默认 `delivery_only`，双层输出仅按需）。
3. 提供合同文本（或路径）后，按 `SKILL.md` 的 Phase 0-4 流程执行。
4. 如果是资管场景，额外说明 `issuance` 或 `investment`，以及产品类型。

## 输入
- 合同文本（`.md`/`.docx`/`.pdf` 经抽取后的文本）。
- 可选：业务模式、立场（甲方/乙方/中立）、交付偏好（双层输出/交付版）。

## 输出
- 风险分级表（条款风险 + 严重度 + 依据 + 建议改写）。
- 可选：谈判策略 memo、合规工作底稿、批注版修改建议。

## 最小使用方式
- 对话触发（推荐）：描述合同类型、立场和目标，按 `SKILL.md` 流程执行。
- 若是资管场景：明确 `issuance` 或 `investment`，并声明产品类型。

## 依赖与边界
- 可复用 `_Skills/alts-review` 的部分审查资产（按 `SKILL.md` 定义）。
- 不承担路由编排职责；入口仍由会话层或 `system-router` 统一调度。
- 交付前建议执行 `checklists/` 门禁层，避免格式漂移与证据链缺口。
- 规范类文件位于 `protocols/`，模板类文件位于 `templates/`，知识索引位于 `knowledge_base/`。

## 失败与恢复
- 失败信号：文件版本不明、关键附件缺失、模式参数不完整。
- 恢复动作：先补齐资料清单，再重新触发 Phase 0 入场检查。
