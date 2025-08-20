下面给你一个**可直接落地的骨架方案**，包含四部分：

✅ **工具路由模块（RAG Router + 规则兜底）**
✅ **自我反思模块（Reflexion 风格，JSON 输出）**
✅ **知识库结构（短期 + 向量 + 关系型日志）**
✅ **宏工具封装模板**

我会用 **Python + LangChain / LangGraph 风格**，确保你能插到现有 Agent 框架中。

---

## 1. **工具路由模块**（RAG + 规则兜底）

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

# 假设 tools_index 是一个 FAISS 索引，每个工具有描述和示例
embeddings = OpenAIEmbeddings()
vector_store = FAISS.load_local("tools_index", embeddings)

# 规则兜底
def rule_based_fallback(query, tools):
    for t in tools:
        if any(keyword in query.lower() for keyword in t["keywords"]):
            return t
    return None

def rag_router(query):
    # 检索 top-3 工具
    docs = vector_store.similarity_search(query, k=3)
    tool_cards = "\n\n".join([f"{d.metadata['name']}: {d.page_content}" for d in docs])

    template = """
    You are a Tool Router.
    User task: {query}
    Candidate tools:
    {tool_cards}

    Decide:
    1) Should a tool be used? (yes/no)
    2) If yes, which tool? Give name.
    3) Draft input parameters.
    Return JSON: {{"use_tool":true/false,"tool_name":"","params":{{}}}}
    """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0)
    return llm(prompt.format(query=query, tool_cards=tool_cards))
```

> **升级点**：可以把 `docs` + query + 环境信号做排序，或者训练轻监督分类模型替换 LLM 决策。

---

## 2. **自我反思模块（JSON 输出）**

```python
from langchain.prompts import ChatPromptTemplate

reflection_template = """
You are the Self-Reflection module.
Given:
- GOAL: {goal}
- PLAN: {plan}
- ACTION TRACE: {trace}
- OUTCOME: {outcome}

Analyze and return JSON:
{{
 "what_went_wrong": ["..."],
 "why": ["..."],
 "fix_next_time": ["..."],
 "tool_insights": ["..."]
}}
"""

def generate_reflection(goal, plan, trace, outcome):
    prompt = ChatPromptTemplate.from_template(reflection_template)
    llm = ChatOpenAI(temperature=0)
    return llm.predict(goal=goal, plan=plan, trace=trace, outcome=outcome)
