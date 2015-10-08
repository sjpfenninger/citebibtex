import sublime
import sublime_plugin

import os
from collections import defaultdict

from .lib.bibtexparser.bparser import BibTexParser
from .lib.bibtexparser import customization
from .lib import md2bib


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
        self.refs_dict = {}
        self.refs = {}
        self.ref_keys = {}
        _ = self.check_modified(global_file)
        self._update_in_progress = False
        sublime.set_timeout_async(lambda: self.update_refs(global_file), 0)

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
            raise
        if ref_file not in self.last_modified:  # Initialize if needed
            self.last_modified[ref_file] = modified
            return True  # Upate needed if this file was never seen before
        else:
            if modified > self.last_modified[ref_file]:
                self.last_modified[ref_file] = modified
                return True  # Update needed if file was modified
            else:
                return False

    def get_item(self, i):
        # Year
        try:
            year = i['year']
        except KeyError:
            try:
                year = i['issued']
            except KeyError:
                year = '<no date>'

        # Authors
        try:
            authors = i['author']
            # authors is a list of 'last, first' strings, we only want
            # the last names here
            authors = ', '.join([a.split(',',)[0] for a in authors])
        except KeyError:
            authors = '<no authors>'

        # Title
        try:
            title = i['title']
        except KeyError:
            title = ''

        # Publication
        if 'journal' in i or 'journaltitle' in i:
            if 'journal' in i:
                publication = i['journal']
            else:
                publication = i['journaltitle']
            if 'volume' in i:
                publication = publication + ' (' + i['volume'] + ')'
            if 'number' in i:
                publication = publication + ' ' + i['number']
        else:
            try:
                publication = i['institution']
            except KeyError:
                try:
                    publication = i['booktitle']
                except KeyError:
                    # Final fallback if cannot determine publication
                    publication = i['ENTRYTYPE'].capitalize()

        # Set search key
        search_key = i['ID']
        additional_search_fields = self.get_setting('additional_search_fields')
        if additional_search_fields:
            search_key += ' | '
            for field in additional_search_fields:
                try:
                    if isinstance(i[field], list):
                        result = ', '.join(i[field])
                    else:
                        result = i[field]
                    search_key += result + ' | '
                except KeyError:
                    pass

        return [search_key, year + ' | ' + authors, title, publication]

    def update_refs(self, ref_file):
        self._update_in_progress = True
        encoding = self.get_setting('bibtex_file_encoding')
        parser = BibTexParser()
        parser.ignore_nonstandard_types = False
        def customizer(record):
            record = customization.author(record)
            return record
        parser.customization = customizer
        with open(ref_file, 'r', encoding=encoding) as f:
            bib = parser.parse_file(f)
        self.refs_dict[ref_file] = refs = bib.entries_dict
        self.refs[ref_file] = [self.get_item(refs[i]) for i in refs]
        self.ref_keys[ref_file] = [refs[i]['ID'] for i in refs]
        self._update_in_progress = False

    def update_refs_then_show_panel(self, ref_file):
        window = sublime.active_window()
        self.update_refs(ref_file)
        ref_source = self.current_ref_source
        window.show_quick_panel(self.refs[ref_source], self.insert_ref)

    def show_selector(self, selector_callback=None):

        if selector_callback is None:
            selector_callback = self.insert_ref

        # Don't do anything if this is repeatedly called during an update,
        # until BibTeX file is completely read
        if self._update_in_progress:
            return None

        window = sublime.active_window()

        ref_source, source = self.get_setting('bibtex_file',
                                              return_source=True)
        if source == 'project' and not os.path.isabs(ref_source):
            ref_dir = os.path.dirname(window.project_file_name())
            ref_source = os.path.join(ref_dir, ref_source)
        self.current_ref_source = ref_source

        # Before showing selector, check whether BibTeX file was modified
        # and update it if needed
        if self.check_modified(ref_source):
            sublime.status_message('BibTeX file has changed; reloading.')
            callback = lambda: self.update_refs_then_show_panel(ref_source)
            sublime.set_timeout_async(callback, 0)
        else:
            window.show_quick_panel(self.refs[ref_source], selector_callback)

    def insert_ref(self, refid):
        if refid == -1:  # Don't do anything if nothing was selected
            return None
        ref_key = self.ref_keys[self.current_ref_source][refid]
        citation = self.get_citation_style().replace('$CITATION', ref_key)
        view = sublime.active_window().active_view()
        view.run_command('insert_reference', {'reference': citation})

    def insert_citation(self, refid):
        if refid == -1:  # Don't do anything if nothing was selected
            return None
        ref_key = self.ref_keys[self.current_ref_source][refid]
        # Use defaultdict to prevent errors in format string
        # due to missing keys, simply filing them with empty strings
        ref_dict = defaultdict(lambda: '',
                               self.refs_dict[self.current_ref_source][ref_key].copy())
        text_fmt = self.get_setting('citation_format_string')
        # Concatenate all authors into one string
        ref_dict['author'] = ', '.join(ref_dict['author']).strip()
        text = text_fmt.format(**ref_dict)
        view = sublime.active_window().active_view()
        view.run_command('insert_reference', {'reference': text})

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
                                    bibsubset_file)
        _, fname = os.path.split(bibsubset_file)
        sublime.status_message('Extracted citations to {}'.format(fname))


class CiteBibtexShowReferenceSelectorCommand(sublime_plugin.ApplicationCommand):
    def run(self, **kwargs):
        _sublimebibtex.show_selector()


class CiteBibtexShowCitationSelectorCommand(sublime_plugin.ApplicationCommand):
    def run(self, **kwargs):
        _sublimebibtex.show_selector(selector_callback=_sublimebibtex.insert_citation)


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
