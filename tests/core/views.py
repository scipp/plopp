# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from plopp import View


class SimpleView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = None

    def notify_view(self, message):
        self.value = message


class DataView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def notify_view(self, message):
        node_id = message["node_id"]
        self.data = self.graph_nodes[node_id].request_data()
