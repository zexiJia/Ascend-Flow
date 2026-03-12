<div align="center">

<img src="https://img.shields.io/badge/%E6%99%BA%E6%B5%81-Ascend--Flow-blueviolet?style=for-the-badge&logoColor=white" alt="Ascend-Flow" height="40"/>

<br/>
<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=4000&pause=1000&color=8B5CF6&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=80&lines=A+Multi-Agent+Adaptive+Learning+System;That+Keeps+Learners+in+Flow+%F0%9F%8C%8A" alt="Typing SVG" />

<br/>

**Plan** · **Teach** · **Scaffold** · **Motivate**

From **understanding** to **solving** — for **coding interviews** and **foundational math**

<br/>

<img src="https://img.shields.io/badge/status-active_development-brightgreen?style=flat-square"/>
<img src="https://img.shields.io/badge/agents-multi--agent_system-blueviolet?style=flat-square"/>
<img src="https://img.shields.io/badge/domain-AI_for_Education-orange?style=flat-square"/>
<img src="https://img.shields.io/badge/PRs-welcome-ff69b4?style=flat-square"/>

</div>

---

## 🌊 Overview

**Ascend-Flow (智流)** is a multi-agent learning system designed to bridge the gap between *"I understand it"* and *"I can actually solve it."*

Rather than acting as a generic chatbot, Ascend-Flow coordinates multiple specialized LLM tutors that collaboratively plan learning paths, explain concepts intuitively, generate scaffolded practice, regulate challenge and motivation, and adapt to each learner's evolving state.

Our goal is to create a learning experience that delivers real mastery in:

- 💻 **Coding interviews** — LeetCode, algorithms, system design
- 📐 **Foundational mathematics** — calculus, linear algebra, probability
- 🤖 **AI prerequisite learning** — backprop, optimization, statistics

---

## 🤔 Why Ascend-Flow?

Many learners get stuck in **tutorial hell** — they can follow explanations and recognize solutions, but cannot solve problems independently.

Ascend-Flow is built to bridge that gap. Instead of stopping at explanation, the system guides learners through a mastery progression:

1. 🟢 **Understand** the concept
2. 🔵 **Practice** with support
3. 🟡 **Solve** with hints
4. 🟠 **Transfer** to harder variants
5. 🔴 **Consolidate** into reusable intuition

This turns passive familiarity into active problem-solving ability.

---

## 🧠 Core Idea — Multi-Agent Teaching

Ascend-Flow is not a single assistant. It is a multi-agent teaching system. Each agent plays a distinct educational role:

### 🏗️ Agent A — The Architect
Responsible for **long-term planning and memory**. Tracks learner history, models forgetting and retention, plans daily learning paths, and aligns content with long-term goals.

### 🎓 Agent B — The Feynman Tutor
Responsible for **teaching and explanation**. Explains ideas through intuition, analogy, and visual reasoning. If the learner is confused, it immediately switches perspectives — from formal proof to geometric intuition to economic analogy.

### 📝 Agent C — The Examiner
Responsible for **practice generation**. Rewrites problems, adjusts difficulty, creates variants, and generates scaffolded exercises matched precisely to the learner's current state.

### 💪 Agent D — The Motivator
Responsible for **frustration monitoring and flow regulation**. Watches signals like time spent, retry count, and hint dependence. Reduces difficulty when overwhelmed, increases challenge when bored — keeping the learner in the flow zone.

---

## 🎮 Product Experience

### 1️⃣ Daily Drop
The learner opens the app and sees only **today's mission**, not an overwhelming curriculum tree. This reduces friction and eliminates choice overload.

### 2️⃣ Interactive Concept Check
Concepts are taught interactively. For example, gradient descent starts with a "walking downhill" metaphor, then asks a question to confirm understanding. If confused, the explanation changes immediately.

### 3️⃣ Scaffolded Practice
The core learning engine with three levels:
- **Level 1 — Understanding**: cloze-style exercises, guided steps, fill-in-the-blank
- **Level 2 — Application**: canonical problems with intelligent hints
- **Level 3 — Challenge**: generated variants that test true mastery

### 4️⃣ The Crystal 💎
At the end of a session, the system generates a compact knowledge crystal: core takeaways, common mistakes, key formulas, and personalized weak points.

---

## ✨ What Makes It Different?

**🎯 From Explanation to Mastery** — Most tools are good at explaining. Few help learners cross the final mile from knowing to solving. Ascend-Flow focuses on that transition.

**🧬 Semantic Personalization** — Traditional adaptive learning is rule-based and brittle. Ascend-Flow uses LLM-based adaptation at the semantic level, responding not just to what went wrong, but why.

