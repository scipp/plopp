# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
import json
import os

from ...graphics import BaseFig


class Figure(BaseFig):
    """ """

    def __init__(self, View, *args, **kwargs):
        self.view = View(*args, **kwargs)
        self.interactive = True

    def as_json(self):
        return {
            "axes": [self.view.canvas.as_json()],
            "artists": [artist.as_json() for artist in self.view.artists.values()],
        }

    def save(self, filename):
        """
        Save the figure to a json file.
        """
        ext = os.path.splitext(filename)[1]
        if ext.lower() != '.json':
            raise ValueError('File extension must be .json for saving figure.')

        with open(filename, 'w') as f:
            json.dump(self.as_json(), f)
