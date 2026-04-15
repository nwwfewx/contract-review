#!/usr/bin/env python3
"""Extract contract structure (chapter tree + key clause locations + risk hints).

Usage:
  python extract_contract_structure.py --input contract.docx --output structure.json
  python extract_contract_structure.py --input contract.md --output structure.json

Supports: .docx, .md, .txt
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Optional

# Heading patterns for different formats
HEADING_PATTERNS = [
    # Markdown headings
    re.compile(r"^#{1,6}\s+(.+)$"),
    # Chinese chapter/section format
    re.compile(r"^第[一二三四五六七八九十百千零0-9]+[章节条款项]\s*[:：]?\s*(.+)?$"),
    # Numbered outline (1.2.3)
    re.compile(r"^([0-9]+(?:\.[0-9]+)*)\s+(.+)$"),
    # Chinese number outline
    re.compile(r"^（[一二三四五六七八九十]+）\s*(.+)?$"),
    re.compile(r"^\([0-9]+\)\s*(.+)?$"),
]

# Key clause indicators
CLAUSE_KEYWORDS = [
    "甲方", "乙方", "丙方", "任一方", "双方",
    "违约", "赔偿", "解除", "终止",
    "争议", "管辖", "仲裁",
    "保密", "知识产权",
    "付款", "结算", "发票",
    "交付", "验收", "期限",
    "担保", "抵押", "质押",
    "不可抗力", "免责",
    "生效", "盖章", "签字",
]
CLAUSE_HINT = re.compile(r"^(" + "|".join(CLAUSE_KEYWORDS) + ")")

# Risk hint patterns (from 26 golden rules)
RISK_HINTS = {
    "格式合同风险": re.compile(r"(格式合同|无法修改|不可修改)"),
    "倒签合同风险": re.compile(r"(倒签|补签|已实际履行)"),
    "关联交易风险": re.compile(r"(关联方|关联交易|子公司)"),
    "违约金过高": re.compile(r"(违约金|赔偿金额|损失赔偿).{0,30}(100%|200%|全部|倍)"),
    "定金条款": re.compile(r"定金"),
    "保密期限过短": re.compile(r"保密.{0,10}(一年|1年|两年|2年|三年)"),
    "管辖约定问题": re.compile(r"(仲裁|诉讼).{0,20}(对方|乙方|甲方).{0,10}(所在地|住所地)"),
    "印章效力问题": re.compile(r"(截图印章|部门章|扫描件.{0,5}盖章)"),
    "生效条件问题": re.compile(r"(签字盖章|签字、盖章|签字并盖章).{0,10}生效"),
    "被执行人风险": re.compile(r"被执行人"),
    "分公司签约": re.compile(r"(分公司|办事处).{0,10}(签署|签订|盖章)"),
    "附件效力未约定": re.compile(r"附件.{0,30}(未约定|效力|组成部分)"),
    "金额大小写": re.compile(r"(大写|小写).{0,10}(金额|价款|费用)"),
}


def extract_paragraphs_from_docx(docx_path: Path) -> list[str]:
    """Extract text paragraphs from DOCX file."""
    try:
        from docx import Document
        doc = Document(str(docx_path))
        return [p.text for p in doc.paragraphs if p.text.strip()]
    except ImportError:
        raise SystemExit(
            "python-docx not installed. Run: pip install python-docx\n"
            "Or process as .txt/.md instead."
        )


def extract_structure(lines: list[str]) -> dict:
    """Extract chapter tree, key clauses, and risk hints from lines."""
    headings = []
    clauses = []
    risk_findings = []

    for i, line in enumerate(lines, start=1):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Detect headings
        for p in HEADING_PATTERNS:
            m = p.match(line_stripped)
            if m:
                title = m.group(1) if m.groups() else line_stripped
                headings.append({
                    "line": i,
                    "text": line_stripped[:100],  # truncate long headings
                    "title": (title or "").strip()[:80],
                })
                break

        # Detect key clause indicators
        if CLAUSE_HINT.match(line_stripped):
            clauses.append({
                "line": i,
                "keyword": CLAUSE_HINT.match(line_stripped).group(1),
                "text": line_stripped[:150],
            })

        # Detect risk hints
        for risk_name, pattern in RISK_HINTS.items():
            if pattern.search(line_stripped):
                risk_findings.append({
                    "line": i,
                    "risk_type": risk_name,
                    "text": line_stripped[:150],
                })

    return {
        "summary": {
            "total_lines": len(lines),
            "headings_count": len(headings),
            "clause_hints_count": len(clauses),
            "risk_hints_count": len(risk_findings),
        },
        "chapter_tree": headings,
        "key_clauses": clauses,
        "risk_hints": risk_findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract contract structure: chapter tree + key clauses + risk hints"
    )
    parser.add_argument("--input", "-i", required=True, help="Path to .docx/.md/.txt file")
    parser.add_argument("--output", "-o", help="Path to output JSON; default <input>.structure.json")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    # Read content based on file type
    suffix = input_path.suffix.lower()
    if suffix == ".docx":
        paragraphs = extract_paragraphs_from_docx(input_path)
        lines = paragraphs
    else:
        content = input_path.read_text(encoding="utf-8", errors="ignore")
        lines = [line.rstrip() for line in content.splitlines()]

    result = extract_structure(lines)

    # Output
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_suffix(input_path.suffix + ".structure.json")
    )

    if args.format == "markdown":
        output_path = output_path.with_suffix(".structure.md")
        md_content = format_as_markdown(result)
        output_path.write_text(md_content, encoding="utf-8")
    else:
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[DONE] Wrote structure to: {output_path}")
    print(f"  - Headings: {result['summary']['headings_count']}")
    print(f"  - Clause hints: {result['summary']['clause_hints_count']}")
    print(f"  - Risk hints: {result['summary']['risk_hints_count']}")


def format_as_markdown(result: dict) -> str:
    """Format result as Markdown for human review."""
    lines = ["# 合同结构提取报告\n"]

    # Summary
    s = result["summary"]
    lines.append(f"**总行数**: {s['total_lines']} | **章节**: {s['headings_count']} | "
                 f"**关键条款**: {s['clause_hints_count']} | **风险提示**: {s['risk_hints_count']}\n")

    # Chapter tree
    lines.append("## 章节树\n")
    for h in result["chapter_tree"]:
        lines.append(f"- L{h['line']}: {h['title'] or h['text']}")

    # Key clauses
    lines.append("\n## 关键条款定位\n")
    lines.append("| 行号 | 关键词 | 条款摘录 |")
    lines.append("|------|--------|----------|")
    for c in result["key_clauses"][:30]:  # limit display
        lines.append(f"| {c['line']} | {c['keyword']} | {c['text'][:60]}... |")

    # Risk hints
    if result["risk_hints"]:
        lines.append("\n## ⚠️ 风险预警\n")
        lines.append("| 行号 | 风险类型 | 触发文本 |")
        lines.append("|------|----------|----------|")
        for r in result["risk_hints"]:
            lines.append(f"| {r['line']} | {r['risk_type']} | {r['text'][:60]}... |")

    return "\n".join(lines)


if __name__ == "__main__":
    main()

