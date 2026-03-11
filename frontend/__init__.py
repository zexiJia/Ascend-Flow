# filename: frontend/__init__.py
"""Frontend module - UI components, theme, state management and pages"""

# Theme and styling
from frontend.theme import inject_global_css, inject_sidebar_js, topbar

# State management
from frontend.state import (
    init_state,
    reset_problem_state,
    go_to_problem,
    go_to_library,
    go_to_knowledge_map,
    go_to_knowledge_detail,
    go_home,
    logout,
)

# Sidebar
from frontend.sidebar import render_sidebar

# UI components
from frontend.components import (
    StepItem,
    badge,
    render_stepper,
    card,
    avatar_data_uri,
    role_avatar,
)

# Pages
from frontend.pages import (
    render_home,
    render_library,
    render_coding_problem,
    render_math_problem,
    render_dl_problem,
    render_knowledge_map,
    render_knowledge_detail,
)

from frontend.pages.login import render_login

__all__ = [
    # Theme
    "inject_global_css",
    "inject_sidebar_js",
    "topbar",
    # State
    "init_state",
    "reset_problem_state",
    "go_to_problem",
    "go_to_library",
    "go_to_knowledge_map",
    "go_to_knowledge_detail",
    "go_home",
    "logout",
    # Sidebar
    "render_sidebar",
    # Components
    "StepItem",
    "badge",
    "render_stepper",
    "card",
    "avatar_data_uri",
    "role_avatar",
    # Pages
    "render_home",
    "render_library",
    "render_coding_problem",
    "render_math_problem",
    "render_dl_problem",
    "render_knowledge_map",
    "render_knowledge_detail",
    "render_login",
]
