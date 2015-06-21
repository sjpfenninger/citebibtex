# CiteBibtex

[![Join the chat at https://gitter.im/sjpfenninger/citebibtex](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sjpfenninger/citebibtex?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

A Sublime Text plugin to effortlessly insert citations from BibTeX into texts written in Pandoc or LaTeX.

## Installation

Install via [Package Control](https://sublime.wbond.net/packages/CiteBibtex).

Compatible with Sublime Text 3 only.

## Initial configuration

Set the path to your global BibTeX file (`bibtex_file`) in the plugin settings.

## Use

Pressing the citation shortcut key (bound to `F10` by default) brings up a quick panel for  searching the bibliography file. Once the desired reference is found, pressing enter or clicking on it will insert a citation at the current cursor position (if there is more than one cursor, at the first cursor's position). The BibTeX file is checked for modifications each time the quick panel is brought up.

The format for inserted citations is auto-detected as `pandoc` (for use with [Pandoc](http://johnmacfarlane.net/pandoc/README.html)) or `latex` based on the syntax of the open file (this can be disabled by setting `"autodetect_citation_style": false` in the plugin settings). If auto-detection fails, the default is to use `pandoc` (which can be changed by setting `default_citation_style` in the plugin settings).

The `bibtex_file` setting can be overridden on a per-project basis in the project settings, using either a path relative to the project settings file or an absolute path. The following example project settings demonstrate this:

```json
{
    "folders":
    [
        {
            "follow_symlinks": true,
            "path": ".",
        }
    ],
    "bibtex_file": "path/to/bibtex.bib"
}
```

## Extraction of citations from master BibTeX file

The command `CiteBibTeX: Extract citations in current file` is available via the command palette, and will extract all references used in the currently open file from the global BibTeX file, saving that subset in a local BibTeX file.

For example, if `my_paper.md` is currently open and cites 10 out of 100 references in the global BibTeX file, calling this command will save those 10 references in a file called `my_paper.bib` in the same directory as `my_paper.md`. This may useful to keep references portable alongside the text that uses them for sharing or archiving.

## Acknowledgments

Includes the BibTeX parsing library [python-bibtexparser](https://github.com/sciunto-org/python-bibtexparser) (LGPLv3-licensed).

Includes `md2bib.py` from [pandoc-wrappers](https://github.com/reagle/pandoc-wrappers) by Joseph Reagle (GPLv3-licensed).

## License

GNU GPLv3 (see `LICENSE` file).
