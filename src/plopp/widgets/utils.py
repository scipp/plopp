# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import os

# Determine if the code is likely running in a VS Code environment:
RUNNING_IN_VSCODE = False
# Common in VS Code terminals / extension-launched processes
if os.environ.get("VSCODE_PID"):
    RUNNING_IN_VSCODE = True
if os.environ.get("TERM_PROGRAM") == "vscode":
    RUNNING_IN_VSCODE = True
# Sometimes present in remote scenarios
if "VSCODE_IPC_HOOK_CLI" in os.environ:
    RUNNING_IN_VSCODE = True
