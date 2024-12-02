# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)
import pytest
from playwright.sync_api import Browser, Page, expect

_EXPECTED_JUPYTER_LAB_ADDRESS = "http://localhost:8888/lab"


@pytest.fixture(scope="session")
def jupyter_lab_running(browser: Browser) -> bool:
    """Skip tests if jupyter lab is not running in the background."""
    try:
        # Try opening the Jupyter Lab page.
        with browser.new_page() as page:
            page.goto(_EXPECTED_JUPYTER_LAB_ADDRESS)
    except Exception as e:
        # Check if 'net::ERR_CONNECTION_REFUSED' is in the error message.
        # Playwright does not have different error objects for different errors.
        # So, we have to check the error message.
        if "net::ERR_CONNECTION_REFUSED" in str(e):
            pytest.skip(
                f"Jupyter Lab is not running at {_EXPECTED_JUPYTER_LAB_ADDRESS}."
                "Check if jupyter lab is running without TOKEN or PASSWORD"
                "and the address is correct."
            )
            return False
        # Raise the exception if it is not the expected error.
        raise e
    return True


def test_jupyter_lab_server_available(jupyter_lab_running: bool, page: Page) -> None:
    # Expect a title "to contain" a substring.
    assert jupyter_lab_running
    page.goto(_EXPECTED_JUPYTER_LAB_ADDRESS)
    expect(page).to_have_title("JupyterLab")
