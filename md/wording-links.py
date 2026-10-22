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


if __name__ == "__main__":
    pf.run_filter(unlink)
