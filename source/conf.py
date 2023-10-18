# needed packages:
# myst-parser
# sphinx-markdown-tables
# sphinx-notfound-page
# linkify-it-py
# to install it use:
# python -m pip install myst-parser sphinx-markdown-tables sphinx-notfound-page linkify-it-py

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Colada'
copyright = '2023, Kerim Khemraev'
author = 'Kerim Khemraev'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',              # [pip install myst-parser] to use .md as source files
    'sphinx_markdown_tables',   # [pip install sphinx-markdown-tables]
    'notfound.extension',       # [pip install sphinx-notfound-page] Show a better 404 page when an invalid address is entered
]

myst_enable_extensions = [
    "colon_fence",  # Allow code fence using ::: (see https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html#syntax-colon-fence)
    "linkify",      # [linkify-it-py] Allow automatic creation of links from URLs (it is sufficient to write https://google.com instead of <https://google.com>)
    "attrs_inline",
]

# Auto-generate header anchors up to level 6, so that it can be referenced like [](file.md#header-anchor).
# (see https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html#auto-generated-header-anchors)
myst_heading_anchors = 6

templates_path = ['_templates']
exclude_patterns = []

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst', '.md']

# sphinx-notfound-page
# https://github.com/readthedocs/sphinx-notfound-page
notfound_context = {
    'title': 'Page Not Found',
    'body': '''
<h1>Page Not Found</h1>
<p>Sorry, we couldn't find that page.</p>
<p>Try using the search box or go to the homepage.</p>
''',
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_logo = '../logo_64x64.png'
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    # 'includehidden': False,
    # # Toc options
    # 'collapse_navigation': True,
    # 'sticky_navigation': True,
    # 'navigation_depth': 4,
    # 'includehidden': True,
    # 'titles_only': False
}

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/custom.css',
]