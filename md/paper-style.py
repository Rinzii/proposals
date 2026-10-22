#!/usr/bin/env python3

import base64
from pathlib import Path
import subprocess

import panflute as pf


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


def surround(elem, environment):
    elem.content.insert(0, pf.RawBlock(rf"\begin{{{environment}}}", format="latex"))
    elem.content.append(pf.RawBlock(rf"\end{{{environment}}}", format="latex"))


def decorate_change(elem, color, removed):
    content = []
    run = []

    def flush():
        if run:
            command = rf"\PaperStrikeHighlight{{" if removed else rf"\PaperHighlight{{paper-{color}}}{{"
            content.append(pf.Span(pf.RawInline(command, format="latex"), *run, pf.RawInline("}", format="latex")))
            run.clear()

    for child in list(elem.content):
        if isinstance(child, (pf.Emph, pf.Strong, pf.SmallCaps, pf.Quoted)) or isinstance(child, pf.Link) and not child.classes:
            flush()
            decorate_change(child, color, removed)
            content.append(child)
        elif isinstance(child, pf.Code):
            flush()
            content.append(pf.RawInline(r"\allowbreak ", format="latex"))
            run.extend((pf.RawInline(r"\mbox{", format="latex"), child, pf.RawInline("}", format="latex")))
            flush()
            content.append(pf.RawInline(r"\allowbreak ", format="latex"))
        else:
            run.append(child)
    flush()
    elem.content = content


def style(elem, doc):
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
    if doc.format != "latex":
        return
    if isinstance(elem, pf.Span):
        if "grammar-term" in elem.classes:
            return pf.Emph(pf.RawInline(r"\color{paper-grammar}", format="latex"), *elem.content)
        change = next((name for name in ("add", "rm") if name in elem.classes), None)
        if change:
            wording = any(has_class(parent, "wording") for parent in ancestors(elem))
            color = ("wording-add-bg" if change == "add" else "wording-remove-bg") if wording else ("valid-bg" if change == "add" else "invalid-bg")
            decorate_change(elem, color, change == "rm")
            if change == "rm":
                return pf.Span(
                    pf.RawInline(rf"{{\def\PaperRemovalColor{{paper-{color}}}\let\sout\PaperUnmarked ", format="latex"),
                    elem,
                    pf.RawInline("}", format="latex"),
                )
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
    elif isinstance(elem, pf.Div):
        if "wording" in elem.classes:
            surround(elem, "PaperWording")
        elif any(name in elem.classes for name in ("add", "rm", "code-comparison", "cmptable", "tonytable")):
            environment = "PaperAddition" if "add" in elem.classes else "PaperRemoval" if "rm" in elem.classes else "PaperComparison"
            return pf.Div(pf.RawBlock(rf"\begin{{{environment}}}", format="latex"), elem, pf.RawBlock(rf"\end{{{environment}}}", format="latex"))


if __name__ == "__main__":
    pf.run_filter(style, prepare=prepare)
