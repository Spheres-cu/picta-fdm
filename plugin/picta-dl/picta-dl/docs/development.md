# Picta-DL Development
Development Notes for [`picta-dl`](https://github.com/oleksis/picta-dl)

## Files
Files from `youtube-dl` to `yt-dlp`
```txt
▼ picta_dl
├── __init__.py
├── __main__.py  # Set environment variable LD_LIBRARY_PATH for GNU/Linux and *BSD. (2392c0c)
├── compat.py  # [core] /compat dir
├── ▼ docs
│   └── ▼ ytdlp_plugins
│       └── ▼ extractor
│           └── picta.py  # (65828aa) Add ytdlp_plugins extractor for yt-dlp
├── ▼ .github
│   └── ▼ workflows
│       └── release.yml
├── ▼ downloader
│   ├── hls.py
│   ├── http.py
│   └── fragment.py
├── ▼ extractor
│   ├── common.py
│   ├── extractors.py
│   ├── picta.py  # [picta] Redefine _parse_mpd_formats
│   └── youtube.py
├── ▼ postprocesor
│   └── embedthumbnail.py  # (d0b193a)
├── options.py
├── utils.py
├── version.py
├── YoutubeDL.py  # Remplace `yt_dlp` / `yt-dlp` name for `picta_dl` / `picta-dl`
├── ▼ test
│   └── test_local_picta.sh  # (3f9eb6a)
├── ChangeLog
├── README.md
└── appimage-builder.yml  # (c50e524)
```

## Test
Local Test
```bash
USER=user PASSWORD=password ./test/test_local_picta.sh
```

## Install from GitHub
```bash
pip install -e git+https://github.com/oleksis/picta-dl.git#egg=picta-dl
```

## Textual Tree

```python
# t.py
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import  Tree



class TreeApp(App):
    BINDINGS = [
        ("ctrl+s", "app.screenshot()", "Screenshot"),
        Binding("ctrl+c,ctrl+q", "app.quit", "Quit", show=True),
    ]

    def on_mount(self):
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        tree: Tree = Tree("picta_dl")
        tree.root.expand()
        tree.root.add_leaf("__init__.py")
        tree.root.add_leaf("__main__.py")
        tree.root.add_leaf("compat.py")
        docs = tree.root.add("docs", expand=True)
        docs.add("ytdlp_plugins", expand=True).add("extractor", expand=True).add_leaf("picta.py")
        github = tree.root.add(".github", expand=True)
        github.add("workflows", expand=True).add_leaf("release.yml")
        downloader = tree.root.add("downloader", expand=True)
        downloader.add_leaf("hls.py")
        downloader.add_leaf("http.py")
        downloader.add_leaf("fragment.py")
        extractor = tree.root.add("extractor", expand=True)
        extractor.add_leaf("common.py")
        extractor.add_leaf("extractors.py")
        extractor.add_leaf("picta.py")
        extractor.add_leaf("youtube.py")
        postprocesor = tree.root.add("postprocesor", expand=True)
        postprocesor.add_leaf("embedthumbnail.py")
        tree.root.add_leaf("options.py")
        tree.root.add_leaf("utils.py")
        tree.root.add_leaf("version.py")
        tree.root.add_leaf("YoutubeDL.py")
        test = tree.root.add("test", expand=True)
        test.add_leaf("test_local_picta.sh")
        tree.root.add_leaf("ChangeLog")
        tree.root.add_leaf("README.md")
        tree.root.add_leaf("appimage-builder.yml")
        yield tree

    def action_screenshot(self,):
        self.save_screenshot("./build/picta-src.svg")



if __name__ == "__main__":
    app = TreeApp()
    app.run()
```
