# Deployment Artifacts for LangGraph Agent: Tool Meta-Learning Stack

## 1. Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
```

## 2. requirements.txt
```
openai
faiss-cpu
psycopg2-binary
numpy
scikit-learn
langchain
```

## 3. Kubernetes Deployment (deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: langgraph-agent
  template:
    metadata:
      labels:
        app: langgraph-agent
    spec:
      containers:
        - name: agent
          image: your-dockerhub-username/langgraph-agent:latest
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: openai-secret
                  key: api-key
            - name: VECTOR_BACKEND
              value: "pgvector"
            - name: PG_DSN
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: dsn
            - name: FAISS_INDEX_PATH
              value: "/data/faiss"
          volumeMounts:
            - name: faiss-data
              mountPath: /data/faiss
      volumes:
        - name: faiss-data
          persistentVolumeClaim:
            claimName: faiss-pvc
```

## 4. Kubernetes Service (service.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: langgraph-agent-svc
spec:
  selector:
    app: langgraph-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

## 5. Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-secret
type: Opaque
data:
  api-key: <base64-encoded-openai-key>
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
data:
  dsn: <base64-encoded-postgres-dsn>
```

## 6. Persistent Volume Claim (pvc.yaml)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: faiss-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## Deployment Notes:
- Push Docker image: `docker build -t your-dockerhub-username/langgraph-agent:latest . && docker push your-dockerhub-username/langgraph-agent:latest`
- Apply manifests: `kubectl apply -f deployment.yaml -f service.yaml -f pvc.yaml -f secrets.yaml`
- Use Horizontal Pod Autoscaler: `kubectl autoscale deployment langgraph-agent --cpu-percent=70 --min=2 --max=10`
- Postgres + pgvector must be pre-provisioned.

---
Would you like me to also include **Helm Chart templates** and a **GitHub Actions CI/CD pipeline for building and deploying to k8s**?
