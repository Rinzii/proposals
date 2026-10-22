import argparse
from pathlib import Path
import subprocess
import sys

from livereload import Server
from livereload.handlers import StaticFileHandler
from livereload.watcher import Watcher


class PreviewFileHandler(StaticFileHandler):
    @classmethod
    def get_content(cls, abspath, start=None, end=None):
        chunks = super().get_content(abspath, start, end)
        if Path(abspath).suffix.lower() not in {".html", ".htm", ".xhtml"}:
            yield from chunks
            return
        head = []
        overlap = b""
        for chunk in chunks:
            head.append(chunk)
            if b"</head>" in overlap + chunk:
                yield b"".join(head)
                yield from chunks
                return
            overlap = chunk[-6:]
        yield b"".join(head)


class SiteWatcher(Watcher):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.initialized = False

    def is_file_changed(self, path, ignore=None):
        known = path in self._task_mtimes
        changed = super().is_file_changed(path, ignore)
        return changed or (self.initialized and not known and path in self._new_mtimes)

    def examine(self):
        change = super().examine()
        if self.initialized and change[0] and change[0] != "__livereload__":
            print("Rebuilding site...", flush=True)
            build = subprocess.run(["make", "site"], cwd=self.root)
            if build.returncode:
                print(f"Site build failed (exit {build.returncode}). Keeping the previous preview.", file=sys.stderr, flush=True)
                self.filepath = None
                change = (None, None)
            else:
                self.filepath = "*"
                change = ("__livereload__", None)
        self.initialized = True
        return change


def create_server(root):
    server = Server(watcher=SiteWatcher(root))
    server.SFH = PreviewFileHandler
    for pattern in (
        "papers/*/*.md",
        "papers/*/Makefile",
        "papers/*/revisions.yaml",
        "md/index.html",
        "md/*.css",
        "md/defaults.yaml",
        "md/paper-style.yaml",
        "md/paper-style.py",
        "md/papers.tex",
        "md/*.ts",
        "md/mpark-wg21.mk",
        "scripts/site.py",
        "scripts/setup.sh",
        "Makefile",
        "package.json",
        "package-lock.json",
        "tsconfig.json",
    ):
        server.watch(str(root / pattern))
    server.watcher.examine()
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8123)
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    create_server(root).serve(host="127.0.0.1", port=arguments.port, root=str(root / "out/site"), live_css=False)


if __name__ == "__main__":
    main()
