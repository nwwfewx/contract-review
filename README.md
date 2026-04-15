# contract-review

适用于 Codex / Claude 等代理的合同审查技能（开源独立版）。

> 免责声明：本仓库提供的是审查工作流与辅助模板，不构成正式法律意见或律师执业服务。

## 这是什么

`contract-review` 用于把合同审查流程标准化为可执行步骤，输出结构化风险结论和可落地修改建议。

开源版设计目标：
- 独立可用：不依赖私有目录、私有路由器或其它私有技能。
- 新手友好：安装后可直接按示例触发。
- 结果可交付：默认输出风险主表，必要时再扩展附录。

## 核心能力

| 模式 | 适用场景 | 默认输出 |
|---|---|---|
| `general` | 通用合同（采购、服务、委托、租赁等） | 风险清单 + 条款修改建议 |
| `asset_mgmt:issuance` | 资管发行端 | 合规风险清单 + 修订建议 |
| `asset_mgmt:investment:alternative` | 资管投资端（另类） | 合规风险清单 + 修订建议 |
| `asset_mgmt:investment:standardized` | 资管投资端（标准化） | 合规风险清单 + 修订建议 |

专项叠加：
- 托管协议场景会自动叠加 `custody_overlay`（不改变主模式）。

交付模式：
- `delivery_only`（默认）：单主表交付。
- `dual_layer`（按需）：在交付版外增加分析层输出。

## 安装

### Codex

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/nwwfewx/contract-review.git ~/.codex/skills/contract-review
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/nwwfewx/contract-review.git ~/.claude/skills/contract-review
```

安装注意：
- 保持目录名为 `contract-review`。
- 保留 `SKILL.md` 文件名不变。
- 一并保留 `references/`、`checklists/`、`protocols/`、`templates/`。

## 快速开始

最小触发信息：
1. 业务场景（`general` 或 `asset_mgmt:*`）
2. 立场（甲方 / 乙方 / 中立）
3. 合同状态（草稿 / 待签 / 已签 / 用印）
4. 合同文本（或文件路径）

示例 1（通用合同）：

```text
请按 contract-review 审查这份服务合同。
模式：general
立场：甲方
合同状态：待签
输出：delivery_only
```

示例 2（资管发行）：

```text
请按 contract-review 审查这份资管产品合同。
模式：asset_mgmt:issuance
立场：管理人（甲方）
合同状态：草稿
输出：delivery_only
```

示例 3（托管协议叠加）：

```text
请按 contract-review 审查这份托管协议。
模式：asset_mgmt:issuance
立场：管理人
合同状态：待签
并启用托管协议专项检查。
```

## 输入与输出

输入：
- 合同文本（`.md` / `.docx` / `.pdf` 抽取后文本）
- 可选参数：业务模式、立场、交付偏好

输出：
- 主输出：风险分级表（条款位置 + 风险描述 + 严重度 + 依据 + 建议改写）
- 可选附录：谈判策略 memo、合规工作底稿、批注建议

## 仓库结构

```text
.
├── SKILL.md
├── README.md
├── DIRECTORY_GUIDE.md
├── checklists/
├── protocols/
├── references/
├── templates/
├── scripts/
├── knowledge_base/
└── evals/
```

说明：
- 人类说明以 `README.md` 为主。
- 代理执行契约以 `SKILL.md` 为主。
- 二者冲突时，以 `SKILL.md` 为准。

## 开源版与本地增强版

- 开源版（本仓库）：强调独立可用、可快速安装、默认可交付。
- 本地增强版（你的私有工作区）：可以叠加更多内部资料、历史模板、跨技能协作。
- 在开源仓库中，外部模板库仅是可选增强，不是前置依赖。

## FAQ

### 为什么仓库里没有 `smoke_outputs` 的 DOCX 示例文件？

这些文件是历史 smoke test 产物，不属于执行依赖，且会增加二进制体积。开源版默认不纳入仓库。

如需示例，建议新增 `examples/` 并放脱敏样例，配套写清输入和期望输出。

## License

MIT，见 `LICENSE`。
