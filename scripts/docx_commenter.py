#!/usr/bin/env python3
"""
docx_commenter.py — Dual-channel review dispatcher
=====================================================
Routes contract review findings to:
  1. Track Changes (修订模式) — for modification actions (改为/删除/新增)
  2. Comments (批注) — for advisory tips (提示/关注)

Usage:
  python3 docx_commenter.py --docx input.docx --review review.md --output out.docx
  python3 docx_commenter.py --docx input.docx --review review.md --output out.docx --mode comments-only --force-comments-only
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NSMAP = {"w": W_NS, "r": R_NS}


def _qn(tag):
    if ":" in tag:
        prefix, local = tag.split(":", 1)
        ns = {"w": W_NS, "r": R_NS}.get(prefix)
        return f"{{{ns}}}{local}"
    return tag


def _load_xml(path):
    return ET.parse(path)


def _save_xml(tree, path):
    tree.write(path, encoding="UTF-8", xml_declaration=True)


def _ensure_comments_part(doc_dir):
    comments_path = os.path.join(doc_dir, "word", "comments.xml")
    if not os.path.exists(comments_path):
        os.makedirs(os.path.dirname(comments_path), exist_ok=True)
        root = ET.Element(_qn("w:comments"))
        root.set("xmlns:w", W_NS)
        tree = ET.ElementTree(root)
        _save_xml(tree, comments_path)
    return comments_path


def _ensure_comments_relationship(doc_dir):
    rels_path = os.path.join(doc_dir, "word", "_rels", "document.xml.rels")
    tree = _load_xml(rels_path)
    root = tree.getroot()
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0].strip("{")
    def qn(local):
        return f"{{{ns}}}{local}" if ns else local
    for rel in root.findall(qn("Relationship")):
        if rel.get("Type") == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments":
            return
    new_id = f"rId{len(root.findall(qn('Relationship'))) + 1}"
    rel = ET.SubElement(root, qn("Relationship"))
    rel.set("Id", new_id)
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments")
    rel.set("Target", "comments.xml")
    _save_xml(tree, rels_path)


def _ensure_content_types(doc_dir):
    ct_path = os.path.join(doc_dir, "[Content_Types].xml")
    tree = _load_xml(ct_path)
    root = tree.getroot()
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0].strip("{")
    def qn(local):
        return f"{{{ns}}}{local}" if ns else local
    for ov in root.findall(qn("Override")):
        if ov.get("PartName") == "/word/comments.xml":
            return
    ov = ET.SubElement(root, qn("Override"))
    ov.set("PartName", "/word/comments.xml")
    ov.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml")
    _save_xml(tree, ct_path)


def _next_comment_id(comments_root):
    ids = []
    for c in comments_root.findall(_qn("w:comment")):
        cid = c.get(_qn("w:id"))
        if cid is not None:
            try:
                ids.append(int(cid))
            except ValueError:
                pass
    return (max(ids) + 1) if ids else 0


def _build_comment(comment_id, text, author="WynnSing"):
    c = ET.Element(_qn("w:comment"))
    c.set(_qn("w:id"), str(comment_id))
    c.set(_qn("w:author"), author)
    p = ET.SubElement(c, _qn("w:p"))
    r = ET.SubElement(p, _qn("w:r"))
    t = ET.SubElement(r, _qn("w:t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return c


def _build_comment_ref_run(comment_id):
    r = ET.Element(_qn("w:r"))
    rpr = ET.SubElement(r, _qn("w:rPr"))
    rstyle = ET.SubElement(rpr, _qn("w:rStyle"))
    rstyle.set(_qn("w:val"), "CommentReference")
    cref = ET.SubElement(r, _qn("w:commentReference"))
    cref.set(_qn("w:id"), str(comment_id))
    return r


def _insert_comment_markers(paragraph, comment_id):
    start = ET.Element(_qn("w:commentRangeStart"))
    start.set(_qn("w:id"), str(comment_id))
    paragraph.insert(0, start)
    end = ET.Element(_qn("w:commentRangeEnd"))
    end.set(_qn("w:id"), str(comment_id))
    paragraph.append(end)
    paragraph.append(_build_comment_ref_run(comment_id))


def add_comments(doc_dir, findings, author="WynnSing"):
    if not findings:
        return
    comments_path = _ensure_comments_part(doc_dir)
    _ensure_comments_relationship(doc_dir)
    _ensure_content_types(doc_dir)

    comments_tree = _load_xml(comments_path)
    comments_root = comments_tree.getroot()
    doc_path = os.path.join(doc_dir, "word", "document.xml")
    doc_tree = _load_xml(doc_path)
    doc_root = doc_tree.getroot()

    next_id = _next_comment_id(comments_root)

    for f in findings:
        anchor = f.get("anchor", "")
        comment_text = f.get("comment", "").strip()
        if not comment_text:
            continue
        p = _find_paragraph_by_anchor(doc_root, anchor)
        if p is None:
            continue
        comment_id = next_id
        next_id += 1
        _insert_comment_markers(p, comment_id)
        comments_root.append(_build_comment(comment_id, comment_text, author=author))

    _save_xml(doc_tree, doc_path)
    _save_xml(comments_tree, comments_path)


def _find_paragraph_by_anchor(doc_root, anchor):
    if not anchor:
        return None
    for p in doc_root.findall(".//w:p", NSMAP):
        texts = [t.text for t in p.findall(".//w:t", NSMAP) if t.text]
        if texts and anchor == "".join(texts):
            return p
    return None


def clear_existing_comments(doc_dir):
    # document.xml
    doc_path = os.path.join(doc_dir, "word", "document.xml")
    if os.path.exists(doc_path):
        tree = _load_xml(doc_path)
        root = tree.getroot()
        for parent in root.iter():
            for child in list(parent):
                if child.tag in {f"{{{W_NS}}}commentRangeStart", f"{{{W_NS}}}commentRangeEnd", f"{{{W_NS}}}commentReference"}:
                    parent.remove(child)
        _save_xml(tree, doc_path)
    # comments.xml
    comments_path = os.path.join(doc_dir, "word", "comments.xml")
    if os.path.exists(comments_path):
        os.remove(comments_path)
    # rels
    rels_path = os.path.join(doc_dir, "word", "_rels", "document.xml.rels")
    if os.path.exists(rels_path):
        tree = _load_xml(rels_path)
        root = tree.getroot()
        for rel in list(root):
            if rel.get("Type") == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments":
                root.remove(rel)
        _save_xml(tree, rels_path)
    # content types
    ct_path = os.path.join(doc_dir, "[Content_Types].xml")
    if os.path.exists(ct_path):
        tree = _load_xml(ct_path)
        root = tree.getroot()
        for ov in list(root):
            if ov.get("PartName") == "/word/comments.xml":
                root.remove(ov)
        _save_xml(tree, ct_path)


def extract_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paras = []
    for p in root.findall(".//w:p", NSMAP):
        texts = [t.text for t in p.findall(".//w:t", NSMAP) if t.text]
        if texts:
            paras.append("".join(texts))
    return paras


def parse_review_table(md_path):
    rows = []
    lines = md_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        if line.strip().startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 9:
            continue
        row = {
            "序号": parts[0],
            "条款位置": parts[1],
            "原文摘录": parts[2],
            "风险类别": parts[3],
            "风险描述": parts[4],
            "触发后果": parts[5],
            "修改建议": parts[6],
            "反馈措辞": parts[7],
            "推进前置条件": parts[8],
        }
        if row["序号"].isdigit():
            rows.append(row)
    return rows


def build_appendix_ranges(paras):
    starts = []
    for i, p in enumerate(paras):
        if re.match(r"^\s*附件[一二三四五六七八九十]+", p):
            starts.append((p.strip(), i))
    starts.sort(key=lambda x: x[1])
    ranges = {}
    for idx, (title, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(paras)
        ranges[title[:3]] = (start, end)
    main_range = (0, starts[0][1] if starts else len(paras))
    return main_range, ranges


def norm(s: str) -> str:
    s = s.replace("“", "").replace("”", "").replace('"', "")
    s = s.replace("…", "").replace("...", "")
    s = re.sub(r"\s+", "", s)
    return s


def extract_segments(s: str):
    s = s.replace("“", "").replace("”", "").replace('"', "")
    s = s.replace("…", "...")
    parts = [p for p in re.split(r"\.{2,}", s) if p.strip()]
    segs = []
    for part in parts:
        segs.extend([seg.strip() for seg in re.split(r"[；;。！？!?,，、\n]", part) if seg.strip()])
    segs = [seg.strip('"“”') for seg in segs if seg.strip('"“”')]
    segs = [seg for seg in segs if len(seg) >= 4]
    segs.sort(key=len, reverse=True)
    return segs


def clause_patterns(num: str):
    num_esc = re.escape(num)
    return [
        re.compile(rf"^\s*第{num_esc}条"),
        re.compile(rf"^\s*{num_esc}(?=\s|[、.．)]|[\u4e00-\u9fff])"),
    ]


def clause_match(p: str, nums):
    for num in nums:
        for pat in clause_patterns(num):
            if pat.search(p):
                return True
    return False


def score_para(p: str, segments, nums, keywords, full_excerpt):
    p_norm = norm(p)
    seg_score = 0
    for seg in segments:
        if norm(seg) in p_norm:
            seg_score += len(seg)
    kw_score = sum(1 for kw in keywords if kw and kw in p)
    clause_score = 80 if clause_match(p, nums) else 0
    ratio = SequenceMatcher(None, norm(full_excerpt), p_norm).ratio() if full_excerpt else 0
    score = seg_score * 2 + kw_score * 10 + clause_score + ratio * 40
    return score, seg_score, kw_score, ratio


def extract_keywords(location: str):
    loc = re.sub(r"第\d+(?:\.\d+)*条", "", location)
    loc = re.sub(r"附件[一二三四五六七八九十]", "", loc)
    loc = loc.replace("；", "/").replace(";", "/").replace("“", "").replace("”", "")
    parts = re.split(r"[/、,，\s]+", loc)
    return [p for p in parts if len(p) >= 2]


def extract_seg_keywords(segments):
    kws = []
    for seg in segments:
        if len(seg) >= 4:
            kws.append(seg[:4])
            kws.append(seg[-4:])
        if len(seg) >= 3:
            kws.append(seg[:3])
            kws.append(seg[-3:])
    # dedupe while preserving order
    seen = set()
    out = []
    for k in kws:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def select_best_para(paras, segments, nums, keywords, full_excerpt, ratio_threshold=0.55):
    best = (0, None, 0, 0, 0)
    for p in paras:
        score, seg_score, kw_score, ratio = score_para(p, segments, nums, keywords, full_excerpt)
        if score > best[0]:
            best = (score, p, seg_score, kw_score, ratio)
    if best[1] is None:
        return None, 0
    # accept only with strong evidence
    if best[2] == 0 and best[3] == 0 and not clause_match(best[1], nums) and best[4] < ratio_threshold:
        return None, 0
    return best[1], best[2]


def best_segment_in_para(segments, para):
    if not segments:
        return ""
    p_norm = norm(para)
    for seg in segments:
        if norm(seg) in p_norm:
            return seg
    return ""


def split_actions(s: str):
    s = re.sub(r"^建议", "", s.strip()).strip()
    if not s:
        return []
    parts = [p.strip() for p in re.split(r"[；;。]", s) if p.strip()]
    out = []
    for part in parts:
        if "并" in part and any(v in part for v in ["新增", "删除", "改为", "合并", "移动", "调整", "补充", "明确", "设定", "限定", "统一", "增加"]):
            out.extend([p.strip() for p in part.split("并") if p.strip()])
        else:
            out.append(part)
    return out


# ── Action classification ─────────────────────────────────────

_MODIFY_VERBS = ("改为", "调整", "修订")
_DELETE_VERBS = ("删除",)
_INSERT_VERBS = ("新增", "增加", "补充", "明确", "设定", "限定", "列明", "统一", "约定", "增加")
_COMPLEX_VERBS = ("合并", "移动")  # stay as comments for now


def classify_action(action: str) -> str:
    """
    Classify an action string into a channel:
      'track_change' — will be applied as Word Track Changes
      'comment'      — will be injected as a Word comment
    """
    action = action.strip().rstrip("。")
    if action.startswith(_DELETE_VERBS):
        return "track_change"
    if action.startswith(_MODIFY_VERBS):
        return "track_change"
    if action.startswith(_INSERT_VERBS):
        return "track_change"
    # Complex verbs (合并/移动) are hard to automate — keep as comments
    return "comment"


def action_to_revision(action: str, old_text: str, para_text: str) -> dict:
    """
    Convert an action string into a revision dict for docx_track_changes.
    Returns {"action": "replace"/"delete"/"insert", "old_text": ..., "new_text": ...}
    """
    action = action.strip().rstrip("。")
    old_exists = bool(old_text and old_text in para_text and len(old_text) >= 4)

    if action.startswith(_DELETE_VERBS):
        # "删除xxx" or just "删除"
        if old_exists:
            return {"action": "delete", "old_text": old_text, "new_text": ""}
        return {"action": "delete", "old_text": action[2:].strip('"\u201c\u201d') or old_text, "new_text": ""}

    if action.startswith(_INSERT_VERBS):
        content = action
        for v in _INSERT_VERBS:
            if content.startswith(v):
                content = content[len(v):].strip()
                break
        content = content.strip('"\u201c\u201d')
        return {"action": "insert", "old_text": old_text if old_exists else "", "new_text": content}

    if action.startswith(_MODIFY_VERBS):
        content = action
        for v in _MODIFY_VERBS:
            if content.startswith(v):
                content = content[len(v):].strip()
                break
        content = content.strip('"\u201c\u201d')
        if old_exists:
            return {"action": "replace", "old_text": old_text, "new_text": content}
        return {"action": "insert", "old_text": "", "new_text": content}

    # Default: if we have old text, treat as replace; otherwise insert
    if old_exists:
        return {"action": "replace", "old_text": old_text, "new_text": action}
    return {"action": "insert", "old_text": "", "new_text": action}


def action_comment(action: str, old_text: str, para_text: str):
    """Format an action as comment text (used for comment-only channel)."""
    action = action.strip().rstrip("。")
    old_exists = bool(old_text and old_text in para_text and len(old_text) >= 8)
    if action.startswith("删除"):
        return f"删除“{old_text}”。" if old_exists else "删除相关表述。"
    if action.startswith(("新增", "增加", "补充", "明确", "设定", "限定", "列明", "统一", "约定")):
        content = action
        for v in ("新增", "增加", "补充", "明确", "设定", "限定", "列明", "统一", "约定"):
            if content.startswith(v):
                content = content[len(v):].strip()
                break
        return f"新增“{content}”。" if content else "新增相关表述。"
    if action.startswith(("合并", "移动")):
        return action + "。"
    if action.startswith(("改为", "调整", "修订")):
        content = action
        for v in ("改为", "调整", "修订"):
            if content.startswith(v):
                content = content[len(v):].strip()
                break
        if old_exists:
            return f"将“{old_text}”改为“{content}”。"
        return f"新增“{content}”。"
    # default
    if old_exists:
        return f"将“{old_text}”改为“{action}”。"
    return f"新增“{action}”。"


def build_findings(rows, paras, main_range, appendix_ranges, notes=False,
                   use_track_changes=True):
    """
    Build findings from review table rows.

    Returns (revisions, comments, unmatched):
      - revisions: list of dicts for docx_track_changes (modification actions)
      - comments: list of dicts for Word comments (tips + complex actions)
      - unmatched: rows that could not be anchored to any paragraph
    """
    revisions = []
    comments = []
    unmatched = []
    for row in rows:
        nums = re.findall(r"\d+(?:\.\d+)*", row["条款位置"])
        segments = extract_segments(row["原文摘录"])
        keywords = extract_keywords(row["条款位置"])
        keywords += extract_seg_keywords(segments)

        ranges = []
        if "附件" in row["条款位置"]:
            for key, (s, e) in appendix_ranges.items():
                if key in row["条款位置"]:
                    ranges.append((s, e))
        if "第" in row["条款位置"] or "条" in row["条款位置"]:
            ranges.append(main_range)
        if not ranges:
            ranges = [main_range]

        # prefer ranges with segment matches
        best_para = None
        best_seg = 0
        best_score = -1
        for s, e in ranges:
            ratio_threshold = 0.55
            if "附件" in row["条款位置"] and not nums and not keywords:
                ratio_threshold = 0.45
            p, seg_score = select_best_para(paras[s:e], segments, nums, keywords, row["原文摘录"], ratio_threshold=ratio_threshold)
            if p:
                score, _, _, _ = score_para(p, segments, nums, keywords, row["原文摘录"])
                if seg_score > 0 and seg_score >= best_seg:
                    best_seg = seg_score
                    best_para = p
                    best_score = score
                elif best_para is None and score > best_score:
                    best_para = p
                    best_score = score

        if not best_para:
            unmatched.append(row)
            continue

        actions = split_actions(row["修改建议"] or "")
        old_text = best_segment_in_para(segments, best_para)

        for action in actions:
            channel = classify_action(action) if use_track_changes else "comment"

            if channel == "track_change":
                rev = action_to_revision(action, old_text, best_para)
                rev["anchor"] = best_para
                revisions.append(rev)
            else:
                comments.append({
                    "anchor": best_para,
                    "comment": action_comment(action, old_text, best_para)
                })

        if notes:
            note = row["风险描述"]
            if row["触发后果"]:
                note = f"{note}；{row['触发后果']}"
            if note:
                comments.append({"anchor": best_para, "comment": f"提示：{note}"})

    return revisions, comments, unmatched


def main():
    ap = argparse.ArgumentParser(
        description="Contract review → docx dispatcher (track changes + comments)"
    )
    ap.add_argument("--docx", required=True, help="Input .docx file")
    ap.add_argument("--review", required=True, help="Review table .md file")
    ap.add_argument("--output", required=True, help="Output .docx file")
    ap.add_argument("--author", default="WynnSing", help="Author name")
    ap.add_argument("--clear-existing", action="store_true",
                    help="Clear existing comments before adding new ones")
    ap.add_argument("--notes", action="store_true",
                    help="Include risk notes as comments")
    ap.add_argument("--mode", choices=["track-changes", "comments-only"],
                    default="track-changes",
                    help="Output mode: 'track-changes' (default) routes "
                         "modifications to Word Track Changes; "
                         "'comments-only' uses comments for everything (legacy, fallback)")
    ap.add_argument("--force-comments-only", action="store_true",
                    help="Required with --mode comments-only to avoid accidental pure-comment delivery")
    args = ap.parse_args()

    if args.mode == "comments-only" and not args.force_comments_only:
        raise SystemExit(
            "Refusing comments-only without explicit override. "
            "Use '--mode comments-only --force-comments-only' only when user explicitly requires pure comments."
        )

    use_track_changes = (args.mode == "track-changes")

    paras = extract_paragraphs(args.docx)
    main_range, appendix_ranges = build_appendix_ranges(paras)
    rows = parse_review_table(Path(args.review))

    revisions, comments, unmatched = build_findings(
        rows, paras, main_range, appendix_ranges,
        notes=args.notes, use_track_changes=use_track_changes
    )

    if unmatched:
        print(f"⚠️  Unmatched IDs: {[r['序号'] for r in unmatched]}")

    # ── Channel 1: Track Changes (修订模式) ──
    if revisions:
        # Import track changes engine (same directory)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, script_dir)
        from docx_track_changes import apply_revisions as _apply_tc

        # First save with track changes to a temp file, then add comments on top
        tc_tmp = tempfile.mktemp(suffix=".docx", prefix="tc_")
        tc_unmatched = _apply_tc(args.docx, tc_tmp, revisions, author=args.author)
        if tc_unmatched:
            print(f"⚠️  {len(tc_unmatched)} track-change revision(s) unmatched")
        print(f"✅ {len(revisions) - len(tc_unmatched)} revision(s) applied as Track Changes")
        docx_for_comments = tc_tmp
    else:
        docx_for_comments = args.docx

    # ── Channel 2: Comments (批注) ──
    if comments:
        tmp = tempfile.mkdtemp(prefix="docx_commenter_")
        try:
            with zipfile.ZipFile(docx_for_comments, "r") as zf:
                zf.extractall(tmp)
            if args.clear_existing:
                clear_existing_comments(tmp)
            add_comments(tmp, comments, author=args.author)
            base = os.path.splitext(args.output)[0]
            if os.path.exists(args.output):
                os.remove(args.output)
            shutil.make_archive(base, "zip", tmp)
            os.rename(base + ".zip", args.output)
        finally:
            shutil.rmtree(tmp)
        print(f"✅ {len(comments)} comment(s) added")
    elif revisions:
        # No comments, just copy track-changes result
        shutil.copy2(docx_for_comments, args.output)
    else:
        # Nothing to do, copy original
        shutil.copy2(args.docx, args.output)

    # Cleanup temp track-changes file
    if revisions and os.path.exists(tc_tmp):
        os.remove(tc_tmp)

    print(f"📄 Output: {args.output}")


if __name__ == "__main__":
    main()
