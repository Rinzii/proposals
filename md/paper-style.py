#!/usr/bin/env python3

import base64
from pathlib import Path
import subprocess
from urllib.parse import quote

import panflute as pf


# Stroke paths on a 24 by 24 grid, shared by the HTML and PDF renderers.
CALLOUT_ICONS = {
    "info": "M22 12 C22 6.5 17.5 2 12 2 S2 6.5 2 12 S6.5 22 12 22 S22 17.5 22 12 Z M12 11 V17 M12 7 V7.1",
    "decision": "M4 20 H14 M3 9 L6 6 L12 12 L9 15 Z M9 3 L12 0 L18 6 L15 9 Z M8 8 L11 5 M11 9 L22 20",
    "bug": "M7 10 C7 6 17 6 17 10 V15 C17 23 7 23 7 15 Z M9 7 C9 3 15 3 15 7 M8 3 L10 5 M16 3 L14 5 M3 9 L7 11 M2 14 H7 M3 19 L7 17 M21 9 L17 11 M22 14 H17 M21 19 L17 17 M12 11 V16",
    "insert": "M5 2 H14 L20 8 V22 H5 Z M14 2 V8 H20 M9 15 H16 M12.5 11.5 V18.5",
    "remove": "M5 2 H14 L20 8 V22 H5 Z M14 2 V8 H20 M9 15 H16",
    "recorded": "M3 12 H7 M17 12 H21 L22 21 H2 L3 12 M7 14 H17 M8 9 L13 3 L19 8 L14 14 Z",
    "proposed": "M4 20 L5 15 L17 3 L21 7 L9 19 Z M15 5 L19 9 M4 22 H21",
    "wording": "M2 6 V22 H15 M6 2 H15 L21 8 V18 H6 Z M15 2 V8 H21 M9 9 H13 M11 7 V11 M9 14 H15",
    "quote": "M3 6 H9 V13 L6 18 H4 L7 12 H3 Z M14 6 H20 V13 L17 18 H15 L18 12 H14 Z",
}


def include(doc, text, format):
    block = pf.MetaBlocks(pf.RawBlock(text, format=format))
    previous = doc.metadata.content.get("header-includes")
    if previous is None:
        doc.metadata["header-includes"] = pf.MetaList(block)
    elif isinstance(previous, pf.MetaList):
        previous.append(block)
    else:
        doc.metadata["header-includes"] = pf.MetaList(previous, block)


