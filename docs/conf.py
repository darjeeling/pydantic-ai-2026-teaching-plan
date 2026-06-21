from __future__ import annotations

import os

project = "Pydantic AI 2026 Teaching Plan"
author = "Darjeeling"
copyright = "2026, Darjeeling"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinxcontrib.mermaid",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # Internal working note, not part of the published site.
    "tone-rewrite-plan.md",
]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme = "furo"
html_title = "Pydantic AI 2026 Teaching Plan"
html_baseurl = os.getenv("SPHINX_HTML_BASEURL", "")

html_theme_options: dict[str, object] = {
    "light_logo": "logo-light.svg",
    "dark_logo": "logo-dark.svg",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

source_repository = os.getenv("DOCS_SOURCE_REPOSITORY")
if source_repository:
    html_theme_options.update(
        {
            "source_repository": source_repository,
            "source_branch": os.getenv("DOCS_SOURCE_BRANCH", "main"),
            "source_directory": os.getenv("DOCS_SOURCE_DIRECTORY", "docs/"),
        }
    )

myst_enable_extensions = [
    "attrs_block",
    "colon_fence",
    "deflist",
    "substitution",
]
myst_heading_anchors = 3
mermaid_version = "11.4.1"
linkcheck_timeout = 20
linkcheck_retries = 2
suppress_warnings = [
    "misc.highlighting_failure",
    "myst.xref_missing",
]
