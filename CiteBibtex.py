import sublime
import sublime_plugin

import os

from .lib.bib import Bibparser


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

    def check_modified(self, ref_file):
        try:
            modified = os.path.getmtime(ref_file)
        except FileNotFoundError:
            error_message = 'ERROR: Can\'t open BibTeX file '
            sublime.status_message(error_message + ref_file)
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
        # Check whether there is a project-specific override, and if yes,
        # load the project-specific BibTeX file
        project_data = window.project_data()
        if 'bibtex_file' in project_data:
            ref_dir = os.path.dirname(window.project_file_name())
            ref_source = os.path.join(ref_dir, project_data['bibtex_file'])
        else:
            ref_source = self.plugin_settings.get('bibtex_file')
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
        if self.plugin_settings.get('reference_style') == 'pandoc':
            ref = '[@' + ref + ']'
        elif self.plugin_settings.get('reference_style') == 'latex':
            ref = '\citep{' + ref + '}'
        view = sublime.active_window().active_view()
        view.run_command('insert_reference', {'reference': ref})


class CiteBibtexShowSelectorCommand(sublime_plugin.ApplicationCommand):
    def run(self, **kwargs):
        _sublimebibtex.show_selector()


class InsertReferenceCommand(sublime_plugin.TextCommand):
    def run(self, edit, reference):
        # Only using the first cursor no matter how many there are
        cursor_pos = self.view.sel()[0].begin()
        self.view.insert(edit, cursor_pos, reference)


def plugin_loaded():
    _sublimebibtex.plugin_loaded_setup()


_sublimebibtex = CiteBibtex()