def prepare(doc):
    theme = doc.get_metadata("paper-style")
    colors = theme["colors"]
    dimensions = {name: float(value) for name, value in theme.items() if name not in ("colors", "heading-scales", "body-font", "code-font")}
    headings = [float(value) for value in theme["heading-scales"]]
    if doc.format in ("html", "revealjs"):
        declarations = [
            f"  --paper-{name}: light-dark(#{values[0]}, #{values[1]});"
            for name, values in colors.items()
        ]
        for name, path in CALLOUT_ICONS.items():
            svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 26 26">'
                   f'<path d="{path}" fill="none" stroke="black" stroke-width="2" '
                   f'stroke-linecap="round" stroke-linejoin="round"/></svg>')
            declarations.append(f"  --paper-icon-{name}: url('data:image/svg+xml,{quote(svg)}');")
        for name, value in dimensions.items():
            unit = "pt" if name == "body-size" else ""
            declarations.append(f"  --paper-{name}: {value:g}{unit};")
        declarations.extend(f"  --paper-heading-{level}: {scale:g};" for level, scale in enumerate(headings, 1))
        fonts = []
        for key in ("body-font", "code-font"):
            family = theme[key]
            declarations.append(f'  --paper-{key}: "{family}";')
            stem = family.lower().replace(" ", "")
            for variant, weight, style in (("regular", 400, "normal"), ("italic", 400, "italic"), ("bold", 700, "normal"), ("bolditalic", 700, "italic")):
                filename = subprocess.run(["kpsewhich", f"{stem}-{variant}.otf"], check=True, capture_output=True, text=True).stdout.strip()
                encoded = base64.b64encode(Path(filename).read_bytes()).decode("ascii")
                fonts.append(f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: {style}; src: url(data:font/otf;base64,{encoded}) format("opentype"); }}')
        include(doc, "<style>\n" + "\n".join(fonts) + "\n:root {\n" + "\n".join(declarations) + "\n}\n</style>", "html")
    elif doc.format == "latex":
        for metadata, color in (("addcolor", "add"), ("rmcolor", "rm"), ("uccolor", "text"), ("notecolor", "note")):
            doc.metadata[metadata] = pf.MetaString(colors[color][0])
        doc.metadata["toccolor"] = pf.MetaString("paper-link")
        doc.metadata["fontsize"] = pf.MetaString(f'{dimensions["body-size"]:g}pt')
        for key, metadata in (("body-font", "mainfont"), ("code-font", "monofont")):
            stem = theme[key].lower().replace(" ", "")
            doc.metadata[metadata] = pf.MetaString(f"{stem}-regular.otf")
            doc.metadata[metadata + "options"] = pf.MetaList(*(pf.MetaString(f"{option}={stem}-{variant}.otf") for option, variant in (("BoldFont", "bold"), ("ItalicFont", "italic"), ("BoldItalicFont", "bolditalic"))))
        definitions = [
            rf"\definecolor{{paper-{name}}}{{HTML}}{{{values[0]}}}"
            for name, values in colors.items()
        ]
        for name, path in CALLOUT_ICONS.items():
            definitions.append(rf"\newcommand{{\PaperIcon{name}}}{{\pgfpathsvg{{{path}}}}}")
        for name, value in dimensions.items():
            command = "Paper" + "".join(part.title() for part in name.split("-"))
            definitions.append(rf"\newcommand{{\{command}}}{{{value:g}}}")
        definitions.extend(rf"\newcommand{{\PaperHeading{level}}}{{{scale:g}}}" for level, scale in zip(("One", "Two", "Three", "Four", "Five", "Six"), headings))
        include(doc, "\n".join(definitions) + "\n" + Path(__file__).with_name("papers.tex").read_text(), "latex")


def ancestors(elem):
    parent = elem.parent
    while parent is not None:
        yield parent
        parent = parent.parent


def has_class(elem, name):
    return name in getattr(elem, "classes", ())


def decorate_change(elem, command):
    content = []
    run = []

    def flush():
        if run:
            content.append(pf.Span(pf.RawInline(command, format="latex"), *run, pf.RawInline("}", format="latex")))
            run.clear()

    children = list(elem.content)

    def spaced(index):
        return 0 <= index < len(children) and isinstance(children[index], (pf.Space, pf.SoftBreak))

    for index, child in enumerate(children):
        if isinstance(child, (pf.Emph, pf.Strong, pf.SmallCaps, pf.Quoted)) or isinstance(child, pf.Link) and not child.classes:
            flush()
            decorate_change(child, command)
            content.append(child)
        elif isinstance(child, pf.Code):
            if spaced(index - 1) and run:
                run.pop()
                flush()
                content.append(pf.RawInline(r"\PaperCodeBreak ", format="latex"))
                run.append(pf.RawInline(r"\ ", format="latex"))
            flush()
            run.extend((pf.RawInline(r"\mbox{", format="latex"), child, pf.RawInline("}", format="latex")))
            flush()
            if spaced(index + 1):
                content.append(pf.RawInline(r"\allowbreak ", format="latex"))
        else:
            run.append(child)
    flush()
    elem.content = content


