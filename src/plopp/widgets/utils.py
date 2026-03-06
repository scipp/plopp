# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 Scipp contributors (https://github.com/scipp)

import os


def likely_running_in_vscode() -> bool:
    """
    Determine if the code is likely running in a VS Code environment.

    Returns
    -------
    bool
        True if running in VS Code, False otherwise.
    """
    # Common in VS Code terminals / extension-launched processes
    if os.environ.get("VSCODE_PID"):
        return True
    if os.environ.get("TERM_PROGRAM") == "vscode":
        return True
    # Sometimes present in remote scenarios
    if "VSCODE_IPC_HOOK_CLI" in os.environ:
        return True
    return False
