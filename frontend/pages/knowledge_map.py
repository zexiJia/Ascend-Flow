# filename: frontend/pages/knowledge_map.py
"""知识图谱可视化 - 思维导图风格
1. 宏观知识网 (Global Macro View) - 思维导图，显示知识体系
2. 中观路径图 (Learning Path View) - 学习路径，显示前后依赖
3. 微观迁移桥 (Micro Transfer Bridge) - 迁移关系对比

使用 vis-network.js (CDN) 实现图可视化，思维导图风格
"""

from __future__ import annotations

import json
import streamlit as st
import streamlit.components.v1 as components

from knowledge.loader import (
    get_all_knowledge_nodes,
    get_knowledge_nodes_by_level,
    get_knowledge_node_by_id,
)
from knowledge.graph import get_children, get_items_for_node, get_prereqs, get_ancestors
from frontend.state import go_to_knowledge_detail, go_to_problem


# 🎨 思维导图配色方案 - 更柔和的渐变色
SUBJECT_THEMES = {
    "math": {
        "primary": "#6366f1",      # 靛蓝
        "secondary": "#818cf8",
        "light": "#c7d2fe",
        "bg": "#eef2ff",
        "gradient": "linear-gradient(135deg, #6366f1, #8b5cf6)",
    },
    "coding": {
        "primary": "#10b981",      # 翠绿
        "secondary": "#34d399",
        "light": "#a7f3d0",
        "bg": "#ecfdf5",
        "gradient": "linear-gradient(135deg, #10b981, #06b6d4)",
    },
    "deeplearning": {
        "primary": "#f59e0b",      # 琥珀
        "secondary": "#fbbf24",
        "light": "#fde68a",
        "bg": "#fffbeb",
        "gradient": "linear-gradient(135deg, #f59e0b, #ef4444)",
    },
}

# 层级配色
LEVEL_THEMES = {
    "macro": {"color": "#6366f1", "size": 45, "font": 14, "shape": "box"},
    "meso": {"color": "#10b981", "size": 32, "font": 12, "shape": "ellipse"},
    "micro": {"color": "#f59e0b", "size": 20, "font": 10, "shape": "dot"},
}

SUBJECT_ICONS = {"math": "📐", "coding": "💻", "deeplearning": "🧠"}
SUBJECT_NAMES = {"math": "数学", "coding": "编程", "deeplearning": "深度学习"}


def render_knowledge_map() -> None:
    """渲染知识图谱/知识库"""
    
    # 根据是否指定学科显示不同标题
    init_subject = st.session_state.get("knowledge_map_subject")
    subject_names = {"math": "数学", "coding": "编程", "deeplearning": "深度学习"}
    
    if init_subject and init_subject in subject_names:
        st.markdown(f"## 📖 {subject_names[init_subject]}知识库")
        st.caption("浏览知识点，点击开始学习")
    else:
        st.markdown("## 🗺️ 知识图谱")
        st.caption("浏览知识结构，在下方选择知识点开始学习")
    
    # 视图切换
    view_options = [
        ("🌐 思维导图", "macro"),
        ("📊 学习路径", "path"),
        ("🔗 迁移关系", "transfer"),
    ]
    current_view = st.session_state.get("kg_view", "macro")
    
    # 标签按钮
    cols = st.columns(3)
    for i, (label, key) in enumerate(view_options):
        with cols[i]:
            btn_type = "primary" if key == current_view else "secondary"
            if st.button(label, key=f"tab_{key}", use_container_width=True, type=btn_type):
                st.session_state.kg_view = key
                st.rerun()
    
    st.markdown("---")
    
    # 根据视图渲染
    if current_view == "macro":
        _render_mindmap_view()
    elif current_view == "path":
        _render_path_view()
    else:
        _render_transfer_view()


