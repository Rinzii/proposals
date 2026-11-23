import argparse
import html
from os.path import relpath
from pathlib import Path
import shutil
from string import Template
import tempfile
from urllib.parse import quote, urlsplit

import yaml


def read_paper(root, directory):
    folder = root / directory
    rule = next(
        line.partition(":=")[2].strip()
        for line in (folder / "Makefile").read_text().splitlines()
        if line.startswith("PAPER_RULE :=")
    )
    output_stem, source_stem = rule.split(":")
    source = folder / f"{source_stem}.md"
    text = source.read_text()
    metadata = yaml.safe_load(text.split("---", 2)[1])
    abstract = text.partition("\n# Abstract")[2].partition("\n\n")[2].split("\n# ", 1)[0]
    metadata["abstract"] = " ".join(abstract.replace("`", "").split())
    document = metadata["document"]
    number, separator, revision = document.upper().partition("R")
    numbered = (
        number[:1] in {"P", "D"}
        and number[1:].isdigit()
        and separator
        and revision.isdigit()
    )
    routes = [f"P{number[1:]}", document.upper()] if numbered else [folder.name.replace("_", "-")]
    return folder, output_stem, metadata, list(dict.fromkeys(routes))


def author_names(authors):
    if isinstance(authors, (str, dict)):
        authors = [authors]
    return [author.get("name", "") if isinstance(author, dict) else author for author in authors or []]


def redirect(destination, script_path):
    escaped = html.escape(destination, quote=True)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<noscript><meta http-equiv="refresh" content="0; url={escaped}"></noscript>
<title>Paper moved</title>
<script src="{html.escape(script_path, quote=True)}" data-destination="{escaped}" defer></script>
</head>
<body><a href="{escaped}">Open the paper</a></body>
</html>
'''


def write_redirects(output, folders, aliases, target):
    for folder in folders:
        destination = output / folder
        destination.mkdir(parents=True, exist_ok=True)
        page = redirect(f"{relpath(target, folder)}/", relpath("redirect.js", folder))
        for alias in aliases:
            path = destination / f"{alias}.html"
            if not path.exists():
                path.write_text(page)


def render_site(root, output, directories):
    groups = {"progress": [], "abandoned": []}
    output.mkdir(parents=True, exist_ok=True)
    assets = root / "out/assets"
    for filename in ("index.js", "redirect.js"):
        if not (assets / filename).is_file():
            raise FileNotFoundError(f"Missing compiled frontend asset: {assets / filename}")
    for asset in assets.glob("*.js"):
        shutil.copyfile(asset, output / asset.name)
    # Published papers own the existing series and revision URLs.
    directories = sorted(map(Path, directories), key=lambda path: path.parent.name == "draft")
    draft_slugs = {(path.parents[1].name, path.name) for path in directories if path.parent.name == "draft"}
    published_slugs = {(path.parents[1].name, path.name) for path in directories if path.parent.name == "published"}
    for directory in directories:
        folder, output_stem, metadata, routes = read_paper(root, directory)
        paper_path = folder.relative_to(root / "papers")
        language, stage, slug = paper_path.parts
        if stage not in {"draft", "published"}:
            raise ValueError(f"Expected draft/ or published/ in {directory}")
        is_draft = stage == "draft"
        namespace = Path() if language == "cxx" else Path(language)
        compiled = root / "out/papers" / paper_path
        rendered = compiled / f"{output_stem}.html"
        pdf = compiled / f"{output_stem}.pdf"
        slug_route = slug.replace("_", "-")
        share_route = Path("drafts") / language / slug_route
        canonical = (share_route if is_draft else namespace / routes[0]).as_posix()
        destinations = {namespace / route for route in [*routes, slug_route]}
        if is_draft or (language, slug) not in draft_slugs:
            destinations.add(share_route)
        for route in destinations:
            destination = output / route
            if is_draft and (destination / "index.html").exists():
                continue
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(rendered, destination / "index.html")
            if pdf.exists():
                shutil.copyfile(pdf, destination / "paper.pdf")

        aliases = {output_stem, output_stem.replace("-", "_"), *routes}
        legacy_folders = [Path(), Path("drafts/cpp"), Path("cpp")] if language == "cxx" else [namespace]
        write_redirects(output, legacy_folders, aliases, canonical)

        document = metadata["document"]
        manifest = folder / "revisions.yaml"
        older = yaml.safe_load(manifest.read_text()) or [] if manifest.exists() else []
        older = [item for item in older if item["document"].upper() != document.upper()]
        older.sort(key=lambda item: int(item["document"].upper().rpartition("R")[2]), reverse=True)
        for item in older:
            published_url = urlsplit(item["url"])
            if published_url.scheme not in {"https", "http"} or not published_url.netloc:
                raise ValueError(f"Revision URL must be an HTTP or HTTPS address: {item['url']}")
            if "snapshot" in item:
                snapshot = folder / item["snapshot"]
                route = namespace / item["document"].upper()
                destination = output / route
                destination.mkdir(parents=True, exist_ok=True)
                if not (is_draft and (destination / "index.html").exists()):
                    shutil.copyfile(snapshot.with_suffix(".html"), destination / "index.html")
                    shutil.copyfile(snapshot.with_suffix(".pdf"), destination / "paper.pdf")
                item["url"] = f"{route}/"
                write_redirects(output, legacy_folders, {route.name, route.name.lower()}, route)
        if is_draft and (language, slug) in published_slugs:
            continue

        title = html.escape(metadata["title"])
        status = str(metadata.get("status", "unspecified"))
        audience = metadata.get("audience", [])
        if isinstance(audience, str):
            audience = [audience]
        revision = document.rpartition("R")[2]
        revision = f"R{revision}" if revision.isdigit() else "Not specified"
        identifier = document if len(routes) > 1 else f"Draft {revision}"
        document_markup = f'<span class="document">{html.escape(identifier)}</span>'
        tracking_issue = metadata.get("tracking-issue")
        if tracking_issue is not None:
            document_markup = f'<a class="document" href="https://github.com/cplusplus/papers/issues/{int(tracking_issue)}" aria-label="WG21 tracking issue: {html.escape(identifier)}">{html.escape(identifier)}</a>'
        date = metadata.get("date")
        date_text = date.isoformat() if hasattr(date, "isoformat") else str(date or "Not specified")
        revisions = [{"document": document, "date": date, "url": f"{canonical if is_draft else namespace / routes[-1]}/", "author": metadata.get("author"), "original-author": metadata.get("original-author"), "status": status}, *older]
        items = []
        authors = []
        for item in revisions:
            revision_number = item["document"].upper().rpartition("R")[2]
            revision_date = item["date"]
            revision_date = revision_date.isoformat() if hasattr(revision_date, "isoformat") else str(revision_date or "Not specified")
            revision_authors = author_names(item.get("author"))
            original_authors = author_names(item.get("original-author"))
            authors.extend([*revision_authors, *original_authors])
            revision_status = str(item.get("status", "published"))
            state = "Draft" if revision_status == "progress" else revision_status.replace("_", " ").capitalize()
            label = html.escape(f'{item["document"]} {metadata["title"]}')
            items.append(f'<li data-status="{html.escape(revision_status)}"><time datetime="{html.escape(revision_date)}">{html.escape(revision_date)}</time><span class="revision-marker" aria-hidden="true"></span><div class="revision-description"><a href="{html.escape(item["url"])}" aria-label="{label}">R{html.escape(revision_number)}</a><span class="revision-state">{html.escape(state)}</span><span class="revision-authors">{html.escape(", ".join(revision_authors))}</span></div></li>')
        searchable = " ".join([metadata["title"], document, canonical, folder.name, metadata["abstract"], *audience, *(item["document"] for item in older), *authors]).casefold()
        entry = f'''<details class="paper" data-status="{html.escape(status)}" data-search="{html.escape(searchable)}">
  <summary class="paper-summary">
    {document_markup}
    <span class="paper-body">
      <span class="paper-heading"><span class="paper-title">{title}</span><a class="paper-latest" href="{html.escape(canonical)}/" aria-label="Latest version of {title}">Latest <span aria-hidden="true">&rarr;</span></a></span>
      <span class="paper-meta">{html.escape(date_text)} · {html.escape(", ".join(audience)) or "Not specified"}</span>
    </span>
    <span class="expand-icon" aria-hidden="true">+</span>
  </summary>
  <ol class="revisions">{"".join(items)}</ol>
