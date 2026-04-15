#!/usr/bin/env python3
"""
docx_track_changes.py
=====================
Apply Word Track Changes (修订模式) directly to .docx files.

Uses lxml (bundled with python-docx) to inject <w:ins> / <w:del> revision
markup into the document XML.  The result opens in Word with standard
tracked‑changes UI – users can Accept / Reject each revision.

Usage (standalone):
    python3 docx_track_changes.py \
        --docx input.docx \
        --output output.docx \
        --revisions revisions.json \
        --author WynnSing

Revisions JSON format:
[
  {
    "anchor": "paragraph full text for locating",
    "action": "replace",       // "replace" | "delete" | "insert"
    "old_text": "text to find in paragraph",
    "new_text": "replacement text"
  },
  ...
]

API usage (imported by docx_commenter.py):
    from docx_track_changes import apply_revisions_to_doc
    apply_revisions_to_doc(doc, revisions, author="WynnSing")
"""

import argparse
import copy
import json
import re
from datetime import datetime

from docx import Document
from lxml import etree

# ── XML namespaces ────────────────────────────────────────────
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _qn(tag: str) -> str:
    """Qualified name helper, e.g. _qn('w:ins') → '{...}ins'."""
    prefix, local = tag.split(":")
    ns = {"w": W_NS}[prefix]
    return f"{{{ns}}}{local}"


# ── Revision ID generator ────────────────────────────────────
_REV_ID_COUNTER = 1000


def _next_rev_id() -> str:
    global _REV_ID_COUNTER
    _REV_ID_COUNTER += 1
    return str(_REV_ID_COUNTER)


# ── Core revision primitives ─────────────────────────────────


def _copy_rpr(run_elem):
    """Deep-copy the <w:rPr> from a run element, or return None."""
    rpr = run_elem.find(_qn("w:rPr"))
    return copy.deepcopy(rpr) if rpr is not None else None


def insert_text_after_run(run_elem, text: str, author: str, date: str):
    """Insert *text* as a tracked insertion (<w:ins>) right after *run_elem*."""
    parent = run_elem.getparent()
    run_idx = list(parent).index(run_elem)

    ins = etree.Element(_qn("w:ins"))
    ins.set(_qn("w:id"), _next_rev_id())
    ins.set(_qn("w:author"), author)
    ins.set(_qn("w:date"), date)

    new_run = etree.SubElement(ins, _qn("w:r"))
    rpr = _copy_rpr(run_elem)
    if rpr is not None:
        new_run.insert(0, rpr)

    t = etree.SubElement(new_run, _qn("w:t"))
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    parent.insert(run_idx + 1, ins)
    return ins


def insert_text_before_run(run_elem, text: str, author: str, date: str):
    """Insert *text* as a tracked insertion (<w:ins>) right before *run_elem*."""
    parent = run_elem.getparent()
    run_idx = list(parent).index(run_elem)

    ins = etree.Element(_qn("w:ins"))
    ins.set(_qn("w:id"), _next_rev_id())
    ins.set(_qn("w:author"), author)
    ins.set(_qn("w:date"), date)

    new_run = etree.SubElement(ins, _qn("w:r"))
    rpr = _copy_rpr(run_elem)
    if rpr is not None:
        new_run.insert(0, rpr)

    t = etree.SubElement(new_run, _qn("w:t"))
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    parent.insert(run_idx, ins)
    return ins


def delete_run(run_elem, author: str, date: str):
    """Wrap *run_elem* in <w:del> and convert <w:t> → <w:delText>."""
    parent = run_elem.getparent()
    run_idx = list(parent).index(run_elem)

    del_elem = etree.Element(_qn("w:del"))
    del_elem.set(_qn("w:id"), _next_rev_id())
    del_elem.set(_qn("w:author"), author)
    del_elem.set(_qn("w:date"), date)

    parent.remove(run_elem)
    del_elem.append(run_elem)

    for t in run_elem.findall(_qn("w:t")):
        t.tag = _qn("w:delText")

    parent.insert(run_idx, del_elem)
    return del_elem