**🌊 Flow-State Optimization** — The system keeps learners not overwhelmed, not bored, and continuously progressing. This is where motivation, learning gain, and retention compound.

---

## 🏛️ System Architecture

Ascend-Flow combines three major layers:

- 📚 **Knowledge Layer** — A structured knowledge graph connecting concepts, skills, and representations across math, coding, and AI foundations.
- 🎓 **Pedagogy Layer** — A multi-agent orchestration system that decides what to teach, how to explain, when to review, and what exercise to generate.
- 🔍 **Verification Layer** — Step-level checking and process-aware feedback, telling learners exactly which reasoning step failed.

---

## 🕸️ Knowledge Graph Design

The knowledge graph is designed around **learning transfer**, not encyclopedic relation storage.

**Node Types:**
- 📘 **Concept** — definitions, theorems, formal ideas (e.g., Bayes' rule, gradient, binary search invariant)
- ⚡ **Skill** — executable abilities (e.g., writing correct binary search, computing a Jacobian)
- 🔮 **Representation** — reusable mental models (e.g., DAGs, state transition diagrams, geometric intuitions)

**Relation Types:**
- **Prerequisite** — A must be learned before B
- **Transfer** — learning A makes B easier
- **Analogy** — A and B share the same intuition
- **Shared Representation** — same structure explains both
- **Application** — A is used inside B
- **Contrast** — differentiating A and B reduces confusion

This makes the graph a learning transfer network, not just a knowledge database.

---

## ⚙️ Learning Engine

Ascend-Flow treats learning as a sequential decision problem. At each step, the system decides what concept to review, what explanation style to use, what exercise to generate, what hint to provide, and when to raise or lower difficulty.

The objective is to maximize learning gain, transfer gain, retention, and engagement — while minimizing frustration and wasted effort.

---

## 🔬 Technical Directions

**🎮 Flow Control via Multi-Objective RL** — The learner trajectory is modeled as a decision process. Signals include correctness, response time, hint usage, revision behavior, and persistence.

**🕸️ GraphRAG for Logical Alignment** — Explanations are constrained by a structured semantic graph to identify prerequisite gaps, reduce hallucinations, and ensure logically traceable explanations.

**✅ Process Reward Models** — Step-by-step validation enables precise diagnosis and targeted feedback, not just final-answer checking.

**♻️ Synthetic Data Flywheel** — Generated problem variants, error patterns, and misconception clusters continuously improve the system. The more it is used, the better it becomes at teaching.

---

## 📚 Knowledge & Item Design

Ascend-Flow uses a layered curriculum representation:

- 🔴 **Macro** — high-level map for navigation and planning (e.g., Binary Search, Linear Algebra Basics)
- 🟠 **Meso** — subtopics for weekly planning (e.g., binary search templates, vector chain rule)
- 🟡 **Micro** — smallest assessable units of mastery (e.g., choosing binary search boundaries)
- 🟢 **Item** — concrete exercises linked directly to micro-skills

---

## 🎯 Use Cases

- Coding interview preparation
- Calculus, linear algebra, and probability learning
- AI / math prerequisites
- Adaptive problem-solving practice
- Personalized educational copilots
- Flow-based tutoring systems
- Research on intelligent tutoring and multi-agent learning

---

## 🔭 Vision

We believe the future of education is not a larger content library. It is a system that can understand what a learner knows, detect where they are stuck, choose the next best step, explain in the right way, generate the right challenge, and keep them moving in flow.

**Ascend-Flow** is our step toward that future.

---

## 🗺️ Roadmap

- [ ] Knowledge graph schema for math / coding / DL fundamentals
- [ ] Multi-agent orchestration for planner / tutor / examiner / motivator
- [ ] Scaffolded problem generation pipeline
- [ ] Step-level grading and feedback engine
- [ ] Personalized learner state tracking
- [ ] Graph-based retrieval and prerequisite tracing
- [ ] Flow-aware difficulty control
- [ ] Knowledge crystal generation

---

## 📦 Project Status

Ascend-Flow is an active open-source research and product exploration project. The repository will gradually include system design, curriculum schemas, item generation pipelines, agent orchestration logic, evaluation tools, and demo experiences.

---

## 🤝 Contributing

Contributions, ideas, and discussions are welcome. If you are interested in AI for education, multi-agent systems, adaptive learning, intelligent tutoring, knowledge graphs, or process supervision — please feel free to open an issue or start a discussion.

---

## 📄 License

To be added.

---

<div align="center">

<br/>

### 🌊 Ascend-Flow · 智流

**Ascend** — continuous growth toward mastery  
**Flow** — the optimal state between boredom and frustration  
**智流** — a stream of intelligence and learning momentum

<sub>Built with ❤️ for learners who refuse to stay stuck.</sub>

<br/>

</div>
