from pallets_sphinx_themes import ProjectLink, get_version

# Project --------------------------------------------------------------

project = "Click"
copyright = "2014 Pallets Team"
author = "Pallets Team"
release, version = get_version("Click", version_length=1)

# General --------------------------------------------------------------

master_doc = "index"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "pallets_sphinx_themes"]
intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

# HTML -----------------------------------------------------------------

html_theme = "click"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("Pallets에 후원하기", "https://palletsprojects.com/donate"),
        ProjectLink("클릭 웹사이트", "https://palletsprojects.com/p/click/"),
        ProjectLink("PyPI 릴리스", "https://pypi.org/project/Click/"),
        ProjectLink("소스 코드", "https://github.com/pallets/click/"),
        ProjectLink("이슈 트래커", "https://github.com/pallets/click/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "versions.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "versions.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "versions.html", "localtoc.html"]}
html_static_path = ["_static"]
html_favicon = "_static/click-icon.png"
html_logo = "_static/click-logo-sidebar.png"
html_title = "Click Documentation ({})".format(version)
html_show_sourcelink = False
html_domain_indices = False
html_experimental_html5_writer = True

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, "Click-{}.tex".format(version), html_title, author, "manual")
]