def replace_run(run_elem, new_text: str, author: str, date: str):
    """
    Replace the text content of *run_elem* – produces a <w:del> + <w:ins>
    pair, which Word shows as a tracked replacement.
    """
    rpr = _copy_rpr(run_elem)
    del_elem = delete_run(run_elem, author, date)

    parent = del_elem.getparent()
    del_idx = list(parent).index(del_elem)

    ins = etree.Element(_qn("w:ins"))
    ins.set(_qn("w:id"), _next_rev_id())
    ins.set(_qn("w:author"), author)
    ins.set(_qn("w:date"), date)

    new_run = etree.SubElement(ins, _qn("w:r"))
    if rpr is not None:
        new_run.insert(0, rpr)

    t = etree.SubElement(new_run, _qn("w:t"))
    t.text = new_text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    parent.insert(del_idx + 1, ins)
    return del_elem, ins


# ── Paragraph / run matching ─────────────────────────────────


def _norm(s: str) -> str:
    """Normalise whitespace for matching."""
    return re.sub(r"\s+", "", s)


def _get_paragraph_text(p_elem) -> str:
    """Extract full text from a paragraph element."""
    texts = []
    for t in p_elem.findall(f".//{_qn('w:t')}"):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _find_paragraph(body, anchor: str):
    """Find the paragraph element whose text best matches *anchor*."""
    anchor_norm = _norm(anchor)
    if not anchor_norm:
        return None
    for p in body.findall(f".//{_qn('w:p')}"):
        if _norm(_get_paragraph_text(p)) == anchor_norm:
            return p
    # Fallback: substring match (anchor may be truncated)
    best, best_len = None, 0
    for p in body.findall(f".//{_qn('w:p')}"):
        p_norm = _norm(_get_paragraph_text(p))
        if anchor_norm in p_norm and len(p_norm) > best_len:
            best, best_len = p, len(p_norm)
    return best


def _find_runs_containing(p_elem, target: str):
    """
    Find the run(s) in *p_elem* that contain *target*.
    Returns (runs_list, match_type):
      - ('single', [run])  if target is fully contained in one run
      - ('multi', [r1, r2, ...]) if target spans multiple consecutive runs
      - ('none', []) if not found
    """
    runs = p_elem.findall(_qn("w:r"))
    if not runs:
        return "none", []

    target_norm = _norm(target)

    # 1) Check single-run match
    for r in runs:
        t_elem = r.find(_qn("w:t"))
        if t_elem is not None and t_elem.text and _norm(t_elem.text) and target_norm in _norm(t_elem.text):
            return "single", [r]

    # 2) Check multi-run span
    for start_idx in range(len(runs)):
        combined = ""
        span = []
        for r in runs[start_idx:]:
            t_elem = r.find(_qn("w:t"))
            if t_elem is not None and t_elem.text:
                combined += t_elem.text
                span.append(r)
                if _norm(target) in _norm(combined):
                    return "multi", span

    return "none", []


def _split_run_at(run_elem, target: str):
    """
    Split a run so that *target* is isolated in its own run.
    Returns (pre_run_or_None, target_run, post_run_or_None).
    All three inherit the original run's formatting.
    """
    t_elem = run_elem.find(_qn("w:t"))
    if t_elem is None or not t_elem.text:
        return None, run_elem, None

    full = t_elem.text
    # Find target position (case-sensitive first, then normalised)
    idx = full.find(target)
    if idx < 0:
        # Try normalised match — find the substring boundaries
        fn = _norm(full)
        tn = _norm(target)
        nidx = fn.find(tn)
        if nidx < 0:
            return None, run_elem, None
        # Map normalised index back to original string
        orig_pos = 0
        norm_pos = 0
        while norm_pos < nidx and orig_pos < len(full):
            if not full[orig_pos].isspace():
                norm_pos += 1
            orig_pos += 1
        idx = orig_pos
        # find end
        end_norm = nidx + len(tn)
        while norm_pos < end_norm and orig_pos < len(full):
            if not full[orig_pos].isspace():
                norm_pos += 1
            orig_pos += 1
        end_idx = orig_pos
        target_actual = full[idx:end_idx]
    else:
        target_actual = target
        end_idx = idx + len(target)

    parent = run_elem.getparent()
    run_idx = list(parent).index(run_elem)
    rpr = _copy_rpr(run_elem)

    result_pre, result_target, result_post = None, None, None

    pre_text = full[:idx]
    mid_text = target_actual
    post_text = full[end_idx:]

    # Build pre run
    if pre_text:
        pre_run = etree.Element(_qn("w:r"))
        if rpr is not None:
            pre_run.append(copy.deepcopy(rpr))
        pre_t = etree.SubElement(pre_run, _qn("w:t"))
        pre_t.text = pre_text
        pre_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        parent.insert(run_idx, pre_run)
        run_idx += 1
        result_pre = pre_run

    # Modify original run to contain only target text
    t_elem.text = mid_text
    result_target = run_elem

    # Build post run
    if post_text:
        post_run = etree.Element(_qn("w:r"))
        if rpr is not None:
            post_run.append(copy.deepcopy(rpr))
        post_t = etree.SubElement(post_run, _qn("w:t"))
        post_t.text = post_text
        post_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        parent.insert(run_idx + 1, post_run)
        result_post = post_run

    return result_pre, result_target, result_post


