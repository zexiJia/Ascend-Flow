# filename: frontend/components/ai_chat.py
"""AI 教师对话组件 - 可在题目和知识点页面复用"""

from __future__ import annotations

from typing import List, Dict, Any
import streamlit as st

from services.ai_grader import AI_ENABLED


def _get_chat_key(context_type: str, context_id: str) -> str:
    """生成对话历史的 session_state 键"""
    return f"ai_chat_{context_type}_{context_id}"


def _get_initial_explanation(context_type: str, context_data: Dict[str, Any]) -> str:
    """根据上下文生成初始讲解的 prompt"""
    if context_type == "problem":
        domain = context_data.get("domain", "")
        title = context_data.get("title", "")
        prompt_text = context_data.get("prompt", "")
        difficulty = context_data.get("difficulty", "")
        explanation = context_data.get("explanation", "")
        
        return f"""你是一位经验丰富的AI教师，正在教授学生解决以下{domain}问题。

【题目】{title}
【难度】{difficulty}
【题目描述】{prompt_text}

{f"【已有讲解】{explanation}" if explanation else ""}

请用中文为学生提供一个清晰、生动的讲解，包括：
1. 🎯 **核心考点**：这道题考察什么知识点？
2. 💡 **解题思路**：如何分析和思考这道题？
3. 📝 **关键步骤**：解题的核心步骤是什么？
4. ⚠️ **易错点**：有哪些常见的错误需要避免？
5. 🔗 **拓展思考**：这道题和哪些知识点有联系？

请用通俗易懂的语言，适当使用类比和例子，让学生容易理解。"""

    elif context_type == "knowledge":
        name = context_data.get("name", "")
        level = context_data.get("level", "")
        subject = context_data.get("subject", "")
        summary = context_data.get("summary", "")
        
        level_name = {"macro": "一级知识点", "meso": "二级知识点", "micro": "三级技能点"}.get(level, "知识点")
        subject_name = {"math": "数学", "coding": "编程", "deeplearning": "深度学习"}.get(subject, "")
        
        return f"""你是一位经验丰富的AI教师，正在为学生讲解以下{subject_name}知识点。

【知识点】{name}
【类型】{level_name}
【概述】{summary}

请用中文为学生提供一个系统、生动的讲解，包括：
1. 📚 **核心概念**：这个知识点的核心内容是什么？
2. 🎯 **学习目标**：学完这个知识点应该掌握什么？
3. 💡 **关键要点**：有哪些需要重点理解的内容？
4. 📝 **实际应用**：这个知识点在实际中如何应用？
5. 🔗 **知识关联**：它与其他知识点有什么联系？
6. ⚠️ **常见误区**：学习时容易出现什么误解？

请用通俗易懂的语言，适当使用类比和具体例子，让学生容易理解和记忆。"""

    return "请介绍这个内容"


def _call_ai(prompt: str) -> str:
    """调用 AI 获取回复 - 使用现有的 agent_call 接口"""
    if not AI_ENABLED:
        return "⚠️ 未配置 AI（需要设置 ICHAT_APPID/ICHAT_APPKEY/ICHAT_SOURCE 环境变量）"
    
    try:
        from agents.gpt_client import ichat_chat_completions
        
        text, _ = ichat_chat_completions(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.6,
        )
        return (text or "").strip() or "❌ AI 未返回内容"
    except Exception as e:
        return f"❌ AI 调用失败: {str(e)}"


def _call_ai_chat(messages: List[Dict[str, str]]) -> str:
    """调用 AI 进行多轮对话"""
    if not AI_ENABLED:
        return "⚠️ 未配置 AI（需要设置 ICHAT_APPID/ICHAT_APPKEY/ICHAT_SOURCE 环境变量）"
    
    try:
        from agents.gpt_client import ichat_chat_completions
        
        text, _ = ichat_chat_completions(
            messages=messages,
            max_tokens=1200,
            temperature=0.6,
        )
        return (text or "").strip() or "❌ AI 未返回内容"
    except Exception as e:
        return f"❌ AI 调用失败: {str(e)}"