def style_poll(elem, doc, recorded):
    kind = "recorded" if recorded else "proposed"
    title = elem.attributes.pop("label", "Recorded poll" if recorded else "Proposed poll")
    source = elem.attributes.pop("source", None)
    result = elem.attributes.pop("result", None) if recorded else None
    if doc.format == "html":
        elem.classes.append("paper-callout")
        elem.attributes.update({"role": "group", "aria-label": title})
        label = pf.Span(pf.Str(title), classes=["callout-label"])
    else:
        label = pf.Span(pf.RawInline(r"\PaperCalloutLabel{", format="latex"), pf.Str(title),
                        pf.RawInline("}", format="latex"))
    heading = pf.Para(pf.Link(label, url=source) if source else label)
    if result:
        heading.content.append(pf.Space() if doc.format == "html" else pf.RawInline(r"\hfill\quad ", format="latex"))
        heading.content.append(pf.Span(pf.Str("Result:"), pf.Space(), pf.Strong(pf.Str(result)), classes=["poll-result"]))
    elem.content.insert(0, heading)
    if doc.format == "latex":
        elem.content.insert(0, pf.RawBlock(rf"\begin{{PaperCallout}}{{{kind}}}", format="latex"))
        elem.content.append(pf.RawBlock(r"\end{PaperCallout}", format="latex"))


