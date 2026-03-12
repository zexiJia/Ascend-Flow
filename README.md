# Ascend-Flow 智流

<div align="center">

### A multi-agent adaptive learning system that keeps learners in flow

**Plan** • **Teach** • **Scaffold** • **Motivate**  
From **understanding** to **solving** for **coding interviews** and **foundational math**

</div>

---

## Overview

**Ascend-Flow (智流)** is a **multi-agent learning system** designed to bridge the gap between *“I understand it”* and *“I can actually solve it.”*

Rather than acting as a generic chatbot, Ascend-Flow coordinates multiple specialized LLM tutors that collaboratively:

- plan learning paths
- explain concepts intuitively
- generate scaffolded practice
- regulate challenge and motivation
- adapt to each learner’s evolving state

Our goal is to create a learning experience that feels as smooth and engaging as short-form content, while delivering real mastery in:

- **coding interviews**
- **foundational mathematics**
- **AI prerequisite learning**

---

## Why Ascend-Flow?

Many learners get stuck in **tutorial hell**:

- they can follow explanations
- they can recognize solutions
- but they cannot solve problems independently

Ascend-Flow is built to **bridge that gap**.

Instead of stopping at explanation, the system actively guides learners through a progression:

1. **Understand the concept**
2. **Practice with support**
3. **Solve with hints**
4. **Transfer to harder variants**
5. **Consolidate into reusable intuition**

This turns passive familiarity into active problem-solving ability.

---

## Core Idea

Ascend-Flow is not a single assistant. It is a **multi-agent teaching system**.

Each agent plays a distinct educational role:

### Agent A — The Architect
Responsible for **long-term planning and memory**.

- tracks learner history
- models forgetting and retention
- plans daily learning paths
- aligns content with long-term goals

Example:  
> “Based on yesterday’s performance, today we will focus on dynamic programming and review matrix eigenvalues.”

---

### Agent B — The Feynman Tutor
Responsible for **teaching and explanation**.

Its goal is not to restate definitions, but to explain ideas with:

- intuition
- analogy
- visual reasoning
- multiple explanation styles

If the learner says “I still don’t get it,” the tutor can immediately switch perspectives—for example, from a formal explanation to a physical, geometric, or economic analogy.

---

### Agent C — The Examiner
Responsible for **practice generation**.

Instead of merely retrieving existing problems, this agent can:

- rewrite problems
- adjust parameters
- create variants
- generate scaffolded exercises
- raise or lower difficulty on demand

This allows practice to be matched precisely to the learner’s current state.

---

### Agent D — The Motivator
Responsible for **frustration monitoring and flow regulation**.

It watches signals such as:

- time spent
- retry count
- hint dependence
- repeated failure patterns

If the task is too hard, it reduces difficulty and offers encouragement.  
If the task is too easy, it increases challenge to keep the learner in the **flow zone**.

---

## Product Experience

Ascend-Flow is designed to feel less like a static course and more like an intelligent learning loop.

### 1. Daily Drop
The learner opens the app and sees only **today’s mission**, not an overwhelming curriculum tree.

Example:
> “Good morning, Alex. Today we’ll tackle the hardest part of dynamic programming and review matrix eigenvalues.”

This reduces friction and eliminates choice overload.

---

### 2. Interactive Concept Check
Concepts are taught interactively rather than dumped as long text blocks.

For example, when learning **gradient descent**, the tutor may start with a “walking downhill” metaphor, then ask a simple question to confirm understanding.

If the learner is confused, the explanation changes immediately.

---

### 3. Scaffolded Practice
This is the core learning engine.

#### Level 1 — Understanding
Cloze-style exercises, guided steps, fill-in-the-blank code or formulas.

#### Level 2 — Application
Canonical problems with intelligent hints instead of direct answers.

#### Level 3 — Challenge
Generated variants that test true mastery.

Example:
> “What changes if the array is no longer sorted?”

This is where recognition becomes real transfer.

---

### 4. The Crystal
At the end of a session, the system automatically generates a compact **knowledge crystal**:

- core takeaways
- common mistakes
- key formulas or invariants
- personalized weak points

This gives learners something to retain, revisit, and share.

---

## What Makes It Different?

### 1. From Explanation to Mastery
Most tools are good at explaining.  
Few are good at helping learners cross the final mile from **knowing** to **solving**.

Ascend-Flow focuses on that transition.

---

### 2. Semantic Personalization
Traditional adaptive learning is rule-based, expensive, and brittle.

Ascend-Flow uses LLM-based adaptation at the **semantic level**, allowing it to respond not just to *what* the learner got wrong, but to *why* they got stuck.

---

### 3. Flow-State Optimization
The system aims to keep learners in a state of productive challenge:

- not overwhelmed
- not bored
- continuously progressing

This is where motivation, learning gain, and retention compound.

---

## System Architecture

Ascend-Flow combines three major layers:

### Knowledge Layer
A structured **knowledge graph** connecting concepts, skills, and representations across math, coding, and AI foundations.

### Pedagogy Layer
A multi-agent orchestration system that decides:

