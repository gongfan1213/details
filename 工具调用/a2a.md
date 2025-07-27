https://a2a-protocol.org/latest/topics/agent-discovery/


Interaction Mechanisms¶
Request/Response (Polling):


The client sends a request (e.g., using the message/send RPC method) and receives a response from the server.
If the interaction requires a stateful long-running task, the server might initially respond with a working status. The client would then periodically call tasks/get to poll for updates until the task reaches a terminal state (e.g., completed, failed).

如果交互需要有状态的长时间运行任务，服务器可能最初会以working状态进行响应。然后客户端会定期调用tasks/get来轮询更新，直到任务达到终端状态（例如，completed、failed）。

Streaming (Server-Sent Events - SSE):

流式传输（服务器发送事件 - SSE）：


For tasks that produce results incrementally or provide real-time progress updates.

对于逐步生成结果或提供实时进度更新的任务。

The client initiates an interaction with the server using message/stream.

客户端使用message/stream发起与服务器的交互。

The server responds with an HTTP connection that remains open, over which it sends a stream of Server-Sent Events (SSE).

服务器通过保持打开的HTTP连接进行响应，并通过该连接发送服务器发送事件（SSE）流。

These events can be Task, Message, or TaskStatusUpdateEvent (for status changes) or TaskArtifactUpdateEvent (for new or updated artifact chunks).

这些事件可以是 Task、Message 或 TaskStatusUpdateEvent（用于状态更改），也可以是 TaskArtifactUpdateEvent（用于新的或更新的工件块）。

This requires the server to advertise the streaming capability in its Agent Card.

这要求服务器在其智能体卡片中宣传streaming功能。

Learn more about Streaming & Asynchronous Operations.

了解有关流处理与异步操作的更多信息。

Push Notifications: 推送通知：



For very long-running tasks or scenarios where maintaining a persistent connection (like SSE) is impractical.

对于长时间运行的任务，或者在维持持久连接（如服务器发送事件(SSE)）不切实际的场景中。

The client can provide a webhook URL when initiating a task (or by calling tasks/pushNotificationConfig/set).

客户可以在发起任务时（或通过调用 tasks/pushNotificationConfig/set）提供一个 webhook URL。

When the task status changes significantly (e.g., completes, fails, or requires input), the server can send an asynchronous notification (an HTTP POST request) to this client-provided webhook.

当任务状态发生重大变化（例如，完成、失败或需要输入）时，服务器可以向此客户端提供的 webhook 发送异步通知（HTTP POST 请求）。

This requires the server to advertise the pushNotifications capability in its Agent Card.

这要求服务器在其智能体卡片中公布pushNotifications功能。

Learn more about Streaming & Asynchronous Operations.

了解有关流处理与异步操作的更多信息。

a2a通信通过https进行的，所有的请求和响应都使用json-rpc2.0作为有效的载荷格式的

身份验证要求在agent card当中声明的

# agent card
the agent card is  a json document that servs as a digital business card 


supported protocal features like straming or pushNotifications

authentications:required authentication schemes

id,name,descripttion,inputModes,outputModes,examples

## 发现策略

### 1.well-known URI知名统一资源标识符


Process: 流程：

A client agent knows or programmatically discovers the domain of a potential A2A Server (e.g., smart-thermostat.example.com).

客户端智能体知道或以编程方式发现潜在A2A服务器的域名（例如，smart-thermostat.example.com）。

The client performs an HTTP GET request to https://smart-thermostat.example.com/.well-known/agent.json.

客户端向https://smart-thermostat.example.com/.well-known/agent.json执行HTTP GET请求。

If the Agent Card exists and is accessible, the server returns it as a JSON response.

如果智能体卡片存在且可访问，服务器会以JSON响应的形式返回它。


### 2. Curated Registries (Catalog-Based Discovery)¶2. 精选注册表（基于目录的发现）

Mechanism: An intermediary service (the registry) maintains a collection of Agent Cards. Clients query this registry to find agents based on various criteria (e.g., skills offered, tags, provider name, desired capabilities).

机制： 一种中介服务（注册表）维护一组智能体卡片。客户端根据各种标准（例如，提供的技能、标签、提供商名称、所需功能）查询此注册表以查找智能体。

Process: 流程：

A2A Servers (or their administrators) register their Agent Cards with the registry service. The mechanism for this registration is outside the scope of the A2A protocol itself.

A2A服务器（或其管理员）向注册服务注册其智能体卡。这种注册机制不在A2A协议本身的范畴内。

Client agents query the registry's API (e.g., "find agents with 'image-generation' skill that support streaming").

客户端智能体查询注册表的API（例如，“查找具备‘图像生成’技能且支持流传输的智能体”）。

The registry returns a list of matching Agent Cards or references to them.

注册表返回一组匹配的智能体卡片或其引用。

Considerations: Requires an additional registry service. The A2A protocol does not currently define a standard API for such registries, though this is an area of potential future exploration and community standardization.
注意事项: 需要额外的注册服务。目前A2A协议并未为这类注册中心定义标准API，不过这是未来可能探索及社区标准化的一个领域。

# 3. Direct Configuration / Private Discovery¶
In many scenarios, especially within tightly coupled systems, for private agents, or during development and testing, clients might be directly configured with Agent Card information or a URL to fetch it.

在许多场景中，尤其是在紧密耦合的系统内、针对私有智能体，或者在开发和测试期间，客户端可能会直接配置智能体卡片信息或获取该信息的网址。



Mechanism: The client application has hardcoded Agent Card details, reads them from a local configuration file, receives them through an environment variable, or fetches them from a private, proprietary API endpoint known to the client.

机制： 客户端应用程序对智能体卡详细信息进行了硬编码，从本地配置文件中读取，通过环境变量接收，或者从客户端已知的私有专有API端点获取。

Process: This is highly specific to the application's deployment and configuration strategy.

流程： 这与应用程序的部署和配置策略高度相关。

Advantages: Simple and effective for known, static relationships between agents or when dynamic discovery is not a requirement.

优点： 对于智能体之间已知的静态关系，或在不需要动态发现的情况下，这种方法简单有效。

Considerations: Less flexible for discovering new or updated agents dynamically. Changes to the remote agent's card might require re-configuration of the client. Proprietary API-based discovery is not standardized by A2A.

**注意事项**：在动态发现新的或更新的智能体方面灵活性较差。对远程智能体卡片的更改可能需要重新配置客户端。基于专有API的发现并未由应用到应用（A2A）进行标准化。

Protection Mechanisms: 保护机制：

Access Control on the Endpoint: The HTTP endpoint serving the Agent Card (whether it's the /.well-known/agent.json path, a registry API, or a custom URL) should be secured using standard web practices if the card is not intended for public, unauthenticated access.

端点的访问控制： 如果智能体卡片并非面向公众的无身份验证访问，则提供智能体卡片的HTTP端点（无论是 /.well-known/agent.json 路径、注册中心API还是自定义URL）都应使用标准的网络实践进行安全防护。

mTLS: Require mutual TLS for client authentication if appropriate for the trust model.

**双向传输层安全（mTLS）**：如果符合信任模型，要求使用双向传输层安全协议进行客户端身份验证。

Network Restrictions: Limit access to specific IP ranges, VPCs, or private networks.

**网络限制**：限制对特定IP范围、虚拟私有云（VPC）或专用网络的访问。

Authentication: Require standard HTTP authentication (e.g., OAuth 2.0 Bearer token, API Key) to access the Agent Card itself.

身份验证: 需要标准的HTTP身份验证（例如，OAuth 2.0承载令牌、API密钥）才能访问智能体卡片本身。






