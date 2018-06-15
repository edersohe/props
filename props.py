from __future__ import print_function

import os
import re

from collections import OrderedDict

class Props(object):

    def __init__(self, trim_spaces=True, key_value_sep='=', commet_char='#', eol='\r\n'):
        self._lines = []
        self._dict = OrderedDict()
        self._index = OrderedDict()
        self._trim_spaces = trim_spaces
        self._key_value_sep = key_value_sep
        self._comment_char = commet_char
        self._eol = eol

    def load_file(self, path):
        f = open(path, 'r')
        text = f.read()
        f.close()

        self.load_text(text)

        return self

    def load_text(self, text):
        self._lines = re.split('\r?\n?', text)
        self.parse()

        return self

    def parse(self):
        for i in range(len(self._lines)):
            line = self._lines[i]
            if self._trim_spaces:
                line = line.strip().strip('\t')
            if line != '' and not line.startswith(self._comment_char):
                key, value = line.split(self._key_value_sep, 1)
                key = key.strip().strip('\t')
                value = value.strip().strip('\t')
                self._dict[key] = value
                self._index[key] = i

    def get(self, key):
        key = key.strip().strip('\t')
        return self._dict[key]

    def set(self, key, value):
        key = key.strip().strip('\t')
        value = value.strip().strip('\t')
        if key in self._dict:
            old_value = self._dict[key]
            index = self._index[key]
            if old_value != value:
                self._lines[index] = "# UPDATE << {}={} >>\r\n".format(key, old_value) + self._lines[index].replace(old_value, value)
                self._dict[key] = value
        else:
            self._lines.append("# NEW >>\r\n" + key + self._key_value_sep + value)
            self._index[key] = len(self._lines) - 1
            self._dict[key] = value


    def update(self, update_dict):
        for key, value in update_dict.items():
            key = key.strip().strip('\t')
            value = value.strip().strip('\t')
            self.set(key, value)

    def to_dict(self):
        return self._dict

    def to_file(self, path):
        f = open(path, 'w')
        f.write(self.to_text())
        f.close()

    def to_text(self):
        return self._eol.join(self._lines)

    def to_screen(self):
        print(self.to_text())


def merge_files_to_file(path_props_default, path_props_custom, path_result):
    props_default = Props().load_file(path_props_default)
    props_custom = Props().load_file(path_props_custom)

    props_default.update(props_custom.to_dict())

    props_default.to_file(path_result)


def merge_texts_to_file(text_props_default, text_props_custom, path_result):
    props_default = Props().load_text(text_props_default)
    props_custom = Props().load_text(text_props_custom)

    props_default.update(props_custom.to_dict())

    props_default.to_file(path_result)