- what to teach next
- how to explain it
- when to review
- how to generate the right next exercise

### Verification Layer
Step-level checking and process-aware feedback, so the learner can be told exactly **which reasoning step failed**, not just whether the final answer was wrong.

---

## Knowledge Graph Design

The knowledge graph is designed around **learning transfer**, not encyclopedic relation storage.

### Node Types

#### Concept
Definitions, theorems, and formal ideas  
Examples: Bayes’ rule, gradient, binary search invariant

#### Skill
Executable abilities  
Examples: writing a correct lower-bound binary search, computing a Jacobian, tracing gradients on a graph

#### Representation
Reusable mental models and forms  
Examples: DAGs, state transition diagrams, geometric intuitions

---

### Relation Types

The graph focuses on relations that matter for learning:

- **Prerequisite** — A must be learned before B
- **Transfer** — Learning A makes B easier
- **Analogy** — A and B share the same intuition
- **Shared Representation** — the same structure explains both
- **Application** — A is used inside B
- **Contrast** — differentiating A and B reduces confusion

This makes the graph a **learning transfer network**, not just a knowledge database.

---

## Learning Engine

Ascend-Flow treats learning as a sequential decision problem.

At each step, the system decides:

- what concept to review
- what explanation style to use
- what exercise to generate
- what hint to provide
- when to raise or lower difficulty

The objective is to maximize:

- **learning gain**
- **transfer gain**
- **retention**
- **engagement**
- while minimizing frustration and wasted effort

---

## Technical Directions

Ascend-Flow is built around several core research ideas.

### Flow Control via Multi-Objective RL
The learner trajectory can be modeled as a decision process where the system chooses the next best action to maintain flow and maximize mastery.

Potential signals include:

- correctness
- response time
- hint usage
- revision behavior
- persistence

---

### GraphRAG for Logical Alignment
Instead of retrieving isolated chunks, explanations are constrained by a structured semantic graph.

This helps:

- identify prerequisite gaps
- retrieve the right conceptual anchors
- reduce hallucinations
- ensure mathematical and coding explanations remain logically traceable

---

### Process Reward Models
We care about *how* a learner solves a problem, not just the final answer.

This enables:

- step-by-step validation
- precise diagnosis
- targeted feedback
- lower frustration during problem solving

---

### Synthetic Data Flywheel
Generated problem variants, error patterns, and misconception clusters can be used to continuously improve the teaching system.

Over time, this creates compounding assets such as:

- misconception libraries
- personalized explanation preferences
- high-performing hint templates
- “aha moment” patterns

The more the system is used, the better it becomes at teaching.

---

## Knowledge and Item Design

Ascend-Flow uses a layered curriculum representation.

### Layer 1 — Macro
High-level map for navigation and planning  
Examples: Search & Binary Search, Linear Algebra Basics, Backpropagation

### Layer 2 — Meso
Subtopics used for weekly planning and training scripts  
Examples: binary search templates and invariants, vector chain rule

### Layer 3 — Micro
Smallest assessable units of mastery  
Examples: choosing binary search boundaries, applying chain rule correctly, tracing gradients through a graph

### Layer 4 — Item
Concrete exercises used for training and evaluation

Each item links directly to the relevant micro-skills, making practice generation and mastery diagnosis precise and scalable.

---

## Use Cases

Ascend-Flow is especially suited for:

- **coding interview preparation**
- **calculus, linear algebra, and probability learning**
- **AI/math prerequisites**
- **adaptive problem-solving practice**
- **personalized educational copilots**
- **flow-based tutoring systems**
- **research on intelligent tutoring and multi-agent learning**

---

## Vision

We believe the future of education is not a larger content library.

It is a system that can:

- understand what a learner knows
- detect where they are stuck
- choose the next best step
- explain in the right way
- generate the right challenge
- keep them moving in flow

**Ascend-Flow** is our step toward that future.

---

## Roadmap

- [ ] Knowledge graph schema for math / coding / DL fundamentals
- [ ] Multi-agent orchestration for planner / tutor / examiner / motivator
- [ ] Scaffolded problem generation pipeline
- [ ] Step-level grading and feedback engine
- [ ] Personalized learner state tracking
- [ ] Graph-based retrieval and prerequisite tracing
- [ ] Flow-aware difficulty control
- [ ] Knowledge crystal generation

---

## Project Status

Ascend-Flow is an active open-source research and product exploration project.  
The repository will gradually include:

- system design
- curriculum schemas
- item generation pipelines
- agent orchestration logic
- evaluation tools
- demo experiences

---

## Contributing

Contributions, ideas, and discussions are welcome.

If you are interested in:

- AI for education
- multi-agent systems
- adaptive learning
- intelligent tutoring
- knowledge graphs
- process supervision

please feel free to open an issue or start a discussion.

---

## License

To be added.

---

## Name

**Ascend-Flow (智流)**

- **Ascend**: continuous growth toward mastery
- **Flow**: the optimal state between boredom and frustration
- **智流**: a stream of intelligence and learning momentum
