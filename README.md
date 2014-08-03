# CiteBibtex

A Sublime Text plugin to effortlessly insert citations from BibTeX into texts written in Pandoc or LaTeX.

## Installation

Install via [Package Control](https://sublime.wbond.net/).

Tested on Sublime Text 3 only.

## Initial configuration

Set the path to your global BibTeX file (`bibtex_file`) in the plugin settings.

## Use

Pressing the citation shortcut key (bound to `F10` by default) brings up a quick panel for  searching the bibliography file. Once the desired reference is found, pressing enter or clicking on it will insert a citation at the current cursor position (if there is more than one cursor, at the first cursor's position). The BibTeX file is checked for modifications each time the quick panel is brought up.

The format for inserted citations can be set to either `pandoc` or `latex` in the plugin settings. `pandoc` is the default, for use with [Pandoc](http://johnmacfarlane.net/pandoc/README.html).

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

## Acknowledgments

Includes `Bibparser` from [bibpy](https://github.com/ptigas/bibpy) by Panagiotis Tigkas (MIT-licensed).

## License

The MIT License (MIT)

Copyright (c) 2014 Stefan Pfenninger

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