def render_ai_teacher_chat(
    context_type: str,
    context_id: str,
    context_data: Dict[str, Any],
    key_prefix: str = "",
) -> None:
    """
    渲染 AI 教师对话组件
    
    Args:
        context_type: 上下文类型 ("problem" 或 "knowledge")
        context_id: 上下文 ID (题目 ID 或知识点 ID)
        context_data: 上下文数据 (题目或知识点信息)
        key_prefix: 组件 key 前缀，用于避免重复
    """
    
    chat_key = _get_chat_key(context_type, context_id)
    
    # 初始化对话历史
    if chat_key not in st.session_state:
        st.session_state[chat_key] = {
            "messages": [],  # 对话历史
            "started": False,  # 是否已开始对话
            "loading": False,  # 是否正在加载
        }
    
    chat_state = st.session_state[chat_key]
    
    st.markdown("---")
    st.markdown("### 🤖 AI 教师")
    
    if not AI_ENABLED:
        st.warning("💡 AI 功能需要配置环境变量才能使用")
        return
    
    # 开始对话按钮
    if not chat_state["started"]:
        st.markdown("有疑问？点击下方按钮，AI教师会先为你讲解，然后你可以继续提问。")
        
        if st.button("🙋 询问AI老师", key=f"{key_prefix}start_ai_chat_{context_id}", use_container_width=True):
            chat_state["started"] = True
            chat_state["loading"] = True
            st.rerun()
    
    # 对话进行中
    if chat_state["started"]:
        # 首次加载，生成初始讲解
        if chat_state["loading"] and len(chat_state["messages"]) == 0:
            with st.spinner("🤔 AI老师正在准备讲解..."):
                user_prompt = _get_initial_explanation(context_type, context_data)
                
                # 使用单轮调用获取初始讲解
                response = _call_ai(user_prompt)
                
                chat_state["messages"] = [
                    {"role": "assistant", "content": response}
                ]
                chat_state["loading"] = False
                st.rerun()
        
        # 显示对话历史
        for i, msg in enumerate(chat_state["messages"]):
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border-radius:12px;padding:1rem;margin-bottom:0.75rem;border-left:4px solid #3b82f6;">
                    <div style="font-weight:600;color:#1e40af;margin-bottom:0.5rem;">🤖 AI老师</div>
                    <div style="color:#1f2937;line-height:1.7;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#f3f4f6;border-radius:12px;padding:1rem;margin-bottom:0.75rem;border-left:4px solid #6b7280;">
                    <div style="font-weight:600;color:#374151;margin-bottom:0.5rem;">👤 你</div>
                    <div style="color:#1f2937;">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # 输入新问题
        st.markdown("---")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "继续提问...",
                key=f"{key_prefix}ai_input_{context_id}",
                placeholder="例如：能再详细解释一下吗？/ 有没有类似的例子？",
                label_visibility="collapsed",
            )
        
        with col2:
            send_clicked = st.button("发送", key=f"{key_prefix}ai_send_{context_id}", use_container_width=True)
        
        if send_clicked and user_input.strip():
            chat_state["loading"] = True
            
            # 构建完整对话历史
            system_prompt = "你是一位友善、专业的AI教师。请用中文简洁地回答学生的问题。"
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加上下文
            context_intro = _get_initial_explanation(context_type, context_data)
            messages.append({"role": "user", "content": f"[背景信息]\n{context_intro}"})
            messages.append({"role": "assistant", "content": chat_state["messages"][0]["content"] if chat_state["messages"] else "好的，我来帮你讲解。"})
            
            # 添加历史对话（最近4轮）
            for msg in chat_state["messages"][-8:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 添加新问题
            messages.append({"role": "user", "content": user_input.strip()})
            
            with st.spinner("🤔 思考中..."):
                response = _call_ai_chat(messages)
            
            # 更新对话历史
            chat_state["messages"].append({"role": "user", "content": user_input.strip()})
            chat_state["messages"].append({"role": "assistant", "content": response})
            chat_state["loading"] = False
            
            st.rerun()
        
        # 重置对话按钮
        if len(chat_state["messages"]) > 1:
            if st.button("🔄 重新开始对话", key=f"{key_prefix}ai_reset_{context_id}"):
                st.session_state[chat_key] = {
                    "messages": [],
                    "started": False,
                    "loading": False,
                }
                st.rerun()

