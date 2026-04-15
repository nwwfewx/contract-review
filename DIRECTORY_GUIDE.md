# contract-review Directory Guide

## Canonical Entry
- `SKILL.md`：唯一执行入口与行为契约。
- `references/loading_map_and_dependencies.md`：上下文加载与依赖索引。

## Directory Boundaries
- `checklists/`：交付门禁（回答“这次有没有做到位”）。
- `protocols/`：硬规则与证据/否决/版本等规范协议。
- `templates/`：输出模板与文案模板资产。
- `references/`：路由、流程、场景清单、外部方法映射等“怎么做”说明。
- `knowledge_base/`：知识索引与知识库条目。
- `scripts/`：可执行工具（结构提取、DOCX 修订/批注）。
- `evals/`：评测样例定义。

## Placement Rules
1. 新增“审查要点”优先放 `references/checklist_*.md`。  
2. 新增“放行标准/发布标准”放 `checklists/`。  
3. 新增“硬性约束/字段协议”放 `protocols/`。  
4. 新增“产物模板/措辞模板”放 `templates/`。  
5. 新增“可执行逻辑”放 `scripts/`，避免把算法堆进 `SKILL.md`。  

## Migration Note
- 旧路径 `references/hard_*.md`、`references/*_template.md`、根目录 `KNOWLEDGE_INDEX.md` 已迁移。
- 若发现旧路径引用，以本文件和 `references/loading_map_and_dependencies.md` 为准更新。
