# Pages module - all page renderers
from frontend.pages.home import render_home
from frontend.pages.library import render_library
from frontend.pages.coding import render_coding_problem
from frontend.pages.math import render_math_problem
from frontend.pages.deeplearning import render_dl_problem
from frontend.pages.knowledge_map import render_knowledge_map
from frontend.pages.knowledge_detail import render_knowledge_detail

__all__ = [
    "render_home",
    "render_library",
    "render_coding_problem",
    "render_math_problem",
    "render_dl_problem",
    "render_knowledge_map",
    "render_knowledge_detail",
]
