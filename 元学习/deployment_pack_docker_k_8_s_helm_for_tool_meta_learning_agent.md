# 🚀 Deployment Pack: Docker + Kubernetes (with Helm)

为上方的 **Tool Meta-Learning Stack（LangGraph 风格 + RL Router + FAISS/PGVector + OpenAI）** 提供容器化与 K8s 上线资产。

> 目录
> 1) `Dockerfile`
> 2) `requirements.txt`
> 3) `server.py`（FastAPI 服务端，包装 Graph）
> 4) `docker-compose.yaml`（本地含 Postgres/pgvector）
> 5) Helm Chart：`charts/agent/`（Deployment / Service / Secret / ConfigMap / HPA / Ingress）
> 6) 运行指南与常见问题

---

## 1) `Dockerfile`

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2, uvicorn, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (the production-ready file above assumed as app.py)
COPY app.py ./
COPY server.py ./

# Non-root user (optional)
RUN useradd -m svcuser
USER svcuser

EXPOSE 8080

# Healthcheck optional: hit /healthz
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
```

> 把上文画布里的**生产就绪版**保存为 `app.py`（或修改下方 `server.py` 的 import）。

---

## 2) `requirements.txt`

```text
fastapi==0.111.0
uvicorn[standard]==0.30.0
openai>=0.28.0
faiss-cpu>=1.8.0
psycopg2-binary>=2.9.9
numpy>=1.26.4
scikit-learn>=1.4.2
pgvector>=0.2.5
python-dotenv>=1.0.1
```

> 若使用 Anthropic，请在此加入 `anthropic` 并在 `app.py/server.py` 调用处切换。

---

## 3) `server.py`（FastAPI 网关）

提供 HTTP 接口：`POST /run` 运行一次 Agent；`POST /learn` 手动打分更新 LinUCB；`GET /healthz` 健康检查。

```python
from fastapi import FastAPI
from pydantic import BaseModel
import os
import uuid

# Import objects from app.py (the production-ready implementation above)
from app import (
    Graph, NodeIO, ToolRouterNode, ToolExecutorNode, ReflectionNode,
    KBWriteNode, KBRetrieveNode, AnswerCheckNode, ToolRegistry, SemanticKB,
    EpisodicBuffer, PostgresLog, LinUCBRouter, LLMRAGRouter, RuleRouter,
    reward_fn, FaissVectorStore, PGVectorStore, get_embedding, Tool,
    search_tool_impl, calc_tool_impl
)

app = FastAPI(title="Tool Meta-Learning Agent")

# Bootstrap singletons at startup
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_tools.index")
PG_DSN = os.getenv("PG_DSN")

# Build vector backend
if VECTOR_BACKEND == "faiss":
    dim = len(get_embedding("probe"))
    vec_backend = FaissVectorStore(dim=dim, index_path=FAISS_INDEX_PATH)
else:
    assert PG_DSN, "PG_DSN required for pgvector backend"
    vec_backend = PGVectorStore(PG_DSN)

kb = SemanticKB(vec_backend)
episodic = EpisodicBuffer(1024)
sql_log = PostgresLog(PG_DSN)

# Registry and tools (keep in sync with app.py)
registry = ToolRegistry()
registry.register(Tool(name="search", description="Web search", keywords=["search", "find"], run=search_tool_impl, cost=0.01))
registry.register(Tool(name="calc", description="Calculator", keywords=["calculate", "compute"], run=calc_tool_impl, cost=0.002))

# Seed tips once (idempotent in FAISS; PGVector may duplicate if you POST many times)
kb.add_tip("Always validate JSON before API call", {"type": "heuristic"})
kb.add_tip("Search tool works best with keywords", {"type": "tool_tip", "tool": "search"})

# Policies
emb_dim = len(get_embedding("probe"))
linucb = LinUCBRouter(dim=emb_dim, tools=registry.all(), alpha=1.0)
llm_rag = LLMRAGRouter(kb)
rule = RuleRouter()