def _render_mindmap_graph(nodes_data: list, edges_data: list, height: int = 650) -> str:
    """生成思维导图风格的图可视化 HTML"""
    
    nodes_json = json.dumps(nodes_data, ensure_ascii=False)
    edges_json = json.dumps(edges_data, ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow: hidden; }}
            #graph {{
                width: 100%;
                height: {height}px;
                border-radius: 16px;
                background: linear-gradient(145deg, #fafbff 0%, #f0f4ff 50%, #e8f4f8 100%);
            }}
            .vis-tooltip {{
                background: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 12px 16px !important;
                font-family: inherit !important;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15) !important;
                font-size: 13px !important;
                line-height: 1.5 !important;
                max-width: 250px !important;
            }}
            /* 缩放控制按钮 */
            .zoom-controls {{
                position: absolute;
                top: 12px;
                right: 12px;
                display: flex;
                flex-direction: column;
                gap: 6px;
                z-index: 100;
            }}
            .zoom-btn {{
                width: 36px;
                height: 36px;
                border: none;
                border-radius: 8px;
                background: white;
                color: #6366f1;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: all 0.2s;
            }}
            .zoom-btn:hover {{
                background: #6366f1;
                color: white;
                transform: scale(1.05);
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="zoom-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">−</button>
            <button class="zoom-btn" onclick="fitAll()" style="font-size:14px;">⟲</button>
        </div>
        <script>
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            
            var container = document.getElementById('graph');
            var data = {{ nodes: nodes, edges: edges }};
            
            var options = {{
                nodes: {{
                    font: {{
                        face: '-apple-system, BlinkMacSystemFont, sans-serif',
                        color: '#1e293b',
                        strokeWidth: 0,
                        size: 14
                    }},
                    borderWidth: 3,
                    borderWidthSelected: 5,
                    shadow: {{
                        enabled: true,
                        color: 'rgba(0,0,0,0.12)',
                        size: 12,
                        x: 0,
                        y: 4
                    }},
                    scaling: {{
                        min: 20,
                        max: 50,
                        label: {{ enabled: true, min: 12, max: 18 }}
                    }}
                }},
                edges: {{
                    smooth: {{
                        type: 'curvedCW',
                        roundness: 0.12
                    }},
                    arrows: {{
                        to: {{
                            enabled: true,
                            scaleFactor: 0.5,
                            type: 'arrow'
                        }}
                    }},
                    color: {{
                        inherit: false,
                        opacity: 0.6
                    }},
                    width: 2,
                    hoverWidth: 4,
                    selectionWidth: 4
                }},
                physics: {{
                    enabled: true,
                    barnesHut: {{
                        gravitationalConstant: -4000,
                        centralGravity: 0.4,
                        springLength: 200,
                        springConstant: 0.015,
                        damping: 0.12,
                        avoidOverlap: 0.6
                    }},
                    stabilization: {{
                        iterations: 200,
                        fit: true
                    }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true,
                    dragNodes: true,
                    zoomSpeed: 0.8,
                    minZoom: 0.6,
                    maxZoom: 3,
                    navigationButtons: false,
                    keyboard: {{ enabled: true, speed: {{ x: 10, y: 10, zoom: 0.1 }} }}
                }}
            }};
            
            var network = new vis.Network(container, data, options);
            
            // 缩放函数
            function zoomIn() {{
                var scale = network.getScale();
                network.moveTo({{ scale: scale * 1.3, animation: true }});
            }}
            function zoomOut() {{
                var scale = network.getScale();
                network.moveTo({{ scale: scale / 1.3, animation: true }});
            }}
            function fitAll() {{
                network.fit({{ animation: true }});
            }}

            // 缩放下限/上限保护：避免缩得太小影响操作
            var MIN_ZOOM = 0.6;
            var MAX_ZOOM = 3.0;
            network.on('zoom', function() {{
                var s = network.getScale();
                if (s < MIN_ZOOM) {{ network.moveTo({{ scale: MIN_ZOOM }}); }}
                if (s > MAX_ZOOM) {{ network.moveTo({{ scale: MAX_ZOOM }}); }}
            }});

            // 点击节点进入学习：修改父页面 URL 参数 kp，让 Streamlit 捕获并跳转
            var isDragging = false;
            network.on('dragStart', function() {{ isDragging = true; }});
            network.on('dragEnd', function() {{ setTimeout(function(){{ isDragging = false; }}, 50); }});
            network.on('click', function(params) {{
                if (isDragging) return;
                if (params.nodes && params.nodes.length > 0) {{
                    var nodeId = params.nodes[0];
                    try {{
                        var url = new URL(window.parent.location.href);
                        url.searchParams.set('kp', nodeId);
                        window.parent.location.href = url.toString();
                    }} catch(e) {{
                        window.parent.location.search = '?kp=' + encodeURIComponent(nodeId);
                    }}
                }}
            }});

            // 悬停效果
            network.on('hoverNode', function(params) {{
                container.style.cursor = 'pointer';
            }});
            network.on('blurNode', function(params) {{
                container.style.cursor = 'grab';
            }});
            
            // 稳定后自适应
            network.once('stabilized', function() {{
                network.fit({{ animation: false }});
            }});
        </script>
    </body>
    </html>
    """
    return html


def _render_mindmap_graph_display(nodes_data: list, edges_data: list, height: int = 500) -> str:
    """生成纯展示用的思维导图 HTML（无点击跳转，仅用于可视化）"""
    
    nodes_json = json.dumps(nodes_data, ensure_ascii=False)
    edges_json = json.dumps(edges_data, ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow: hidden; }}
            #graph {{
                width: 100%;
                height: {height}px;
                border-radius: 16px;
                background: linear-gradient(145deg, #fafbff 0%, #f0f4ff 50%, #e8f4f8 100%);
            }}
            .vis-tooltip {{
                background: white !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 12px 16px !important;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15) !important;
                font-size: 13px !important;
                max-width: 250px !important;
            }}
            .zoom-controls {{
                position: absolute;
                top: 12px;
                right: 12px;
                display: flex;
                flex-direction: column;
                gap: 6px;
                z-index: 100;
            }}
            .zoom-btn {{
                width: 36px;
                height: 36px;
                border: none;
                border-radius: 8px;
                background: white;
                color: #6366f1;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .zoom-btn:hover {{
                background: #6366f1;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="zoom-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">−</button>
            <button class="zoom-btn" onclick="fitAll()" style="font-size:14px;">⟲</button>
        </div>
        <script>
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            var container = document.getElementById('graph');
            var data = {{ nodes: nodes, edges: edges }};
            
            var options = {{
                nodes: {{
                    font: {{ face: '-apple-system, sans-serif', color: '#1e293b', size: 14 }},
                    borderWidth: 3,
                    shadow: {{ enabled: true, color: 'rgba(0,0,0,0.12)', size: 12 }},
                    scaling: {{ min: 20, max: 50, label: {{ enabled: true, min: 12, max: 18 }} }}
                }},
                edges: {{
                    smooth: {{ type: 'curvedCW', roundness: 0.12 }},
                    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                    color: {{ inherit: false, opacity: 0.6 }},
                    width: 2
                }},
                physics: {{
                    enabled: true,
                    barnesHut: {{
                        gravitationalConstant: -4000,
                        centralGravity: 0.4,
                        springLength: 200,
                        springConstant: 0.015,
                        damping: 0.12,
                        avoidOverlap: 0.6
                    }},
                    stabilization: {{ iterations: 200, fit: true }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true,
                    dragNodes: true,
                    zoomSpeed: 0.8,
                    minZoom: 0.5,
                    maxZoom: 3
                }}
            }};
            
            var network = new vis.Network(container, data, options);
            
            function zoomIn() {{ network.moveTo({{ scale: network.getScale() * 1.3, animation: true }}); }}
            function zoomOut() {{ network.moveTo({{ scale: network.getScale() / 1.3, animation: true }}); }}
            function fitAll() {{ network.fit({{ animation: true }}); }}
            
            network.on('hoverNode', function() {{ container.style.cursor = 'pointer'; }});
            network.on('blurNode', function() {{ container.style.cursor = 'grab'; }});
            network.once('stabilized', function() {{ network.fit({{ animation: false }}); }});
        </script>
    </body>
    </html>
    """
    return html


def _render_mindmap_view() -> None:
    """思维导图视图 - 展示知识体系"""
    
    # 筛选器
    col1, col2, col3 = st.columns([1, 1, 2])
    
    # 从 session state 获取初始学科筛选
    init_subject = st.session_state.get("knowledge_map_subject")
    subject_options = ["全部学科", "📐 数学", "💻 编程", "🧠 深度学习"]
    subject_map = {"math": 1, "coding": 2, "deeplearning": 3}
    default_idx = subject_map.get(init_subject, 0)
    
    with col1:
        show_level = st.selectbox(
            "📊 显示层级",
            ["一二级节点", "仅一级节点", "全部节点"],
            key="mm_level"
        )
    with col2:
        subject_filter = st.selectbox(
            "📚 学科筛选",
            subject_options,
            index=default_idx,
            key="mm_subject"
        )
    
    # 构建图数据
    nodes_data, edges_data, node_map = _build_mindmap_data(show_level, subject_filter)
    
    if not nodes_data:
        st.info("暂无知识节点")
        return
    
    # 操作提示
    st.caption("🖱️ 拖拽移动 | 滚轮缩放 | 在下方选择知识点开始学习")
    
    # 渲染思维导图（纯展示）
    html = _render_mindmap_graph_display(nodes_data, edges_data, height=500)
    components.html(html, height=530)
    
    # 图例
    _render_legend()
    
    # 在图下方提供可点击的知识点列表
    _render_node_selector(node_map)


def _build_mindmap_data(level_filter: str, subject_filter: str):
    """构建思维导图数据"""
    all_nodes = get_all_knowledge_nodes()
    
    # 层级筛选
    if level_filter == "仅一级节点":
        filter_levels = {"macro"}
    elif level_filter == "一二级节点":
        filter_levels = {"macro", "meso"}
    else:
        filter_levels = {"macro", "meso", "micro"}
    
    # 学科筛选
    subject_map = {"📐 数学": "math", "💻 编程": "coding", "🧠 深度学习": "deeplearning"}
    selected_subject = subject_map.get(subject_filter)
    
    filtered = [n for n in all_nodes if n.level in filter_levels]
    if selected_subject:
        filtered = [n for n in filtered if n.subject == selected_subject]
    
    valid_ids = {n.node_id for n in filtered}
    
    nodes_data = []
    edges_data = []
    node_map = {}  # node_id -> node object
    
    for n in filtered:
        node_map[n.node_id] = n
        theme = SUBJECT_THEMES.get(n.subject, SUBJECT_THEMES["math"])
        level_cfg = LEVEL_THEMES.get(n.level, LEVEL_THEMES["meso"])
        
        # 根据层级设置不同样式
        if n.level == "macro":
            # 一级节点 - 大圆角矩形，渐变色背景
            icon = SUBJECT_ICONS.get(n.subject, "📖")
            nodes_data.append({
                "id": n.node_id,
                "label": f"{icon} {n.name}",
                "size": level_cfg["size"],
                "shape": "box",
                "color": {
                    "background": theme["primary"],
                    "border": theme["secondary"],
                    "highlight": {"background": theme["secondary"], "border": theme["primary"]},
                    "hover": {"background": theme["secondary"], "border": theme["primary"]},
                },
                "font": {"color": "#ffffff", "size": level_cfg["font"], "bold": True},
                "margin": 12,
                "shapeProperties": {"borderRadius": 12},
                "title": f"<b>{n.name}</b><br/>📚 {SUBJECT_NAMES.get(n.subject, '')}<br/>⭐ 难度 {n.difficulty}/10<br/><br/>点击查看详情",
            })
        elif n.level == "meso":
            # 二级节点 - 椭圆，柔和颜色
            nodes_data.append({
                "id": n.node_id,
                "label": n.name,
                "size": level_cfg["size"],
                "shape": "ellipse",
                "color": {
                    "background": theme["light"],
                    "border": theme["primary"],
                    "highlight": {"background": theme["secondary"], "border": theme["primary"]},
                    "hover": {"background": theme["secondary"], "border": theme["primary"]},
                },
                "font": {"color": theme["primary"], "size": level_cfg["font"]},
                "title": f"<b>{n.name}</b><br/>📖 二级知识点<br/>⭐ 难度 {n.difficulty}/10<br/><br/>点击查看详情",
            })
        else:
            # 三级节点 - 小圆点
            nodes_data.append({
                "id": n.node_id,
                "label": n.name,
                "size": level_cfg["size"],
                "shape": "dot",
                "color": {
                    "background": theme["secondary"],
                    "border": theme["primary"],
                    "highlight": {"background": theme["primary"], "border": theme["primary"]},
                    "hover": {"background": theme["primary"], "border": theme["primary"]},
                },
                "font": {"color": "#475569", "size": level_cfg["font"]},
                "title": f"<b>{n.name}</b><br/>🎯 技能点<br/><br/>点击查看详情",
            })
        
        # 父子边 - 柔和曲线
        for p in n.parents:
            if p in valid_ids:
                parent_node = node_map.get(p) or get_knowledge_node_by_id(p)
                edge_color = SUBJECT_THEMES.get(parent_node.subject if parent_node else n.subject, 
                                                SUBJECT_THEMES["math"])["secondary"]
                edges_data.append({
                    "from": p,
                    "to": n.node_id,
                    "color": {"color": edge_color, "highlight": edge_color},
                    "width": 2 if n.level == "meso" else 1,
                })
        
        # 前置边 - 虚线
        for pre in n.prereq:
            if pre in valid_ids and pre not in n.parents:
                edges_data.append({
                    "from": pre,
                    "to": n.node_id,
                    "color": {"color": "#a78bfa", "highlight": "#8b5cf6"},
                    "width": 1,
                    "dashes": [8, 4],
                    "title": "迁移关系",
                })
    
    return nodes_data, edges_data, node_map


def _render_legend() -> None:
    """渲染图例"""
    st.markdown("""
    <div style="display:flex;gap:1.5rem;justify-content:center;padding:1rem 0;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:20px;height:20px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:4px;"></div>
            <span style="font-size:0.8rem;color:#64748b;">一级（学科）</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:18px;height:14px;background:#c7d2fe;border:2px solid #6366f1;border-radius:8px;"></div>
            <span style="font-size:0.8rem;color:#64748b;">二级（主题）</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:12px;height:12px;background:#818cf8;border-radius:50%;"></div>
            <span style="font-size:0.8rem;color:#64748b;">三级（技能）</span>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <div style="width:20px;border-top:2px dashed #a78bfa;"></div>
            <span style="font-size:0.8rem;color:#64748b;">迁移关系</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_node_selector(node_map: dict) -> None:
    """在图下方提供可点击的知识点选择器"""
    if not node_map:
        return
    
    st.markdown("### 📌 选择知识点开始学习")
    
    # 构建选项列表
    nodes_list = list(node_map.values())
    
    # 按学科和层级排序
    level_order = {"macro": 0, "meso": 1, "micro": 2}
    nodes_list.sort(key=lambda x: (x.subject, level_order.get(x.level, 9), x.name))
    
    # 构建下拉选项
    options = ["-- 请选择 --"] + [
        f"{SUBJECT_ICONS.get(n.subject, '📖')} {n.name}" 
        for n in nodes_list
    ]
    
    selected_idx = st.selectbox(
        "🔍 选择知识点",
        range(len(options)),
        format_func=lambda i: options[i],
        key="mm_node_select",
        label_visibility="collapsed"
    )
    
    if selected_idx == 0:
        st.caption("👆 从上方下拉框选择一个知识点，或直接点击下方按钮")
        
        # 显示快捷按钮（按学科分组，每学科显示前几个）
        st.markdown("#### 🚀 快速入口")
        
        by_subject = {"math": [], "coding": [], "deeplearning": []}
        for n in nodes_list:
            if n.subject in by_subject and n.level in ("macro", "meso"):
                by_subject[n.subject].append(n)
        
        cols = st.columns(3)
        for i, (subj, name) in enumerate([("math", "数学"), ("coding", "编程"), ("deeplearning", "深度学习")]):
            with cols[i]:
                theme = SUBJECT_THEMES.get(subj, SUBJECT_THEMES["math"])
                st.markdown(f"**{SUBJECT_ICONS.get(subj, '')} {name}**")
                for n in by_subject.get(subj, [])[:4]:
                    level_badge = "🔷" if n.level == "macro" else "🔹"
                    if st.button(f"{level_badge} {n.name}", key=f"quick_{n.node_id}", use_container_width=True):
                        go_to_knowledge_detail(n.node_id)
                        st.rerun()
        return
    
    # 选中了某个节点
    node = nodes_list[selected_idx - 1]
    
    # 显示节点信息卡片
    theme = SUBJECT_THEMES.get(node.subject, SUBJECT_THEMES["math"])
    icon = SUBJECT_ICONS.get(node.subject, "📖")
    level_name = {"macro": "一级知识点", "meso": "二级知识点", "micro": "技能点"}.get(node.level, "知识点")
    
    children = get_children(node.node_id)
    items = get_items_for_node(node.node_id)
    
    st.markdown(f"""
    <div style="background:{theme['bg']};border-radius:16px;padding:1.25rem;margin:1rem 0;
                border-left:4px solid {theme['primary']};">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
            <span style="font-size:1.8rem;">{icon}</span>
            <div>
                <div style="font-size:1.2rem;font-weight:600;color:#1e293b;">{node.name}</div>
                <div style="font-size:0.8rem;color:#64748b;">{level_name} · 难度 {node.difficulty}/10</div>
            </div>
        </div>
        <div style="color:#475569;font-size:0.9rem;margin-bottom:0.75rem;">
            {node.content.content_summary or '暂无描述'}
        </div>
        <div style="display:flex;gap:1.5rem;font-size:0.85rem;color:#64748b;">
            <span>📚 {len(children)} 个子知识点</span>
            <span>📝 {len(items)} 道关联题目</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 开始学习按钮
    if st.button(f"📚 开始学习「{node.name}」", key=f"learn_{node.node_id}", type="primary", use_container_width=True):
        go_to_knowledge_detail(node.node_id)
        st.rerun()
    
    # 显示子知识点
    if children:
        with st.expander(f"📖 查看子知识点 ({len(children)})", expanded=False):
            for c in children[:10]:
                c_icon = SUBJECT_ICONS.get(c.subject, "📖")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{c_icon} **{c.name}**")
                with col2:
                    if st.button("学习", key=f"child_{c.node_id}"):
                        go_to_knowledge_detail(c.node_id)
                        st.rerun()


def _render_path_view() -> None:
    """学习路径视图"""
    
    # 选择器
    col1, col2 = st.columns([1, 2])
    
    with col1:
        subject_filter = st.selectbox(
            "📚 学科",
            ["全部"] + list(SUBJECT_NAMES.values()),
            key="pv_subject"
        )
    
    subject_reverse = {v: k for k, v in SUBJECT_NAMES.items()}
    selected_subject = subject_reverse.get(subject_filter)
    
    meso_nodes = get_knowledge_nodes_by_level("meso")
    if selected_subject:
        meso_nodes = [n for n in meso_nodes if n.subject == selected_subject]
    
    with col2:
        if not meso_nodes:
            st.info("暂无知识点")
            return
        node_options = {f"{SUBJECT_ICONS.get(n.subject, '')} {n.name}": n.node_id for n in meso_nodes}
        selected_label = st.selectbox("🎯 选择知识点", list(node_options.keys()), key="pv_node")
    
    selected_id = node_options.get(selected_label)
    if not selected_id:
        return
    
    # 操作提示
    st.caption("🖱️ 点击节点查看详情 | 拖拽移动 | 滚轮缩放")
    
    # 构建路径图
    nodes_data, edges_data, path_node_map = _build_path_data(selected_id)
    
    # 渲染路径图
    html = _render_path_graph(nodes_data, edges_data, height=420)
    components.html(html, height=450)
    
    # 学习建议
    _render_learning_suggestions(selected_id)


def _build_path_data(center_id: str):
    """构建路径图数据"""
    center = get_knowledge_node_by_id(center_id)
    if not center:
        return [], [], {}
    
    nodes_data = []
    edges_data = []
    node_map = {}
    
    prereqs = get_prereqs(center_id, transitive=True)[:4]
    children = get_children(center_id)[:6]
    
    theme = SUBJECT_THEMES.get(center.subject, SUBJECT_THEMES["math"])
    
    # 前置节点
    for i, p in enumerate(prereqs):
        node_map[p.node_id] = p
        nodes_data.append({
            "id": p.node_id,
            "label": p.name,
            "size": 24,
            "shape": "ellipse",
            "color": {"background": "#fef3c7", "border": "#f59e0b"},
            "font": {"color": "#92400e", "size": 11},
            "level": i,
            "title": f"前置: {p.name}",
        })
        edges_data.append({
            "from": p.node_id,
            "to": center_id,
            "color": {"color": "#fbbf24"},
            "width": 2,
        })
    
    # 中心节点
    node_map[center_id] = center
    icon = SUBJECT_ICONS.get(center.subject, "")
    nodes_data.append({
        "id": center_id,
        "label": f"{icon} {center.name}",
        "size": 38,
        "shape": "box",
        "color": {"background": theme["primary"], "border": theme["secondary"]},
        "font": {"color": "#ffffff", "size": 13, "bold": True},
        "margin": 10,
        "shapeProperties": {"borderRadius": 10},
        "level": len(prereqs),
        "title": f"当前: {center.name}",
    })
    
    # 子节点
    for c in children:
        node_map[c.node_id] = c
        items = get_items_for_node(c.node_id)
        nodes_data.append({
            "id": c.node_id,
            "label": c.name,
            "size": 18,
            "shape": "dot",
            "color": {"background": "#a7f3d0", "border": "#10b981"},
            "font": {"color": "#065f46", "size": 10},
            "level": len(prereqs) + 1,
            "title": f"技能: {c.name}<br/>{len(items)} 道题",
        })
        edges_data.append({
            "from": center_id,
            "to": c.node_id,
            "color": {"color": "#34d399"},
            "width": 1,
        })
    
    return nodes_data, edges_data, node_map


def _render_path_graph(nodes_data: list, edges_data: list, height: int = 480) -> str:
    """渲染路径图"""
    nodes_json = json.dumps(nodes_data, ensure_ascii=False)
    edges_json = json.dumps(edges_data, ensure_ascii=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ overflow: hidden; }}
            #graph {{
                width: 100%;
                height: {height}px;
                border-radius: 16px;
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #f0f9ff 100%);
            }}
            .vis-tooltip {{
                background: white !important;
                border-radius: 10px !important;
                padding: 10px 14px !important;
                box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
                max-width: 200px !important;
            }}
            .zoom-controls {{
                position: absolute;
                top: 12px;
                right: 12px;
                display: flex;
                flex-direction: column;
                gap: 6px;
                z-index: 100;
            }}
            .zoom-btn {{
                width: 32px;
                height: 32px;
                border: none;
                border-radius: 8px;
                background: white;
                color: #10b981;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .zoom-btn:hover {{
                background: #10b981;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <div class="zoom-controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">−</button>
            <button class="zoom-btn" onclick="fitAll()" style="font-size:12px;">⟲</button>
        </div>
        <script>
            var nodes = new vis.DataSet({nodes_json});
            var edges = new vis.DataSet({edges_json});
            var container = document.getElementById('graph');
            
            var options = {{
                nodes: {{
                    font: {{ face: 'system-ui, sans-serif', size: 13 }},
                    shadow: true
                }},
                edges: {{
                    smooth: {{ type: 'cubicBezier', roundness: 0.3 }},
                    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }}
                }},
                layout: {{
                    hierarchical: {{
                        enabled: true,
                        direction: 'LR',
                        levelSeparation: 200,
                        nodeSpacing: 100,
                        sortMethod: 'directed'
                    }}
                }},
                physics: false,
                interaction: {{
                    hover: true,
                    tooltipDelay: 100,
                    zoomView: true,
                    dragView: true,
                    zoomSpeed: 0.8,
                    minZoom: 0.6,
                    maxZoom: 2.5
                }}
            }};
            
            var network = new vis.Network(container, {{nodes: nodes, edges: edges}}, options);
            
            function zoomIn() {{ network.moveTo({{ scale: network.getScale() * 1.3, animation: true }}); }}
            function zoomOut() {{ network.moveTo({{ scale: network.getScale() / 1.3, animation: true }}); }}
            function fitAll() {{ network.fit({{ animation: true }}); }}

            var MIN_ZOOM = 0.6;
            var MAX_ZOOM = 2.5;
            network.on('zoom', function() {{
                var s = network.getScale();
                if (s < MIN_ZOOM) {{ network.moveTo({{ scale: MIN_ZOOM }}); }}
                if (s > MAX_ZOOM) {{ network.moveTo({{ scale: MAX_ZOOM }}); }}
            }});

            var isDragging = false;
            network.on('dragStart', function() {{ isDragging = true; }});
            network.on('dragEnd', function() {{ setTimeout(function(){{ isDragging = false; }}, 50); }});
            network.on('click', function(params) {{
                if (isDragging) return;
                if (params.nodes && params.nodes.length > 0) {{
                    var nodeId = params.nodes[0];
                    try {{
                        var url = new URL(window.parent.location.href);
                        url.searchParams.set('kp', nodeId);
                        window.parent.location.href = url.toString();
                    }} catch(e) {{
                        window.parent.location.search = '?kp=' + encodeURIComponent(nodeId);
                    }}
                }}
            }});

            network.on('hoverNode', function() {{ container.style.cursor = 'pointer'; }});
            network.on('blurNode', function() {{ container.style.cursor = 'grab'; }});
        </script>
    </body>
    </html>
    """
    return html


def _render_learning_suggestions(node_id: str) -> None:
    """渲染学习建议"""
    node = get_knowledge_node_by_id(node_id)
    prereqs = get_prereqs(node_id, transitive=False)
    children = get_children(node_id)
    
    st.markdown("### 💡 学习建议")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔸 建议先掌握**")
        if prereqs:
            for p in prereqs[:3]:
                icon = SUBJECT_ICONS.get(p.subject, "📖")
                if st.button(f"{icon} {p.name}", key=f"sug_pre_{p.node_id}", use_container_width=True):
                    go_to_knowledge_detail(p.node_id)
                    st.rerun()
        else:
            st.success("✅ 无前置要求")
    
    with col2:
        st.markdown("**🔹 包含技能点**")
        for c in children[:4]:
            items = get_items_for_node(c.node_id)
            st.markdown(f"• {c.name} `{len(items)}题`")
    
    st.markdown("---")
    if st.button("📚 开始学习", key=f"start_{node_id}", type="primary", use_container_width=True):
        go_to_knowledge_detail(node_id)
        st.rerun()


def _render_transfer_view() -> None:
    """迁移关系视图"""
    
    micro_nodes = get_knowledge_nodes_by_level("micro")
    if len(micro_nodes) < 2:
        st.info("需要至少两个技能点才能进行迁移分析")
        return
    
    st.markdown("""
    <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:12px;padding:1rem;margin-bottom:1rem;">
        <p style="margin:0;font-size:0.9rem;color:#92400e;">
            🔗 选择两个技能点，分析它们之间的迁移关系和共享知识
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 构建选项
    left_options = {f"{SUBJECT_ICONS.get(n.subject, '')} {n.name}": n.node_id for n in micro_nodes}
    left_keys = list(left_options.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔵 技能点 A**")
        left_idx = st.selectbox("选择技能点 A", range(len(left_keys)), 
                                format_func=lambda i: left_keys[i], key="tf_left_idx")
        left_label = left_keys[left_idx] if left_idx is not None else left_keys[0]
        left_id = left_options.get(left_label, "")
    
    with col2:
        st.markdown("**🟠 技能点 B**")
        # 过滤掉已选的 A
        right_nodes = [n for n in micro_nodes if n.node_id != left_id]
        right_options = {f"{SUBJECT_ICONS.get(n.subject, '')} {n.name}": n.node_id for n in right_nodes}
        right_keys = list(right_options.keys())
        
        if not right_keys:
            st.warning("请先选择技能点 A")
            return
        
        right_idx = st.selectbox("选择技能点 B", range(len(right_keys)),
                                 format_func=lambda i: right_keys[i], key="tf_right_idx")
        right_label = right_keys[right_idx] if right_idx is not None else right_keys[0]
        right_id = right_options.get(right_label, "")
    
    if left_id and right_id and left_id != right_id:
        _render_transfer_analysis(left_id, right_id)
    else:
        st.info("请选择两个不同的技能点")


def _render_transfer_analysis(left_id: str, right_id: str) -> None:
    """渲染迁移分析"""
    left = get_knowledge_node_by_id(left_id)
    right = get_knowledge_node_by_id(right_id)
    
    if not left or not right:
        st.error("无法加载技能点信息")
        return
    
    st.markdown("---")
    st.markdown(f"### 📊 迁移分析：{left.name} ↔ {right.name}")
    
    # 计算共享祖先
    left_anc = {a.node_id: a for a in get_ancestors(left_id)}
    right_anc = {a.node_id: a for a in get_ancestors(right_id)}
    shared = [left_anc[sid] for sid in (set(left_anc.keys()) & set(right_anc.keys()))]
    
    left_items = get_items_for_node(left_id)
    right_items = get_items_for_node(right_id)
    
    # 统计卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#dbeafe,#bfdbfe);border-radius:16px;padding:1.25rem;text-align:center;">
            <div style="font-size:2.5rem;font-weight:700;color:#1d4ed8;">{len(left_items)}</div>
            <div style="font-size:0.85rem;color:#3b82f6;">A 关联题目</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        score_color = "#22c55e" if len(shared) >= 2 else ("#f59e0b" if shared else "#ef4444")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f3e8ff,#e9d5ff);border-radius:16px;padding:1.25rem;text-align:center;">
            <div style="font-size:2.5rem;font-weight:700;color:{score_color};">{len(shared)}</div>
            <div style="font-size:0.85rem;color:#7c3aed;">共享知识</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ffedd5,#fed7aa);border-radius:16px;padding:1.25rem;text-align:center;">
            <div style="font-size:2.5rem;font-weight:700;color:#ea580c;">{len(right_items)}</div>
            <div style="font-size:0.85rem;color:#f97316;">B 关联题目</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 迁移建议
    if shared:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f5f3ff,#ede9fe);border-left:4px solid #8b5cf6;padding:1rem;border-radius:0 12px 12px 0;margin:1rem 0;">
            <strong style="color:#6d28d9;">💡 迁移建议</strong>
            <p style="margin:0.5rem 0 0 0;color:#64748b;">
                这两个技能通过「{shared[0].name}」关联，学习一个可帮助理解另一个。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 练习推荐
    st.markdown("### 🎯 迁移练习")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.markdown(f"**{left.name}**")
        for item_id, domain in left_items[:2]:
            item = _get_item_by_domain(item_id, domain)
            if item:
                if st.button(f"📝 {item.title}", key=f"tfl_{item_id}", use_container_width=True):
                    go_to_problem(domain, item_id)
                    st.rerun()
    
    with col_r:
        st.markdown(f"**{right.name}**")
        for item_id, domain in right_items[:2]:
            item = _get_item_by_domain(item_id, domain)
            if item:
                if st.button(f"📝 {item.title}", key=f"tfr_{item_id}", use_container_width=True):
                    go_to_problem(domain, item_id)
                    st.rerun()


def _get_item_by_domain(item_id: str, domain: str):
    """获取题目"""
    from problems.coding.loader import get_coding_item_by_id
    from problems.math.loader import get_math_item_by_id
    from problems.deeplearning.loader import get_dl_item_by_id
    
    if domain == "coding":
        return get_coding_item_by_id(item_id)
    elif domain == "math":
        return get_math_item_by_id(item_id)
    return get_dl_item_by_id(item_id)
