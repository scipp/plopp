# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import sys

import matplotlib.pyplot as plt
import numpy as np
import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class Figure(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main widget
        self.setWindowTitle("Figure")
        self.setGeometry(100, 100, 800, 600)
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        # # Set up the layout
        layout = QVBoxLayout()
        # layout.addLayout(button_layout)
        # layout.addWidget(self.canvas)
        # layout.addWidget(self.slider)
        self.widget.setLayout(layout)

    def show(self):
        app = QApplication(sys.argv)
        window = self
        window.show()
        sys.exit(app.exec_())