</details>'''
        groups.setdefault(status, []).append(entry)

    total = sum(map(len, groups.values()))
    filters = [f'<button type="button" data-filter="all" aria-pressed="true">All <span aria-hidden="true">{total}</span></button>']
    sections = []
    for status, entries in groups.items():
        if not entries:
            continue
        label = "In progress" if status == "progress" else status.replace("_", " ").capitalize()
        filters.append(f'<button type="button" data-filter="{html.escape(status)}" aria-pressed="false">{html.escape(label)} <span aria-hidden="true">{len(entries)}</span></button>')
        group_id = quote(status, safe="")
        sections.append(f'''<section class="paper-group" aria-labelledby="heading-{group_id}">
  <div class="group-heading"><h2 id="heading-{group_id}">{html.escape(label)}</h2></div>
  {"".join(entries)}
</section>''')
    template = Template((root / "md/index.html").read_text())
    count_label = f"{total} {'paper' if total == 1 else 'papers'}"
    (output / "index.html").write_text(template.substitute(papers="\n".join(sections), filters="\n".join(filters), count_label=count_label))
    (output / ".nojekyll").touch()


def build_site(root, output, directories):
    if output.is_symlink():
        raise ValueError(f"Output directory is a symlink: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-", dir=output.parent) as temporary:
        staged = Path(temporary)
        render_site(root, staged, directories)
        generated = {path.relative_to(staged): path for path in staged.rglob("*") if path.is_file()}
        for relative in generated:
            if ".git" in relative.parts:
                raise ValueError(f"Cannot publish into .git: {relative}")
            destination = output
            for part in relative.parts[:-1]:
                destination /= part
                if destination.is_symlink():
                    raise ValueError(f"Output directory is a symlink: {destination}")
        stale = []
        folders = []
        for path in output.rglob("*"):
            relative = path.relative_to(output)
            if ".git" in relative.parts:
                continue
            if path.is_symlink() or path.is_file():
                if relative not in generated and not (staged / relative).is_file():
                    stale.append(path)
            elif path.is_dir():
                folders.append(path)
        for path in sorted(stale):
            print(f"Removing stale file: {path}")
        for path in stale:
            path.unlink()
        output.mkdir(parents=True, exist_ok=True)
        for relative, source in generated.items():
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
        for folder in sorted(folders, key=lambda path: len(path.parts), reverse=True):
            if not any(folder.iterdir()):
                print(f"Removing empty directory: {folder}")
                folder.rmdir()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("out/site"))
    parser.add_argument("directories", nargs="+")
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    build_site(root, root / arguments.output, arguments.directories)


if __name__ == "__main__":
    main()
