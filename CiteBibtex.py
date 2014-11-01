import sublime
import sublime_plugin

import os

from .lib.bib import Bibparser
from .lib import md2bib


def get_item(i):
    try:
        year = i['issued']['literal']
    except KeyError:
        year = '<no date>'
    try:
        authors = i['author']
        authors = ', '.join(a['family'] for a in authors)
    except KeyError:
        authors = '<no authors>'
    try:
        title = i['title']
    except KeyError:
        title = ''
    # Publication is a bit more complex
    if 'journal' in i:
        publication = i['journal']
        if 'volume' in i:
            publication = publication + ' (' + i['volume'] + ')'
        if 'number' in i:
            publication = publication + ' ' + i['number']
    else:
        try:
            publication = i['booktitle']
        except KeyError:
            publication = i['type'].capitalize()
    return [i['id'], year + ' | ' + authors, title, publication]


class CiteBibtex(object):
    def plugin_loaded_setup(self):
        ##
        # Load settings
        ##
        plugin_settings_file = self.__class__.__name__ + '.sublime-settings'
        self.plugin_settings = sublime.load_settings(plugin_settings_file)
        ##
        # Initialize and load global references
        ##
        global_file = self.plugin_settings.get('bibtex_file')
        self.last_modified = {}
        self.refs = {}
        _ = self.check_modified(global_file)
        self.update_refs(global_file)

    def get_setting(self, setting, return_source=False):
        project_data = sublime.active_window().project_data()
        # Check whether there is a project-specific override
        if project_data and setting in project_data:
            result = project_data[setting]
            source = 'project'
        else:
            result = self.plugin_settings.get(setting)
            source = 'global'
        if return_source:
            return (result, source)
        else:
            return result

    def get_citation_style(self):
        autodetect_syntaxes = self.plugin_settings.get('autodetect_syntaxes')
        view = sublime.active_window().active_view()
        current_syntax = view.settings().get('syntax')
        current_syntax = os.path.splitext(os.path.basename(current_syntax))[0]
        if (self.get_setting('autodetect_citation_style') and
                current_syntax in autodetect_syntaxes):
            style = autodetect_syntaxes[current_syntax]
        else:
            style = self.get_setting('default_citation_style')

        strings = self.plugin_settings.get('styles')

        try:
            citation_string = strings[style]
        except KeyError:
            error_message = 'Unknown citation style: {}'.format(style)
            sublime.status_message(error_message)
            raise KeyError(error_message)
        return citation_string

    def check_modified(self, ref_file):
        try:
            modified = os.path.getmtime(ref_file)
        except FileNotFoundError:
            error_message = 'ERROR: Can\'t open BibTeX file '
            sublime.status_message(error_message + ref_file)
            raise FileNotFoundError(error_message)
        if ref_file not in self.last_modified:  # Initialize if needed
            self.last_modified[ref_file] = modified
            return True  # Upate needed if this file was never seen before
        else:
            if modified > self.last_modified[ref_file]:
                self.last_modified[ref_file] = modified
                return True  # Update needed if file was modified
            else:
                return False

    def update_refs(self, ref_file):
        with open(ref_file, 'r') as f:
            bib = Bibparser(f.read())
        bib.parse()
        refs = bib.records
        self.refs[ref_file] = [get_item(refs[i]) for i in refs]

    def show_selector(self):
        window = sublime.active_window()

        ref_source, source = self.get_setting('bibtex_file',
                                              return_source=True)
        if source == 'project' and not os.path.isabs(ref_source):
            ref_dir = os.path.dirname(window.project_file_name())
            ref_source = os.path.join(ref_dir, ref_source)

        # Before showing selector, check whether BibTeX file was modified
        # and update it if needed
        if self.check_modified(ref_source):
            self.update_refs(ref_source)
        self.current_ref_source = ref_source
        window.show_quick_panel(self.refs[ref_source], self.insert_ref)

    def insert_ref(self, refid):
        references = self.refs[self.current_ref_source]
        if refid == -1:  # Don't do anything if nothing was selected
            return None
        ref = references[refid][0]
        citation = self.get_citation_style().replace('$CITATION', ref)
        view = sublime.active_window().active_view()
        view.run_command('insert_reference', {'reference': citation})

    def extract_citations(self):
        """
        Extracts those citations from the global BibTeX file
        that are cited in the currently active file, and saves them
        to a BibTeX file alongside the currently active file.

        """
        current_file = sublime.active_window().active_view().file_name()
        # split off extension
        basefile, extension = os.path.splitext(current_file)
        bibsubset_file = basefile + '.bib'
        bibtex_file = self.plugin_settings.get('bibtex_file')
        md2bib.extract_bibliography(current_file, bibtex_file,
                                    bibsubset_file,
                                    include_bibtex_style=True)
        _, fname = os.path.split(bibsubset_file)
        sublime.status_message('Extracted citations to {}'.format(fname))


class CiteBibtexShowSelectorCommand(sublime_plugin.ApplicationCommand):
    def run(self, **kwargs):
        _sublimebibtex.show_selector()


class InsertReferenceCommand(sublime_plugin.TextCommand):
    def run(self, edit, reference):
        # Only using the first cursor no matter how many there are
        cursor_pos = self.view.sel()[0].begin()
        self.view.insert(edit, cursor_pos, reference)


class ExtractCitationsCommand(sublime_plugin.ApplicationCommand):
    def run(self, **kwargs):
        _sublimebibtex.extract_citations()


def plugin_loaded():
    _sublimebibtex.plugin_loaded_setup()


_sublimebibtex = CiteBibtex()
