#!/usr/bin/env python3
"""
Application Setup - WebView window creation and configuration
"""

import webview
from typing import Optional


def create_app(api_instance, width: int = 1200, height: int = 800) -> webview.Window:
    """
    Create and configure the webview application

    Args:
        api_instance: The API instance to bind to the webview
        width: Window width in pixels
        height: Window height in pixels

    Returns:
        Configured webview Window instance
    """
    # Create the webview window
    window = webview.create_window(
        title="Markdown Explorer",
        url="../web/index.html",
        js_api=api_instance,
        width=width,
        height=height,
        min_size=(900, 600),
        resizable=True,
        maximized=False,
        on_top=False,
        shadow=True
    )

    return window


def start_app(window: webview.Window, debug: bool = False):
    """
    Start the webview application

    Args:
        window: The webview window to start
        debug: Whether to run in debug mode (shows dev tools)
    """
    # Start the webview (debug=False hides dev tools by default, but keeps them accessible)
    webview.start(debug=debug)