# ── High-level apply functions ────────────────────────────────


def _apply_delete(p_elem, old_text: str, author: str, date: str) -> bool:
    """Delete *old_text* from paragraph with tracked change."""
    match_type, runs = _find_runs_containing(p_elem, old_text)
    if match_type == "none":
        return False

    if match_type == "single":
        run = runs[0]
        t_elem = run.find(_qn("w:t"))
        if t_elem is not None and _norm(t_elem.text) == _norm(old_text):
            # Whole run matches → delete entire run
            delete_run(run, author, date)
        else:
            # Partial match → split and delete middle
            _, target_run, _ = _split_run_at(run, old_text)
            delete_run(target_run, author, date)
    else:
        # Multi-run: delete all spanning runs
        for r in runs:
            delete_run(r, author, date)
    return True


def _apply_insert(p_elem, new_text: str, old_text: str, author: str, date: str) -> bool:
    """Insert *new_text* near *old_text* anchor (after it) or at end of paragraph."""
    if old_text:
        match_type, runs = _find_runs_containing(p_elem, old_text)
        if match_type != "none":
            last_run = runs[-1]
            insert_text_after_run(last_run, new_text, author, date)
            return True

    # Fallback: insert at end of paragraph
    all_runs = p_elem.findall(_qn("w:r"))
    if all_runs:
        insert_text_after_run(all_runs[-1], new_text, author, date)
        return True

    # Empty paragraph: create a run + wrap in ins
    ins = etree.SubElement(p_elem, _qn("w:ins"))
    ins.set(_qn("w:id"), _next_rev_id())
    ins.set(_qn("w:author"), author)
    ins.set(_qn("w:date"), date)
    new_run = etree.SubElement(ins, _qn("w:r"))
    t = etree.SubElement(new_run, _qn("w:t"))
    t.text = new_text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return True


def _apply_replace(p_elem, old_text: str, new_text: str, author: str, date: str) -> bool:
    """Replace *old_text* with *new_text* using tracked del + ins."""
    match_type, runs = _find_runs_containing(p_elem, old_text)
    if match_type == "none":
        return False

    if match_type == "single":
        run = runs[0]
        t_elem = run.find(_qn("w:t"))
        if t_elem is not None and _norm(t_elem.text) == _norm(old_text):
            replace_run(run, new_text, author, date)
        else:
            _, target_run, _ = _split_run_at(run, old_text)
            replace_run(target_run, new_text, author, date)
    else:
        # Multi-run: delete all, insert after the last deleted
        rpr = _copy_rpr(runs[0])
        last_del = None
        for r in runs:
            last_del = delete_run(r, author, date)

        # Insert new text after last <w:del>
        parent = last_del.getparent()
        del_idx = list(parent).index(last_del)

        ins = etree.Element(_qn("w:ins"))
        ins.set(_qn("w:id"), _next_rev_id())
        ins.set(_qn("w:author"), author)
        ins.set(_qn("w:date"), date)

        new_run = etree.SubElement(ins, _qn("w:r"))
        if rpr is not None:
            new_run.insert(0, rpr)
        t = etree.SubElement(new_run, _qn("w:t"))
        t.text = new_text
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

        parent.insert(del_idx + 1, ins)
    return True


# ── Public API ────────────────────────────────────────────────