class CompositePolicy:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
    def select(self, query, tools, kb_snippets):
        d = self.a.select(query, tools, kb_snippets)
        if d.use_tool or getattr(d, 'rationale', '').startswith("linucb"):
            return d
        d = self.b.select(query, tools, kb_snippets)
        if d.use_tool:
            return d
        return self.c.select(query, tools, kb_snippets)

policy = CompositePolicy(linucb, llm_rag, rule)

# Nodes and graph
router_node = ToolRouterNode(policy, kb, registry)
exec_node = ToolExecutorNode(registry, sql_log, reward_fn)
reflect_node = ReflectionNode()
kb_write_node = KBWriteNode(episodic, kb)
kb_retrieve_node = KBRetrieveNode(kb)
answer_node = AnswerCheckNode()

graph = Graph([router_node, exec_node, reflect_node, kb_write_node, kb_retrieve_node, answer_node])

class RunRequest(BaseModel):
    query: str
    goal: str | None = None

class LearnRequest(BaseModel):
    query: str
    tool_name: str
    reward: float

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/run")
def run(req: RunRequest):
    io = NodeIO(goal=req.goal or f"task:{uuid.uuid4().hex[:8]}", query=req.query)
    io = graph.run(io)
    # RL update if used
    if io.route and io.route.use_tool:
        from app import reward_fn as _rf
        t = registry.get(io.route.tool_name)
        succ = io.outcome.get("success", False)
        rew = _rf(succ, io.outcome.get("latency_ms", 0), t.cost)
        q_emb = get_embedding(req.query)
        linucb.update_with_context(q_emb, t, rew)
    return {
        "final_answer": io.final_answer,
        "route": io.route.__dict__ if io.route else None,
        "outcome": io.outcome,
        "kb_snippets": io.kb_snippets,
        "trace": io.action_trace,
    }

@app.post("/learn")
def learn(req: LearnRequest):
    q_emb = get_embedding(req.query)
    t = registry.get(req.tool_name)
    linucb.update_with_context(q_emb, t, req.reward)
    return {"ok": True}
```

---

## 4) `docker-compose.yaml`（本地一键起）

```yaml
version: "3.9"
services:
  db:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_PASSWORD: example
      POSTGRES_USER: agent
      POSTGRES_DB: agent
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      VECTOR_BACKEND: pgvector
      PG_DSN: postgresql://agent:example@db:5432/agent
    ports:
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy
```

运行：
```bash
docker compose up --build
curl -sX POST localhost:8080/run -H 'content-type: application/json' -d '{"query":"帮我计算 2*(3+4)"}' | jq
```

---

## 5) Helm Chart：`charts/agent/`

```
charts/agent/
  Chart.yaml
  values.yaml
  templates/
    deployment.yaml
    service.yaml
    configmap.yaml
    secret.yaml
    hpa.yaml
    ingress.yaml
    NOTES.txt
```

### `charts/agent/Chart.yaml`
```yaml
apiVersion: v2
name: agent
description: Tool Meta-Learning Agent (LangGraph + RL Router)
type: application
version: 0.1.0
appVersion: "0.1.0"
```

### `charts/agent/values.yaml`
```yaml
image:
  repository: your-dockerhub/agent
  tag: latest
  pullPolicy: IfNotPresent

replicaCount: 2

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

env:
  VECTOR_BACKEND: faiss # or pgvector
  FAISS_INDEX_PATH: /data/faiss_tools.index
  PG_DSN: "" # set when using pgvector

secrets:
  OPENAI_API_KEY: "" # helm --set-file or ExternalSecret

resources:
  limits:
    cpu: "1"
    memory: 1Gi
  requests:
    cpu: "100m"
    memory: 256Mi

ingress:
  enabled: false
  className: nginx
  hosts:
    - host: agent.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  # targetMemoryUtilizationPercentage: 70

persistence:
  enabled: true
  size: 2Gi
  storageClass: ""
