#!/usr/bin/env python3

import panflute as pf


def ancestors(elem):
    parent = elem.parent
    while parent is not None:
        yield parent
        parent = parent.parent


def has_class(elem, name):
    return name in getattr(elem, "classes", ())


def is_pnum(elem):
    found = []

    def visit(child, _):
        if any(has_class(child, name) for name in ("pnum", "marginalized", "marginalizedparent")):
            found.append(child)
        elif isinstance(child, pf.RawInline) and child.format == "latex" and child.text.startswith(r"\pnum{"):
            found.append(child)

    elem.walk(visit)
    return bool(found)


def unlink(elem, doc):
    if not isinstance(elem, pf.Link):
        return None
    if not any(has_class(parent, "wording") for parent in ancestors(elem)):
        return None
    if is_pnum(elem):
        return None
    if has_class(elem, "sref"):
        return pf.Str(f"[{pf.stringify(elem)}]")
    return list(elem.content)


def wrap_latex(elem, environment):
    elem.content.insert(0, pf.RawBlock(rf"\begin{{{environment}}}", format="latex"))
    elem.content.append(pf.RawBlock(rf"\end{{{environment}}}", format="latex"))


def frame_wording(elem, doc):
    if not isinstance(elem, pf.Div) or doc.format not in ("html", "latex"):
        return
    wording = has_class(elem, "wording")
    change_classes = ("add", "paper-removal") if doc.format == "html" else ("paper-addition", "paper-removal")
    if not wording:
        if not any(has_class(elem, name) for name in change_classes):
            return
        if not any(has_class(parent, "wording") for parent in ancestors(elem)):
            return
    # mpark has now assigned paragraph numbers, including those generated from lists.
    numbered = is_pnum(elem)
    whole_change = (wording and len(elem.content) == 1 and isinstance(elem.content[0], pf.Div)
                    and any(has_class(elem.content[0], name) for name in change_classes))
    if doc.format == "html":
        if whole_change:
            elem.classes.append("wording-change")
        if numbered:
            elem.classes.append("wording-numbered")
    else:
        if wording and not whole_change:
            wrap_latex(elem, "PaperWording")
        if numbered and not whole_change:
            wrap_latex(elem, "PaperNumberedGutter")


if __name__ == "__main__":
    pf.run_filters([unlink, frame_wording])