def style(elem, doc):
    if isinstance(elem, pf.Div) and doc.format in ("html", "latex"):
        if "recorded-poll" in elem.classes or "proposed-poll" in elem.classes:
            style_poll(elem, doc, "recorded-poll" in elem.classes)
            return
        if "rm" in elem.classes:
            if any(isinstance(parent, pf.Div) and has_class(parent, "rm") for parent in ancestors(elem)):
                return
            if doc.format == "html":
                elem.classes.append("paper-removal")
    if isinstance(elem, pf.Table) and any(has_class(parent, "code-comparison") for parent in ancestors(elem)):
        columns = len(elem.colspec)
        if columns > 1:
            first = max(0.2, elem.colspec[0][1])
            elem.colspec = [(alignment, first if index == 0 else (1 - first) / (columns - 1)) for index, (alignment, _) in enumerate(elem.colspec)]
            if any(getattr(parent, "identifier", "") == "pack-matrix" for parent in ancestors(elem)):
                elem.colspec = [("AlignCenter" if index == 0 else alignment, width) for index, (alignment, width) in enumerate(elem.colspec)]
                if doc.format == "latex":
                    measured = []
                    for row_index, row in enumerate(elem.content[0].content):
                        names = []
                        for column, cell in enumerate(row.content):
                            name = f"PackMatrix{row_index}Cell{column}"
                            names.append(name)
                            width = elem.colspec[column][1]
                            blocks = list(cell.content)
                            color = ""
                            if blocks and isinstance(blocks[0], pf.RawBlock) and blocks[0].text.startswith(r"\cellcolor{"):
                                color, _, shade = blocks.pop(0).text.partition(r"\colorlet")
                                if shade:
                                    blocks.insert(0, pf.RawBlock(r"\colorlet" + shade, format="latex"))
                            if column == 0:
                                blocks.insert(0, pf.RawBlock(r"\centering", format="latex"))
                            measured.extend((pf.RawBlock(rf"\begin{{PaperMeasureCell}}{{{name}}}{{{width:g}}}{{{columns - 1}}}", format="latex"), *blocks, pf.RawBlock(r"\end{PaperMeasureCell}", format="latex")))
                            cell.content = [pf.Plain(pf.RawInline(color + rf"\usebox{{\csname PaperCell{name}\endcsname}}", format="latex"))]
                        label = row.content[0].content[0].content[0]
                        label.text = label.text.partition(r"\usebox")[0] + rf"\PaperCenteredCell{{{names[0]}}}{{{names[1]}}}{{{names[2]}}}"
                    return [*measured, elem]
    if isinstance(elem, pf.Code) and "nobreak" in elem.classes:
        elem.classes.remove("nobreak")
        if doc.format == "latex":
            lead = r"\PaperCodeBreak\mbox{" if isinstance(elem.prev, (pf.Space, pf.SoftBreak)) else r"\mbox{"
            return pf.Span(pf.RawInline(lead, format="latex"), elem, pf.RawInline("}", format="latex"))
        return
    if doc.format != "latex":
        return
    if isinstance(elem, pf.Span):
        if "grammar-term" in elem.classes:
            return pf.Emph(pf.RawInline(r"\color{paper-grammar}", format="latex"), *elem.content)
        change = next((name for name in ("add", "rm") if name in elem.classes), None)
        if change:
            wording = any(has_class(parent, "wording") for parent in ancestors(elem))
            color = ("wording-add-bg" if change == "add" else "wording-remove-bg") if wording else ("valid-bg" if change == "add" else "invalid-bg")
            if change == "rm":
                decorate_change(elem, r"\PaperStrikeHighlight{")
                return pf.Span(
                    pf.RawInline(rf"{{\def\PaperRemovalColor{{paper-{color}}}\let\sout\PaperUnmarked ", format="latex"),
                    elem,
                    pf.RawInline("}", format="latex"),
                )
            decorate_change(elem, rf"\PaperHighlight{{paper-{color}}}{{")
    elif isinstance(elem, pf.Code) and any(isinstance(parent, pf.Link) for parent in ancestors(elem)):
        return pf.Span(pf.RawInline(r"\mbox{", format="latex"), elem, pf.RawInline("}", format="latex"))
    elif isinstance(elem, pf.CodeBlock):
        if any(has_class(parent, "cmptable") or has_class(parent, "tonytable") for parent in ancestors(elem)):
            return
        if "diff" in elem.classes:
            lines = [r"\begin{PaperDiff}"]
            start = int(elem.attributes.get("startFrom", "1")) if "numberLines" in elem.classes else 1
            for number, line in enumerate(elem.text.splitlines(), start):
                if line.startswith(("+", "-")):
                    color = "wording-add-bg" if line.startswith("+") else "wording-remove-bg"
                    lines.append(rf"\PaperDiffLine{{{number}}}{{paper-{color}}}")
            return pf.Div(
                pf.RawBlock("\n".join(lines), format="latex"),
                elem,
                pf.RawBlock(r"\end{PaperDiff}", format="latex"),
            )
    elif isinstance(elem, pf.TableCell):
        validity = []
        elem.walk(lambda child, _: validity.extend(name for name in ("code-valid", "code-invalid") if has_class(child, name)))
        color = None
        if validity:
            color = "valid-bg" if validity[0] == "code-valid" else "invalid-bg"
        elif isinstance(elem.parent.parent, pf.TableHead):
            color = "table-head"
        elif isinstance(elem.parent.parent, pf.TableBody):
            rows = list(elem.parent.parent.content)
            if rows.index(elem.parent) % 2:
                color = "table-stripe"
        if color:
            shade = rf"\colorlet{{shadecolor}}{{paper-{color}}}" if validity else ""
            elem.content.insert(0, pf.RawBlock(rf"\cellcolor{{paper-{color}}}" + shade, format="latex"))
    elif isinstance(elem, pf.Div) and "wording" not in elem.classes:
        if any(name in elem.classes for name in ("add", "rm", "code-comparison", "cmptable", "tonytable")):
            environment = "PaperAddition" if "add" in elem.classes else "PaperRemoval" if "rm" in elem.classes else "PaperComparison"
            wrapper = pf.Div(pf.RawBlock(rf"\begin{{{environment}}}", format="latex"), elem, pf.RawBlock(rf"\end{{{environment}}}", format="latex"))
            if "add" in elem.classes or "rm" in elem.classes:
                wrapper.classes.append("paper-addition" if "add" in elem.classes else "paper-removal")
            return wrapper


if __name__ == "__main__":
    pf.run_filter(style, prepare=prepare)
