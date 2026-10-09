#!/usr/bin/env python3

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re


DEFAULT_DOCUMENT = Path(__file__).resolve().parents[1] / "drafts/cpp/invoking_annotations_r0.bs"
TOKEN = re.compile(r"(?<!\w)\w+(?:['’+.-]+\w+)*\+*(?!\w)")
FENCE_MARKER = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)[^\n]*?\1(?!`)")
BLOCK_TAGS = {
    "article", "blockquote", "br", "caption", "dd", "div", "dl", "dt", "h1", "h2", "h3",
    "h4", "h5", "h6", "hr", "li", "ol", "p", "section", "table", "td", "th", "tr", "ul",
}


class ProseParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.metadata_parts = []
        self.ignored = None
        self.in_metadata = False

    def handle_starttag(self, tag, attrs):
        if self.ignored is None and tag in {"pre", "xmp", "script", "style", "code"}:
            self.parts.append(" ")
            self.ignored = tag
            self.in_metadata = tag == "pre" and "metadata" in dict(attrs).get("class", "").split()
        elif self.ignored is None and tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag == self.ignored:
            self.ignored = None
            self.in_metadata = False
            self.parts.append(" ")
        elif self.ignored is None and tag in BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data):
        if self.in_metadata:
            self.metadata_parts.append(data)
        elif self.ignored is None:
            self.parts.append(data)

    def unknown_decl(self, declaration):
        if declaration.startswith("CDATA["):
            self.handle_data(declaration[6:])


def strip_fences(source):
    parts = []
    opening = None
    for line in source.splitlines(keepends=True):
        marker = FENCE_MARKER.match(line.rstrip("\r\n"))
        if opening is None:
            if marker and (marker[1][0] == "~" or "`" not in marker[2]):
                opening = marker[1]
                parts.append(" ")
            else:
                parts.append(line)
        elif marker and marker[1][0] == opening[0] and len(marker[1]) >= len(opening) and not marker[2].strip():
            opening = None
    return "".join(parts)


def closing_delimiter(prose, opening, left, right):
    depth = 1
    end = opening + 1
    while end < len(prose):
        if prose[end] == "\\":
            end += 2
            continue
        if prose[end] == left:
            depth += 1
        elif prose[end] == right:
            depth -= 1
            if depth == 0:
                return end
        end += 1
    return None


def strip_link_targets(prose):
    parts = []
    copied_to = 0
    search_at = 0
    while True:
        opening = prose.find("[", search_at)
        if opening < 0:
            break
        label_end = closing_delimiter(prose, opening, "[", "]")
        if label_end is None or prose[label_end + 1:label_end + 2] != "(":
            search_at = opening + 1
            continue
        target_end = closing_delimiter(prose, label_end + 1, "(", ")")
        if target_end is None:
            search_at = opening + 1
            continue
        parts.append(prose[copied_to:opening])
        parts.append(prose[opening + 1:label_end].replace("[", "").replace("]", ""))
        copied_to = target_end + 1
        search_at = copied_to
    parts.append(prose[copied_to:])
    return "".join(parts)


def visible_text(source):
    parser = ProseParser()
    parser.feed(INLINE_CODE.sub(" ", strip_fences(source)))
    parser.close()
    front_matter = " ".join(
        line.partition(":")[2].strip()
        for line in "".join(parser.metadata_parts).splitlines()
        if line.startswith(("Title:", "Abstract:"))
    )
    prose = front_matter + " " + "".join(parser.parts)
    prose = strip_link_targets(prose)
    prose = re.sub(
        r"\[\[([^\]]+)\]\]",
        lambda match: match[1].split("|", 1)[-1] if "|" in match[1] else " ",
        prose,
    )
    prose = re.sub(r"\[[a-z][a-z0-9]*(?:\.[a-z0-9]+)*\]", " ", prose)
    return re.sub(r"\{#[^}]+\}", " ", prose)


def word_count(source):
    return sum(any(character.isalpha() for character in match[0]) for match in TOKEN.finditer(visible_text(source)))


def main():
    argument_parser = argparse.ArgumentParser(description="Count prose words in a Bikeshed paper.")
    argument_parser.add_argument("document", nargs="?", type=Path, default=DEFAULT_DOCUMENT)
    args = argument_parser.parse_args()
    try:
        source = args.document.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        argument_parser.error(str(error))
    print(word_count(source))


if __name__ == "__main__":
    main()