```

> 输出 JSON 存入 **短期记忆 + 向量知识库**，方便后续检索。

---

## 3. **知识库结构（短期 / 向量 / 关系型日志）**

* **短期缓冲**（Python dict 或 Redis LRU）：

```python
episodic_buffer = []  # [{"task_id":..., "reflection":..., "timestamp":...}]
```

* **向量知识库**（FAISS / PGVector）：

```python
# 每条 reflection['tool_insights'] / ['fix_next_time'] 作为 chunk，embedding 入库
vector_store.add_texts(["Always validate JSON before API call", ...])
```

* **关系型日志（SQL 示例）**：

```sql
CREATE TABLE tool_invocations (
    id SERIAL PRIMARY KEY,
    task_id TEXT,
    tool_name TEXT,
    args_hash TEXT,
    success BOOLEAN,
    latency_ms INT,
    err_type TEXT,
    output_schema_digest TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

> 这些日志可以用于挖掘高频调用链、训练轻监督路由模型，或生成 **Tool Tips**。

---

## 4. **宏工具封装模板（频繁调用链 → 内生工具）**

```python
class MacroTool:
    def __init__(self, name, steps):
        """
        steps: list of {"tool":..., "params_template":...}
        """
        self.name = name
        self.steps = steps

    def run(self, context):
        results = []
        for step in self.steps:
            tool = get_tool(step["tool"])
            params = {k: context.get(k, v) for k, v in step["params_template"].items()}
            res = tool.execute(params)
            results.append(res)
        return results[-1]  # 最终输出
```

* **触发封装条件**：日志挖掘发现\*\*≥N 次重复调用链 + 90% 成功率\*\*，自动产出 `steps`。
* **优势**：减少推理回合，提高稳定性。

---

✅ **闭环工作流**：

* `rag_router()` 选工具 → 执行 → `generate_reflection()` → 写入 KB（短期+向量+关系型） → 检索注入下一任务 → 高频调用链自动生成宏工具。

---

需要的话，我可以帮你做两件事：
**① 提供一整套 LangGraph 节点图（Tool Router、Reflection、KB Write、KB Retrieve、MacroTool Runner），用 Python 代码实现**。
**② 再加一个强化学习（ReTool 风格）的路由优化模块**，让系统学“何时调用”工具，而不是每次都问 LLM。

要我先写 **LangGraph 节点版实现**，还是先加 **ReTool 风格的 RL 优化路由**？


```
"""
LangGraph Agent: Tool Meta-Learning Stack (Nodes + RL Router)
-----------------------------------------------------------------
This single-file reference implements:

1) LangGraph-style nodes and wiring for a tool-using agent with
   - Tool Router (RAG + rule fallback)
   - Tool Executor
   - Self-Reflection (Reflexion-style JSON)
   - KB Write (episodic buffer + vector KB + SQL logs)
   - KB Retrieve (inject Tool Tips / Heuristics)
   - MacroTool Runner (auto-encapsulated chains)
   - Answer Check (final self-verification)

2) ReTool-style RL optimization for routing decisions
   - Contextual bandit (LinUCB) policy for "use tool? which tool?"
   - Online updates from execution logs with reward = f(success, latency, cost)

Notes
-----
- You can replace the minimal vector store with FAISS/PGVector and the SQL with your DB.
- The LLM calls are abstracted; plug your provider (OpenAI/Anthropic/etc.).
- This file is meant as a skeleton with production-ready interfaces and docstrings.

Dependencies (suggested)
------------------------
- langgraph>=0.2.*  (optional; here we provide a minimal Graph class if missing)
- pydantic, numpy, scikit-learn (optional), sqlite3 (std lib)

"""
from __future__ import annotations
import os
import time
import json
import math
import uuid
import sqlite3
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable

# -----------------------------
# Utils
# -----------------------------

def now_ms() -> int:
    return int(time.time() * 1000)


def sha1(obj: Any) -> str:
    return hashlib.sha1(json.dumps(obj, sort_keys=True).encode("utf-8")).hexdigest()


# -----------------------------
# Minimal LLM adapter (replace with your provider)
# -----------------------------
class LLM:
    """Very small adapter. Replace with your actual LLM call.
    Implement .complete(system, user) -> str
    """

    def __init__(self, model: str = "gpt-5"):
        self.model = model

    def complete(self, system: str, user: str) -> str:
        # TODO: integrate provider SDK; here we return a stub to keep file runnable
        return "{}"  # return empty JSON by default to avoid crashes


# -----------------------------
# In-memory Vector Store (replace with FAISS/PGVector)
# -----------------------------
class SimpleEmbedder:
    def embed(self, text: str) -> List[float]:
        # Toy embedding: bag-of-chars frequency; replace with real embeddings
        vec = [0]*64
        for ch in text.lower():
            vec[hash(ch) % 64] += 1
        n = sum(vec) or 1
        return [v/n for v in vec]


def cosine(a: List[float], b: List[float]) -> float:
    num = sum(x*y for x, y in zip(a, b))
    da = math.sqrt(sum(x*x for x in a))
    db = math.sqrt(sum(y*y for y in b))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


class SimpleVectorStore:
    def __init__(self, embedder: SimpleEmbedder):
        self.embedder = embedder
        self.rows: List[Tuple[str, List[float], Dict[str, Any]]] = []

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None):
        metadatas = metadatas or [{} for _ in texts]
        for t, m in zip(texts, metadatas):
            self.rows.append((t, self.embedder.embed(t), m))

    def search(self, q: str, k: int = 3, filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None):
        qv = self.embedder.embed(q)
        scored = []
        for text, vec, meta in self.rows:
            if filter_fn and not filter_fn(meta):
                continue
            scored.append((cosine(qv, vec), text, meta))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]


# -----------------------------
# Tool schema & registry
# -----------------------------
@dataclass
class Tool:
    name: str
    description: str
    keywords: List[str]
    cost: float = 0.0  # credits per call (optional)
    latency_hint_ms: int = 200
    examples: List[Dict[str, Any]] = field(default_factory=list)
    run: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda args: {"ok": True}


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self.tools[name]

    def all(self) -> List[Tool]:
        return list(self.tools.values())


# -----------------------------
# SQL Log Store (SQLite for demo)
# -----------------------------
class SQLLog:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                tool_name TEXT,
                args_hash TEXT,
                success INTEGER,
                latency_ms INTEGER,
                err_type TEXT,
                reward REAL,
                output_schema_digest TEXT,
                created_at INTEGER
            )
            """
        )
        self.conn.commit()

    def log(self, row: Dict[str, Any]):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO tool_invocations(task_id, tool_name, args_hash, success, latency_ms, err_type, reward, output_schema_digest, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("task_id"),
                row.get("tool_name"),
                row.get("args_hash"),
                1 if row.get("success") else 0,
                row.get("latency_ms", 0),
                row.get("err_type"),
                row.get("reward", 0.0),
                row.get("output_schema_digest"),
                now_ms(),
            ),
        )
        self.conn.commit()

    def recent(self, limit: int = 500) -> List[Tuple[Any, ...]]:
        cur = self.conn.cursor()
        cur.execute("SELECT task_id, tool_name, success, latency_ms, reward FROM tool_invocations ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()


# -----------------------------
# Memory Layers
# -----------------------------
class EpisodicBuffer:
    def __init__(self, capacity: int = 256):
        self.capacity = capacity
        self.items: List[Dict[str, Any]] = []

    def add(self, item: Dict[str, Any]):
        self.items.append(item)
        if len(self.items) > self.capacity:
            self.items.pop(0)

    def recent(self, k: int = 10):
        return self.items[-k:]


class SemanticKB:
    """Vector KB storing heuristics and tool tips.
    Each entry metadata should include tags like {"type": "tool_tip", "tool": "..."}
    """
    def __init__(self, store: SimpleVectorStore):
        self.store = store

    def add_tip(self, text: str, meta: Dict[str, Any]):
        self.store.add_texts([text], [meta])

    def search_tips(self, query: str, k: int = 4, tool_hint: Optional[str] = None):
        def filt(m):
            return (m.get("type") in ("tool_tip", "heuristic")) and (tool_hint is None or m.get("tool") == tool_hint)
        return self.store.search(query, k=k, filter_fn=filt)


# -----------------------------
# Router Policies (Rule, LLM-RAG, LinUCB RL)
# -----------------------------
@dataclass
class RoutingDecision:
    use_tool: bool
    tool_name: Optional[str]
    params: Dict[str, Any]
    rationale: str = ""


class RouterPolicy:
    def select(self, query: str, tools: List[Tool], kb_snippets: List[str]) -> RoutingDecision:
        raise NotImplementedError

    def update(self, log_rows: List[Tuple[str, str, int, int, float]]):
        """Optional online update from SQL logs: (task_id, tool_name, success, latency_ms, reward)"""
        pass


class RuleRouter(RouterPolicy):
    def select(self, query: str, tools: List[Tool], kb_snippets: List[str]) -> RoutingDecision:
        ql = query.lower()
        for t in tools:
            if any(kw in ql for kw in t.keywords):
                return RoutingDecision(True, t.name, {"query": query}, rationale="rule-hit")
        return RoutingDecision(False, None, {}, rationale="rule-miss")


class LLMRAGRouter(RouterPolicy):
    def __init__(self, llm: LLM, tool_store: SemanticKB):
        self.llm = llm
        self.tool_store = tool_store

    def select(self, query: str, tools: List[Tool], kb_snippets: List[str]) -> RoutingDecision:
        tool_cards = []
        for t in tools:
            ex = (t.examples[0] if t.examples else {})
            tool_cards.append({
                "name": t.name,
                "desc": t.description,
                "example": ex
            })
        sys = "You are a precise Tool Router. Return strict JSON."
        user = json.dumps({
            "task": query,
            "kb_snippets": kb_snippets,
            "tools": tool_cards,
            "instruction": [
                "Decide whether a tool is needed.",
                "If yes, choose best tool and draft params.",
                "JSON only: {use_tool: bool, tool_name: str|null, params: object}"
            ]
        }, ensure_ascii=False)
        raw = self.llm.complete(sys, user)
        try:
            data = json.loads(raw)
            return RoutingDecision(bool(data.get("use_tool", False)), data.get("tool_name"), data.get("params", {}), rationale="llm")
        except Exception:
            return RoutingDecision(False, None, {}, rationale="llm-parse-fail")


class LinUCBRouter(RouterPolicy):
    """Contextual bandit for routing: one model per tool.
    Feature vector = [query_emb(64) + cost + latency_hint]
    Reward = alpha*success - beta*latency - gamma*cost (normalized)
    """
    def __init__(self, embedder: SimpleEmbedder, tools: List[Tool], alpha: float = 1.0):
        self.embedder = embedder
        self.alpha = alpha
        self.tool_index = {t.name: i for i, t in enumerate(tools)}
        d = 64 + 2  # embed dims + cost + latency_hint
        self.A = [self._I(d) for _ in tools]  # dxd
        self.b = [self._zeros(d) for _ in tools]  # dx1

    def _I(self, d):
        return [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]

    def _zeros(self, d):
        return [0.0 for _ in range(d)]

    def _matvec(self, M, v):
        return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]

    def _solve(self, A, b):
        # naive Gaussian elimination; replace with numpy.linalg.solve in production
        d = len(b)
        M = [row[:] for row in A]
        y = b[:]
        # forward
        for i in range(d):
            pivot = M[i][i] or 1e-6
            for j in range(i, d):
                M[i][j] /= pivot
            y[i] /= pivot
            for k in range(i+1, d):
                factor = M[k][i]
                for j in range(i, d):
                    M[k][j] -= factor * M[i][j]
                y[k] -= factor * y[i]
        # back
        x = [0.0]*d
        for i in range(d-1, -1, -1):
            x[i] = y[i] - sum(M[i][j]*x[j] for j in range(i+1, d))
        return x

    def _phi(self, query: str, tool: Tool) -> List[float]:
        e = self.embedder.embed(query)
        return e + [tool.cost, tool.latency_hint_ms/1000.0]

    def select(self, query: str, tools: List[Tool], kb_snippets: List[str]) -> RoutingDecision:
        # UCB per tool; also allow "no tool" action as baseline (index = -1)
        scores: List[Tuple[float, Optional[str]]] = [(0.0, None)]  # action None = no-tool
        for t in tools:
            i = self.tool_index[t.name]
            phi = self._phi(query, t)
            # theta = A^{-1} b
            theta = self._solve(self.A[i], self.b[i])
            # ucb = theta^T phi + alpha * sqrt(phi^T A^{-1} phi)
            # Compute A^{-1} approximately via solving A x = phi twice (inefficient but OK here)
            inv_phi = self._solve(self.A[i], phi)
            mean = sum(theta[j]*phi[j] for j in range(len(phi)))
            var = math.sqrt(max(1e-6, sum(phi[j]*inv_phi[j] for j in range(len(phi)))))
            ucb = mean + self.alpha * var
            scores.append((ucb, t.name))
        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_tool = scores[0]
        if best_tool is None:
            return RoutingDecision(False, None, {}, rationale="linucb-no-tool")
        return RoutingDecision(True, best_tool, {"query": query}, rationale="linucb")

    def update(self, log_rows: List[Tuple[str, str, int, int, float]]):
        # log row = (task_id, tool_name, success, latency_ms, reward)
        for _task_id, tool_name, success, latency_ms, reward in log_rows:
            if tool_name not in self.tool_index:
                continue
            i = self.tool_index[tool_name]
            # For update, we need the original context (query). In real system, store it in logs.
            # Here we assume we can't, so we skip; provide an API for real updates below.
            pass

    # Real online update with context
    def update_with_context(self, query: str, tool: Tool, reward: float):
        i = self.tool_index[tool.name]
        phi = self._phi(query, tool)
        # A <- A + phi phi^T ; b <- b + reward * phi
        d = len(phi)
        for r in range(d):
            for c in range(d):
                self.A[i][r][c] += phi[r]*phi[c]
        for r in range(d):
            self.b[i][r] += reward * phi[r]


# -----------------------------
# Nodes (LangGraph-style)
# -----------------------------
@dataclass
class NodeIO:
    goal: str
    query: str
    plan: str = ""
    kb_snippets: List[str] = field(default_factory=list)
    route: Optional[RoutingDecision] = None
    action_trace: List[Dict[str, Any]] = field(default_factory=list)
    outcome: Dict[str, Any] = field(default_factory=dict)
    reflection: Optional[Dict[str, Any]] = None
    final_answer: Optional[str] = None


class ToolRouterNode:
    def __init__(self, policy: RouterPolicy, kb: SemanticKB, registry: ToolRegistry):
        self.policy = policy
        self.kb = kb
        self.registry = registry

    def __call__(self, io: NodeIO) -> NodeIO:
        # Retrieve KB tips linked to the query or tools
        hits = self.kb.search_tips(io.query, k=4)
        tips = [t for _score, t, _m in hits]
        decision = self.policy.select(io.query, self.registry.all(), tips)
        io.kb_snippets = tips
        io.route = decision
        return io


class ToolExecutorNode:
    def __init__(self, registry: ToolRegistry, sql: SQLLog, reward_fn: Callable[[bool, int, float], float]):
        self.registry = registry
        self.sql = sql
        self.reward_fn = reward_fn

    def __call__(self, io: NodeIO) -> NodeIO:
        if not io.route or not io.route.use_tool:
            io.action_trace.append({"tool": None, "skipped": True})
            io.outcome = {"success": True, "skipped": True}
            return io
        tool = self.registry.get(io.route.tool_name)
        args = io.route.params
        t0 = now_ms()
        try:
            out = tool.run(args)
            latency = now_ms() - t0
            success = bool(out.get("ok", True))
            err = out.get("err_type")
            reward = self.reward_fn(success, latency, tool.cost)
            io.action_trace.append({"tool": tool.name, "args": args, "out": out, "latency_ms": latency})
            io.outcome = {"success": success, "latency_ms": latency, "err_type": err}
            self.sql.log({
                "task_id": io.goal,
                "tool_name": tool.name,
                "args_hash": sha1(args),
                "success": success,
                "latency_ms": latency,
                "err_type": err,
                "reward": reward,
                "output_schema_digest": sha1({k: type(v).__name__ for k, v in out.items()}),
            })
        except Exception as e:
            latency = now_ms() - t0
            reward = self.reward_fn(False, latency, tool.cost)
            io.action_trace.append({"tool": tool.name, "args": args, "exception": str(e), "latency_ms": latency})
            io.outcome = {"success": False, "latency_ms": latency, "err_type": "Exception"}
            self.sql.log({
                "task_id": io.goal,
                "tool_name": tool.name,
                "args_hash": sha1(args),
                "success": False,
                "latency_ms": latency,
                "err_type": "Exception",
                "reward": reward,
                "output_schema_digest": None,
            })
        return io


class ReflectionNode:
    TEMPLATE = (
        "You are the Self-Reflection module. Given GOAL, PLAN, TRACE, OUTCOME, "
        "produce JSON with keys: what_went_wrong[], why[], fix_next_time[], tool_insights[]."
    )

    def __init__(self, llm: LLM):
        self.llm = llm

    def __call__(self, io: NodeIO) -> NodeIO:
        sys = ReflectionNode.TEMPLATE
        user = json.dumps({
            "GOAL": io.goal,
            "PLAN": io.plan,
            "TRACE": io.action_trace,
            "OUTCOME": io.outcome,
        }, ensure_ascii=False)
        raw = self.llm.complete(sys, user)
        try:
            io.reflection = json.loads(raw)
        except Exception:
            io.reflection = {
                "what_went_wrong": [],
                "why": [],
                "fix_next_time": ["Validate outputs and retry on failure."],
                "tool_insights": []
            }
        return io


class KBWriteNode:
    def __init__(self, episodic: EpisodicBuffer, kb: SemanticKB):
        self.episodic = episodic
        self.kb = kb

    def __call__(self, io: NodeIO) -> NodeIO:
        # write episodic
        self.episodic.add({
            "task_id": io.goal,
            "trace": io.action_trace,
            "outcome": io.outcome,
            "reflection": io.reflection,
            "ts": now_ms(),
        })
        # distill insights
        if io.reflection:
            for tip in io.reflection.get("tool_insights", []):
                self.kb.add_tip(tip, {"type": "tool_tip"})
            for rule in io.reflection.get("fix_next_time", []):
                self.kb.add_tip(rule, {"type": "heuristic"})
        return io


class KBRetrieveNode:
    def __init__(self, kb: SemanticKB):
        self.kb = kb

    def __call__(self, io: NodeIO) -> NodeIO:
        hits = self.kb.search_tips(io.query, k=6)
        io.kb_snippets = [t for _s, t, _m in hits]
        return io


class MacroTool:
    def __init__(self, name: str, steps: List[Dict[str, Any]]):
        self.name = name
        self.steps = steps

    def run(self, registry: ToolRegistry, context: Dict[str, Any]) -> Dict[str, Any]:
        last = {}
        for step in self.steps:
            tool = registry.get(step["tool"]) if step.get("tool") else None
            params_tmpl = step.get("params", {})
            params = {k: context.get(k, v) for k, v in params_tmpl.items()}
            if tool is None:
                continue
            last = tool.run(params)
            context.update(last if isinstance(last, dict) else {"_last": last})
        return last


class MacroToolRunnerNode:
    def __init__(self, registry: ToolRegistry, macros: Dict[str, MacroTool]):
        self.registry = registry
        self.macros = macros

    def __call__(self, io: NodeIO) -> NodeIO:
        # Heuristic: if previous invocations show a frequent chain, invoke macro if exists.
        # For demo, we trigger by goal == macro name
        if io.goal in self.macros:
            out = self.macros[io.goal].run(self.registry, {"query": io.query})
            io.action_trace.append({"macro": io.goal, "out": out})
        return io


class AnswerCheckNode:
    def __init__(self, llm: LLM):
        self.llm = llm

    def __call__(self, io: NodeIO) -> NodeIO:
        sys = (
            "You are AnswerCheck. Given TRACE and OUTCOME, write a concise final answer. "
            "If tool was skipped, answer directly; if used, summarize with evidence."
        )
        user = json.dumps({"TRACE": io.action_trace, "OUTCOME": io.outcome, "QUERY": io.query}, ensure_ascii=False)
        text = self.llm.complete(sys, user)
        io.final_answer = text
        return io


# -----------------------------
# Graph Orchestrator
# -----------------------------
class Graph:
    def __init__(self, nodes: List[Callable[[NodeIO], NodeIO]]):
        self.nodes = nodes

    def run(self, io: NodeIO) -> NodeIO:
        for n in self.nodes:
            io = n(io)
        return io


# -----------------------------
# Reward Function (for RL routing updates)
# -----------------------------

def reward_fn(success: bool, latency_ms: int, cost: float, alpha=1.0, beta=0.001, gamma=0.1) -> float:
    """Simple linear reward. Tune coefficients to your SLOs.
    success -> +alpha, latency -> -beta * latency_ms, cost -> -gamma * cost
    """
    return (alpha if success else 0.0) - beta * latency_ms - gamma * cost


# -----------------------------
# Demo Tools
# -----------------------------

def search_tool_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    q = args.get("query", "")
    time.sleep(0.05)
    return {"ok": True, "results": [f"Result for: {q}"], "source": "search"}


def calc_tool_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    expr = args.get("expr") or args.get("query") or "1+1"
    try:
        val = eval(expr, {"__builtins__": {}}, {})
        return {"ok": True, "value": val}
    except Exception as e:
        return {"ok": False, "err_type": "EvalError", "msg": str(e)}


# -----------------------------
# Wiring Example
# -----------------------------
if __name__ == "__main__":
    # Instantiate components
    llm = LLM()
    embedder = SimpleEmbedder()
    vec_store = SimpleVectorStore(embedder)
    kb = SemanticKB(vec_store)
    episodic = EpisodicBuffer(128)
    sql = SQLLog(":memory:")

    # Seed KB with a couple of tips
    kb.add_tip("Always validate JSON before API call", {"type": "heuristic"})
    kb.add_tip("Search tool works best with keywords, not full questions.", {"type": "tool_tip", "tool": "search"})

    # Register tools
    registry = ToolRegistry()
    registry.register(Tool(
        name="search",
        description="Keyword web search returning snippets",
        keywords=["search", "find", "lookup"],
        cost=0.01,
        latency_hint_ms=200,
        examples=[{"query": "python dataclasses"}],
        run=search_tool_impl,
    ))
    registry.register(Tool(
        name="calc",
        description="Safe arithmetic evaluator",
        keywords=["calculate", "sum", "add", "+", "-", "*", "/"],
        cost=0.002,
        latency_hint_ms=20,
        examples=[{"expr": "2*(3+4)"}],
        run=calc_tool_impl,
    ))

    # Policies
    rule_policy = RuleRouter()
    rag_policy = LLMRAGRouter(llm, kb)
    linucb_policy = LinUCBRouter(embedder, registry.all(), alpha=1.0)

    # Choose a composite policy: try LinUCB -> LLM-RAG fallback -> rule fallback
    class CompositePolicy(RouterPolicy):
        def __init__(self, a: RouterPolicy, b: RouterPolicy, c: RouterPolicy):
            self.a, self.b, self.c = a, b, c
        def select(self, query, tools, kb_snippets):
            d = self.a.select(query, tools, kb_snippets)
            if d.use_tool or d.rationale.startswith("linucb"):
                return d
            d = self.b.select(query, tools, kb_snippets)
            if d.use_tool:
                return d
            return self.c.select(query, tools, kb_snippets)

    policy = CompositePolicy(linucb_policy, rag_policy, rule_policy)

    # Nodes
    router_node = ToolRouterNode(policy, kb, registry)
    exec_node = ToolExecutorNode(registry, sql, reward_fn)
    reflect_node = ReflectionNode(llm)
    kb_write_node = KBWriteNode(episodic, kb)
    kb_retrieve_node = KBRetrieveNode(kb)
    macro_runner = MacroToolRunnerNode(registry, macros={
        # Example macro: search then calc (illustration)
        "macro:search_then_calc": MacroTool("macro:search_then_calc", steps=[
            {"tool": "search", "params": {"query": "{query}"}},
            {"tool": "calc", "params": {"expr": "2*(3+4)"}},
        ])
    })
    answer_check = AnswerCheckNode(llm)

    # Build graph (Router -> Execute -> Reflection -> KBWrite -> KBRetrieve -> Answer)
    graph = Graph([
        router_node,
        exec_node,
        reflect_node,
        kb_write_node,
        kb_retrieve_node,
        macro_runner,
        answer_check,
    ])

    # Run a couple of queries and perform RL updates
    def run_and_learn(user_query: str):
        io = NodeIO(goal=f"task:{uuid.uuid4().hex[:8]}", query=user_query)
        io = graph.run(io)
        print("FINAL:", io.final_answer)
        # RL update (with context) if tool used
        if io.route and io.route.use_tool and io.action_trace:
            tname = io.route.tool_name
            tool = registry.get(tname)
            succ = io.outcome.get("success", False)
            rew = reward_fn(succ, io.outcome.get("latency_ms", 0), tool.cost)
            linucb_policy.update_with_context(user_query, tool, rew)
        return io

    # Examples
    run_and_learn("帮我计算 2*(3+4)")
    run_and_learn("查一下LangGraph 是什么？")
    run_and_learn("不要用工具，直接解释一下向量数据库是什么？")

    # Show recent logs
    print("\nLogs:", sql.recent(10))

```
