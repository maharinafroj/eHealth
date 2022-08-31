
import os
import sys

sys.path.insert(0, os.path.abspath('../'))

project = 'Project Template'
copyright = '2022, Maharin Afroj'
author = 'Maharin Afroj'


master_doc = 'index'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx_rtd_theme']
templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    'canonical_url': 'https://dbgen.readthedocs.io/en/latest/',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}
html_static_path = ['_static']