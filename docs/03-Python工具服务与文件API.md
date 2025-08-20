### Python 工具服务与文件 API

默认地址：`http://localhost:1601`

#### 路由前缀
- 工具：`/v1/tool`
- 文件：`/v1/file_tool`

---

#### 工具（支持流式 SSE 与非流式）
1) 代码执行（Code Interpreter）
- **POST** `/v1/tool/code_interpreter`
- 请求体（关键字段）：
  - `task`: 待执行的自然语言或代码任务
  - `file_names`: 结果关联的文件名数组（可选，会自动拼接预览 URL）
  - `request_id`: 会话/任务标识
  - `stream`: 是否流式
  - `stream_mode`: `{mode: "general"|"token"|"time", token?: N, time?: 秒}`
- 流式返回：SSE，含 `heartbeat` 与 `[DONE]`

2) 报告生成（Report）
- **POST** `/v1/tool/report`
- 字段同上，额外：
  - `file_type`: `html|ppt|md`，当为 `ppt|html` 时会自动剥离代码围栏

3) 深度搜索（Deep Search）
- **POST** `/v1/tool/deepsearch`
- 关键字段：`query`、`request_id`、`max_loop`、`search_engines`
- 返回：SSE（流式搜索进展与结果，含 `heartbeat` 与 `[DONE]`）

---

#### 文件接口（上传/下载/预览/列表）
1) 获取文件信息
- **POST** `/v1/file_tool/get_file`
  - Body：`{ "file_id": "...", "request_id": "...", "file_name": "..." }`
  - 返回：`ossUrl`、`downloadUrl`、`domainUrl`

2) 通过内容上传
- **POST** `/v1/file_tool/upload_file`
  - Body：`{ "file_name": "结果.md", "content": "...", "file_id": "...", "description": "...", "request_id": "..." }`

3) 通过二进制上传
- **POST** `/v1/file_tool/upload_file_data`
  - Form：`file=@local.bin`，`requestId=<uuid>`

4) 获取文件列表
- **POST** `/v1/file_tool/get_file_list`
  - Body：`{ "request_id": "...", "filters": [{"file_id": "..."}] }`

5) 下载与预览
- **GET** `/v1/file_tool/download/{file_id}/{file_name}`
- **GET** `/v1/file_tool/preview/{file_id}/{file_name}`

---

#### 最小可用示例（cURL）
代码执行（流式）：
```bash
curl -N -H 'Content-Type: application/json' -H 'Accept: text/event-stream' \
  -d '{
    "task": "用Python计算前10个素数，并解释思路",
    "file_names": [],
    "request_id": "req-001",
    "stream": true,
    "stream_mode": {"mode": "general"}
  }' \
  http://localhost:1601/v1/tool/code_interpreter
```

报告生成（非流式）：
```bash
curl -H 'Content-Type: application/json' \
  -d '{
    "task": "围绕xxx生成一份网页报告",
    "file_names": [],
    "file_type": "html",
    "file_name": "报告.html",
    "request_id": "req-002",
    "stream": false,
    "stream_mode": {"mode": "general"}
  }' \
  http://localhost:1601/v1/tool/report
```