def _find_sibling_paragraph(p_elem, old_text: str):
    """
    When *old_text* is NOT in the anchored paragraph (e.g. table cell),
    search sibling cells in the same table row for a paragraph containing it.
    Returns the matching paragraph element or None.
    """
    # Walk up to find if we're inside a table cell (<w:tc>)
    tc = p_elem.getparent()
    if tc is None or tc.tag != _qn("w:tc"):
        # Not in a table cell – check ancestors
        for anc in p_elem.iterancestors():
            if anc.tag == _qn("w:tc"):
                tc = anc
                break
        else:
            return None

    # Get the row (<w:tr>)
    tr = tc.getparent()
    if tr is None or tr.tag != _qn("w:tr"):
        return None

    old_norm = _norm(old_text)
    # Search all cells in this row
    for cell in tr.findall(_qn("w:tc")):
        for p in cell.findall(f".//{_qn('w:p')}"):
            if old_norm in _norm(_get_paragraph_text(p)):
                return p
    return None


def apply_revisions_to_doc(doc, revisions: list, author: str = "WynnSing",
                           date: str = None) -> list:
    """
    Apply a list of revision dicts to an open python-docx Document.

    Each revision dict:
      {
        "anchor": str,       # paragraph text to locate
        "action": str,       # "replace" | "delete" | "insert"
        "old_text": str,     # text to match within paragraph (for delete/replace)
        "new_text": str,     # new text (for replace/insert)
      }

    Returns a list of unmatched revision dicts.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    body = doc.element.body
    unmatched = []

    for rev in revisions:
        anchor = rev.get("anchor", "")
        action = rev.get("action", "replace")
        old_text = rev.get("old_text", "")
        new_text = rev.get("new_text", "")

        p_elem = _find_paragraph(body, anchor)
        if p_elem is None:
            # Fallback: try to find a paragraph containing old_text directly
            if old_text:
                p_elem = _find_paragraph(body, old_text)
            if p_elem is None:
                unmatched.append(rev)
                continue

        # For delete/replace: check if old_text is in this paragraph
        # If not, try sibling cells in the same table row
        if old_text and action in ("delete", "replace"):
            match_type, _ = _find_runs_containing(p_elem, old_text)
            if match_type == "none":
                sibling_p = _find_sibling_paragraph(p_elem, old_text)
                if sibling_p is not None:
                    p_elem = sibling_p

        ok = False
        if action == "delete":
            ok = _apply_delete(p_elem, old_text, author, date)
        elif action == "insert":
            ok = _apply_insert(p_elem, new_text, old_text, author, date)
        elif action == "replace":
            if old_text and new_text:
                ok = _apply_replace(p_elem, old_text, new_text, author, date)
            elif old_text and not new_text:
                ok = _apply_delete(p_elem, old_text, author, date)
            elif new_text and not old_text:
                ok = _apply_insert(p_elem, new_text, "", author, date)
        else:
            unmatched.append(rev)
            continue

        if not ok:
            unmatched.append(rev)

    return unmatched


def apply_revisions(input_path: str, output_path: str, revisions: list,
                    author: str = "WynnSing") -> list:
    """
    Load a .docx, apply revisions, save to output_path.
    Returns list of unmatched revisions.
    """
    doc = Document(input_path)
    unmatched = apply_revisions_to_doc(doc, revisions, author=author)
    doc.save(output_path)
    return unmatched


# ── CLI ───────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(
        description="Apply Word Track Changes to a .docx file"
    )
    ap.add_argument("--docx", required=True, help="Input .docx file")
    ap.add_argument("--output", required=True, help="Output .docx file")
    ap.add_argument("--revisions", required=True,
                    help="JSON file with revision list")
    ap.add_argument("--author", default="WynnSing",
                    help="Revision author name (default: WynnSing)")
    args = ap.parse_args()

    with open(args.revisions, "r", encoding="utf-8") as f:
        revisions = json.load(f)

    unmatched = apply_revisions(args.docx, args.output, revisions,
                                author=args.author)
    if unmatched:
        print(f"⚠️  {len(unmatched)} revision(s) could not be matched:")
        for r in unmatched:
            print(f"   - [{r.get('action')}] anchor: {r.get('anchor', '')[:60]}...")
    else:
        print(f"✅ All {len(revisions)} revision(s) applied successfully.")
    print(f"📄 Output: {args.output}")


if __name__ == "__main__":
    main()