```

### `templates/deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "agent.fullname" . }}
  labels:
    app: {{ include "agent.name" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "agent.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "agent.name" . }}
    spec:
      containers:
        - name: agent
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 8080
          env:
            - name: VECTOR_BACKEND
              value: {{ .Values.env.VECTOR_BACKEND | quote }}
            - name: FAISS_INDEX_PATH
              value: {{ .Values.env.FAISS_INDEX_PATH | quote }}
            - name: PG_DSN
              value: {{ .Values.env.PG_DSN | quote }}
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ include "agent.fullname" . }}
                  key: OPENAI_API_KEY
          volumeMounts:
            - name: data
              mountPath: /data
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 20
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: {{ include "agent.fullname" . }}
```

### `templates/service.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "agent.fullname" . }}
spec:
  selector:
    app: {{ include "agent.name" . }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  type: {{ .Values.service.type }}
```

### `templates/configmap.yaml`
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "agent.fullname" . }}-config
```

### `templates/secret.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "agent.fullname" . }}
stringData:
  OPENAI_API_KEY: {{ .Values.secrets.OPENAI_API_KEY | quote }}
```

### `templates/hpa.yaml`
```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "agent.fullname" . }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "agent.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
{{- end }}
```

### `templates/ingress.yaml`
```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "agent.fullname" . }}
  annotations:
    kubernetes.io/ingress.class: {{ .Values.ingress.className }}
spec:
  rules:
  {{- range .Values.ingress.hosts }}
    - host: {{ .host }}
      http:
        paths:
        {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "agent.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
        {{- end }}
  {{- end }}
  tls:
  {{- toYaml .Values.ingress.tls | nindent 2 }}
{{- end }}
```

### `templates/NOTES.txt`
```txt
1. Get the service URL by running these commands:
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "agent.fullname" . }} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  echo http://$SERVICE_IP/

2. Test:
  kubectl -n {{ .Release.Namespace }} port-forward svc/{{ include "agent.fullname" . }} 8080:80 &
  curl -sX POST localhost:8080/run -H 'content-type: application/json' -d '{"query":"帮我计算 2*(3+4)"}' | jq
```

---

## 6) 运行指南

### A. 构建镜像并本地起服务
```bash
# 将画布中的生产就绪版保存为 app.py，并与 Dockerfile/requirements.txt/server.py 放同目录
export OPENAI_API_KEY=sk-xxx
docker build -t your-dockerhub/agent:latest .
docker run --rm -p 8080:8080 \
  -e OPENAI_API_KEY \
  -e VECTOR_BACKEND=faiss \
  your-dockerhub/agent:latest
```

### B. 使用 docker-compose 启动（含 Postgres/pgvector）
```bash
export OPENAI_API_KEY=sk-xxx
docker compose up --build
```

### C. Helm 安装到 Kubernetes
```bash
# 1) 打包/推送镜像
export IMAGE=your-dockerhub/agent:latest
# 2) 安装 chart
helm upgrade --install agent charts/agent \
  --set image.repository=your-dockerhub/agent \
  --set image.tag=latest \
  --set env.VECTOR_BACKEND=pgvector \
  --set env.PG_DSN="postgresql://user:pass@pg:5432/db" \
  --set-file secrets.OPENAI_API_KEY=./openai.key
```

> **注意**：Postgres 建议用云服务或现网运维的 StatefulSet/Operator（Crunchy, Zalando）。若用自管 PG，请配置备份与监控。

---

## 常见问题（FAQ）
- **pgvector 索引与相似度**：示例使用 `<=>` 近邻（cosine），确保 `vector(1536)` 与你的 embedding 维度一致。
- **多副本一致性**：FAISS 在多副本下需共享持久卷或改用 PGVector；Helm 的 `persistence.enabled` 可为每个副本挂载 RWX 存储，或直接切到 PGVector。
- **成本控制**：通过环境变量切换 `openai_chat_model` / `openai_embedding_model`；也可在 `values.yaml` 里暴露。
- **安全**：把 `OPENAI_API_KEY` 通过 External Secrets 管理；Ingress 建议接 WAF/CC 防护。
- **可观测性**：加上 Prometheus 指标与日志收集（可在 server.py 中暴露 `/metrics`）。

---

> 到这里，你已经可以：本地（FAISS）快速跑，或在 K8s（PGVector）上线。需要我把 **Postgres StatefulSet** 也一并给出，还是对接 **Cloud SQL / RDS** 的 k8s Secret 示例？

