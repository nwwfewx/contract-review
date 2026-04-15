# Output Requirements

## Output Requirements
Default output must use the fixed Markdown format below (same as `20-Areas-领域维护/💼工作_💰资产管理&保险资金运用/contract_review_20260204.md`) to avoid drift.

**Document block**
1. `Document`
2. `文件：<合同路径>`
3. `立场：<机构类型 | 部门角色 | 职级>`

**Main table (single table, fixed columns, in this exact order)**
1. 序号
2. 条款位置
3. 原文摘录
4. 风险类别
5. 风险描述
6. 触发后果
7. 修改建议
8. 反馈措辞（参考）
9. 推进前置条件

Do not change this default table schema unless the user explicitly asks for custom columns.

**If the user explicitly requests 审查依据/优先级**, add an appendix section after the main table, mapping `序号 -> 审查依据/优先级`, or extend the table only upon request.

**Email feedback option**
After delivering the review table, ask whether a “邮件反馈版本” is needed, and only draft it after user confirmation.

**Default delivery mode**
- Default is `delivery_only` (single main table).
- `dual_layer` (全景分析 + 交付版 + 差异说明) is opt-in only.

**DOCX 修订版交付（当用户需要 DOCX 审查落版时）**
- 默认只交付 **一个** DOCX 文件（同一文件内同时承载 Track Changes 与提示型 Comments）；除非用户明确要求“另出纯批注版”，否则不得并行交付“修订版 + 批注版”两份衍生文件。
- 先判定模式：
  - `layout-lock`：命中“分毫不差/沿用最新版/交付件/版式锁定”等严格排版要求。
  - `revision-docx`：常规 DOCX 审查修订交付（默认）。
- `layout-lock` 规则：
  - 以同类型项目最新定稿 `.doc/.docx` 为母版，先另存为，再原位定点改文。
  - 原位编辑优先使用 LibreOffice/Word/WPS 原生文档引擎；禁止引入 markdown/docx 重排链路。
  - 修改型动作仍走 **Track Changes**，提示型仍走 **Comments**。
  - 交付前必须完成旧项目残留词反查（项目名/主体名/旧资产名）并抽检封面、目录、核心表格。
- `revision-docx` 规则：
  - 默认使用 **Track Changes（修订模式）**，修改型操作直接写入 `<w:ins>` / `<w:del>` 修订标记。
  - 修订/批注作者名固定为：`WynnSing`。
  - 修改型操作（改为/删除/新增/补充/明确/限定等）→ **Track Changes**：在 Word 中显示为红色删除线（删除）和彩色下划线（插入），用户可逐条接受/拒绝。
  - 提示型信息（提示/关注/风险说明）→ **Comments（批注）**：仍然显示在批注栏中。
  - 不混写修改型和提示型内容。
- 修订定位规则（避免错位）：
  1) 优先用“原文摘录”片段定位段落和 run；
  2) 条款号仅匹配**段首**（如“第9条/9.1 …”），不要用裸数字匹配；
  3) 涉及“附件一/二/三/四”时仅在对应附件范围内定位；
  4) 若无法可靠匹配，宁可跳过并输出未命中清单。
- 兼容模式：`--mode comments-only --force-comments-only` 可回退至纯批注模式（所有操作都作为批注注入）。

**Non-citable delivery language (default)**
- Use conditional phrasing: “基于现有文本/资料”“可能/存在/需关注”
- Avoid absolute approvals; avoid “可以/没问题/合规无瑕疵”
- Add “供内部决策参考，不构成对业务结果的保证” when needed

**Dual-layer output (only when user requests 全景/双层输出)**
1. 全景分析（内部理解版）：See `templates/panoramic_analysis_template.md`
2. 交付版（对业务/可落地）：按主表输出
3. 差异说明（为何差异存在）：See `templates/delta_rationale_template.md`

**Optional appendices (only on explicit request)**
1. Risk grading appendix: severity × likelihood + escalation triggers. See `templates/risk_grading_template.md`.
2. Email feedback appendix: templated feedback email with “when not to use template” rules. See `templates/email_feedback_templates.md`.
3. Meeting brief appendix: negotiation/committee briefing with action items. See `templates/meeting_brief_template.md`.
4. Redline appendix: clause-by-clause replacement language and fallback positions.
5. Playbook deviation appendix: `序号 -> 偏离项 -> 允许范围/触发升级条件`.
6. NDA quick triage appendix: GREEN/YELLOW/RED routing. See `templates/nda_triage_template.md`.
7. Compliance mini-checklist appendix: DPA/个人信息处理要点。See `references/compliance_mini_checklist.md`.
8. General contract clauses checklist appendix: limitation of liability, dispute resolution, termination, confidentiality. See `references/general_clauses_checklist.md`.
9. Legal-basis verification appendix: `序号 -> 引用依据 -> 层级 -> 生效状态 -> 新旧法适用结论`.
10. Comparison/Causality appendix: `序号 -> entity_scope -> comparison_basis -> causality_chain -> scope_boundary`.
