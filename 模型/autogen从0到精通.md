### **1. 微软 AutoGen 简介**

##### **1.1 什么是 AutoGen？**

AutoGen 是微软研究院开发的一个开源编程框架，旨在构建能够协同工作以解决复杂任务的 AI 代理。AutoGen 的核心设计理念在于促进多个代理之间的合作，通过对话和信息交换，共同完成那些单个 AI 系统难以独立完成的任务。这种多代理协同的特性是 AutoGen 的主要特点，使其区别于其他侧重于单代理的工具。正如 PyTorch 在深度学习领域所扮演的角色一样，AutoGen 旨在为 Agentic AI 的开发和研究提供一个易于使用且灵活的框架。通过提供一个标准化的平台，AutoGen 加速了 Agentic AI 在解决实际问题方面的进展。

AutoGen 的目标是简化构建下一代基于多代理对话的 LLM 应用的过程。它旨在通过提供一个通用的框架来编排、自动化和优化复杂的 LLM 工作流程，从而最大限度地发挥 LLM 模型的性能并克服其固有的局限性。AutoGen 不仅仅是一个工具，更像是一个研究平台，旨在推动 Agentic AI 领域的发展，并为研究人员和开发者提供一个试验和创新的环境。

##### **1.2 主要特性和设计原则**

AutoGen 的设计着重于提升 Agentic 工作流程的代码质量、鲁棒性、通用性和可扩展性。为了实现这些目标，AutoGen 采用了异步、事件驱动的架构。这种架构使得系统能够支持更灵活的协作模式，并更好地应对复杂多代理系统的扩展性需求。在 AutoGen 中，代理通过异步消息进行通信，支持事件驱动和请求/响应两种交互模式。这种设计允许代理独立运行并响应事件，从而提高了系统的整体效率和灵活性。

AutoGen 具有高度模块化和可扩展的设计，用户可以轻松地通过可插拔的组件定制系统，包括自定义代理、工具、记忆和模型。这种模块化设计不仅促进了代码的重用，也使得开发者可以根据特定的应用需求轻松地替换或添加组件。此外，AutoGen 还支持构建主动式和长期运行的代理，这对于处理复杂的、需要持续交互的任务至关重要。

为了进一步增强框架的功能，AutoGen 提供了内置和社区扩展。这些扩展模块包括先进的模型客户端、各种类型的代理、多代理团队管理以及专门为 Agentic 工作流程设计的工具。对社区扩展的支持鼓励了开源开发者为 AutoGen 贡献自己的扩展，从而不断丰富和完善框架的功能。AutoGen 还支持跨语言互操作性，目前支持 Python 和 .NET，并且正在开发对更多语言的支持。这种跨语言能力使得不同技术栈的开发者能够更容易地使用和集成 AutoGen。为了保证代码的可靠性和可维护性，AutoGen 的接口强制执行构建时的类型检查，从而确保代码的鲁棒性和一致性。最后，AutoGen 提供了强大的可观察性和调试工具，内置了用于跟踪、追踪和调试代理交互和工作流程的机制，并支持 OpenTelemetry 这一行业标准的可观察性框架。这些工具对于理解和管理复杂多代理系统的行为至关重要。

##### **1.3 AutoGen 的演进：从 v0.2 到 v0.4**

AutoGen 在发布初始版本后，受到了广泛的关注。然而，用户在使用过程中也遇到了一些挑战，尤其是在扩展应用、处理动态工作流程和调试工具方面存在一定的局限性。基于社区的反馈，微软对 AutoGen 进行了全面的重新设计，推出了 v0.4 版本。v0.4 版本着重于改进代码质量、鲁棒性、可用性和 Agentic 工作流程的可扩展性。这一重大更新旨在建立一个强大的生态系统，以推动 Agentic AI 的进一步发展。

v0.4 版本解决了 v0.2 中存在的扩展性不足、动态工作流程支持有限以及调试工具缺乏等问题。新版本采用了更为健壮的异步、事件驱动架构，从而能够支持更广泛的 Agentic 应用场景，并提供更强的可观察性、更灵活的协作模式以及可重用的组件。为了方便现有 v0.2 用户迁移到新版本，AutoGen v0.4 通过 AgentChat API 提供了一条平滑的升级路径。AgentChat API 在很大程度上保留了 v0.2 的抽象级别，使得现有代码的迁移变得更加容易。例如，AgentChat 提供了与 v0.2 中行为相似的 AssistantAgent 和 UserProxy agent。此外，它还提供了一个团队接口，其中包括 RoundRobinGroupChat 和 SelectorGroupChat 等实现，涵盖了 v0.2 中 GroupChat 类的所有功能。

**表 1：AutoGen v0.2 和 v0.4 的比较**

| 特性/方面 | AutoGen v0.2 | AutoGen v0.4 |
| --- | --- | --- |
| 架构 | 隐式 | 异步，事件驱动 |
| 可扩展性 | 有限 | 改进，支持分布式代理 |
| 可观察性 | 有限 | 内置工具，支持 OpenTelemetry |
| 调试 | 有限 | 改进的工具，消息追踪 |
| 可扩展性 | 基础 | 模块化，可插拔组件，社区扩展 |
| 语言支持 | 主要为 Python | Python 和 .NET，计划支持更多语言 |

#### **2. 设置 AutoGen 开发环境**

##### **2.1 系统要求**

要使用 AutoGen，系统必须满足一定的要求。AutoGen 的核心是用 Python 编写的，因此需要安装**Python 3.10 或更高版本**。这是运行 AutoGen 框架的基础。确保 Python 版本符合要求是开始使用 AutoGen 的首要步骤。

##### **2.2 安装方法**

AutoGen 提供了多种安装方法，以满足不同用户的需求和偏好。最常用的方法是使用 pip 包管理器安装`autogen-agentchat`库。可以在终端或命令提示符中运行以下命令来安装核心框架：

**Bash**

`pip install autogen-agentchat`

对于需要使用 OpenAI 模型的用户，建议安装`autogen-ext[openai]`扩展包。该扩展包包含了与 OpenAI API 集成的必要组件。可以使用以下命令进行安装：

**Bash**

`pip install autogen-ext[openai]`

AutoGen 还提供了一个无需编写代码即可构建多代理工作流程的图形用户界面，即 AutoGen Studio。要安装 AutoGen Studio，可以使用以下命令：

**Bash**

`pip install autogenstudio`

AutoGen 的模块化设计允许用户根据需要安装额外的功能。例如，如果需要使用特定的功能（如 blendsearch、web-surfer、video-surfer 或 Anthropic 模型），可以安装相应的额外选项。安装命令的格式为`pip install "autogen-ext[feature_name]"`。

除了使用 pip 安装外，一些用户可能更喜欢使用 Anaconda 环境管理系统。AutoGen 也可以通过 Anaconda 进行安装。用户需要在 Anaconda 提示符中创建并激活一个包含 Python 3.10 或更高版本的环境，然后使用 pip 安装 AutoGen。

对于希望修改 AutoGen 源代码或使用最新开发版本的开发者，还可以选择从 GitHub 仓库克隆源代码进行安装。这需要用户具备一定的 Python 开发经验。

##### **2.3 设置 API 密钥**

要使 AutoGen 能够与各种大型语言模型（如 OpenAI、Groq 和 Hugging Face）进行交互，通常需要配置相应的 API 密钥。API 密钥是访问这些 LLM 服务的凭证，对于 AutoGen 代理利用 LLM 的能力至关重要。

AutoGen 提供了多种设置 API 密钥的方法，包括使用环境变量、配置文件（如`OAI_CONFIG_LIST.json`）以及`.env`文件。这些方法提供了灵活性和安全性，方便用户管理敏感的凭证。

例如，要配置 OpenAI 模型，通常需要设置包含模型名称和 API 密钥的`config_list`。`config_list`可以直接在代码中定义，也可以从 JSON 文件加载。使用`config_list_from_json`函数可以方便地从 JSON 文件加载配置信息，尤其是在需要配置多个模型或复杂的设置时。

值得注意的是，AutoGen 不仅支持 OpenAI 模型，还可以通过兼容 OpenAI API 的端点与其他非 OpenAI 模型进行交互，例如 FastChat、LM Studio、Ollama、Hugging Face Inference API 和 Groq。这为用户提供了广泛的模型选择，包括开源选项。

#### **3. 核心概念：代理与对话**

##### **3.1 什么是代理？**

在 AutoGen 中，代理被定义为通过消息进行通信、维护自身状态并响应接收到的消息或状态变化而执行动作的软件实体。这些动作可能修改代理的状态并产生外部影响，例如更新消息日志、发送新消息、执行代码或进行 API 调用。AutoGen 的代理具有可定制和可对话的特性，能够集成 LLM、工具和人类，从而实现复杂的任务解决。AutoGen AgentChat 提供了一系列预设的代理类型，每种代理都具有特定的角色和功能，包括 AssistantAgent、UserProxyAgent、CodeExecutorAgent、OpenAIAssistantAgent、MultimodalWebSurfer、FileSurfer 和 VideoSurfer。

##### **3.2 主要代理类型详解**

##### **3.2.1 AssistantAgent**

AssistantAgent 是一种内置的代理类型，它充当 AI 助手，使用 LLM 来解决任务。它是利用 LLM 能力的关键组件。AssistantAgent 能够使用工具和函数来扩展其功能，超越了单纯的文本生成。每个 AssistantAgent 都配置有一个默认的系统消息，但用户可以自定义该消息以定义代理的角色和行为。值得一提的是，AssistantAgent 还具备代码生成和调试的能力，这使得 AutoGen 在软件开发任务中尤其有用。

##### **3.2.2 UserProxyAgent**

UserProxyAgent 充当人类用户的代理，促进交互并提供反馈。它是实现人机协作工作流程的关键。UserProxyAgent 具有代码执行能力，并且可以通过配置进行设置，允许安全且受控地执行其他代理生成的代码。UserProxyAgent 提供了不同的`human_input_mode`选项（ALWAYS、NEVER、TERMINATE），用于控制与人类用户的交互程度。此外，UserProxyAgent 还支持默认的自动回复，并且可以通过`register_reply`方法进行自定义，从而在特定条件下实现更自主的行为。

**表 2：AutoGen AgentChat 中的不同代理类型**

```csv
**代理类型**,**描述**,**主要特性/功能**
AssistantAgent,充当 AI 助手，使用 LLM 解决任务。,LLM 驱动，工具和函数使用，代码生成，可定制的系统消息。
UserProxyAgent,充当人类用户的代理，促进交互并提供反馈。,人机交互，代码执行，可配置的人工输入模式，可定制的自动回复。
CodeExecutorAgent,旨在执行代码。,执行代码片段。
OpenAIAssistantAgent,由 OpenAI Assistant 提供支持，能够使用自定义工具。,利用 OpenAI Assistants API。
MultimodalWebSurfer,能够搜索网络并访问网页以收集信息。,网络搜索和浏览，多模态输入。
FileSurfer,可以搜索和浏览本地文件以获取信息。,本地文件系统访问。
VideoSurfer,旨在观看视频并从中提取信息。,视频分析。
```

**表 3：UserProxyAgent 的常见** `human_input_mode` **选项**

```csv
**模式**,**描述**,**用例**
ALWAYS,在每次收到消息后提示用户输入。,交互式调试，需要持续人工监督的场景。
NEVER,从不提示用户输入；依赖默认的自动回复或基于 LLM 的响应。,完全自主的工作流程，自动化系统。
TERMINATE,仅在收到终止消息时提示用户输入。,自主工作流程，仅在结束时需要人工干预。
```

##### **3.3 对话的概念**

AutoGen 的核心在于代理之间的交互，这种交互通过发送和接收消息来实现。通信是多代理协同的核心机制。ConversableAgent 是能够进行交互的代理的基类。它为构建可以相互通信的代理提供了基本框架。AutoGen 的强大之处在于其能够自动化多个有能力的代理之间的聊天过程，从而支持自主和人机协作的工作流程。

#### **4. 探索 AutoGen 中的不同对话模式**

##### **4.1 基本双代理聊天**

最简单的交互模式是 UserProxyAgent 和 AssistantAgent 之间的交互，通常用于执行基本的任务。这种模式是更复杂的多代理交互的基础。以下代码片段展示了如何启动一个基本的双代理聊天：

```notion-code python
import os
from autogen import AssistantAgent, UserProxyAgent

llm_config = {
    "config_list": [{
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY")
    }]
}
assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

user_proxy.initiate_chat(
    assistant,
    message="请告诉我一个关于 NVDA 和 TSLA 股票价格的笑话。",
)
```

此代码创建了一个 AssistantAgent 和一个 UserProxyAgent，然后 UserProxyAgent 向 AssistantAgent 发送了一条消息，启动了对话。

##### **4.2 顺序多代理聊天**

在顺序多代理聊天模式中，一个代理的输出会成为下一个代理的输入，形成一个明确的序列。这种模式适用于需要线性工作流程的任务。`carryover`属性可以用于在不同代理之间的对话中传递上下文信息，从而保持连续性和关联性。

##### **4.3 群聊**

群聊模式允许多个代理通过`GroupChatManager`进行协作。这种模式支持更复杂的协同问题解决。`GroupChatManager`负责协调群聊中的代理，并决定哪个代理应该发言。AutoGen 提供了不同的发言者选择策略，包括自动（由 LLM 决定）、手动（用户选择）、随机和轮流。

##### **4.4 嵌套聊天**

嵌套聊天模式是指在一次对话中启动另一次“对话中的对话”，用于处理更复杂的工作流程。这种模式允许封装子任务或寻求专业知识，而不会中断主对话流程。可以使用`register_nested_chats`方法来定义和触发嵌套对话。

##### **4.5 StateFlow（基于状态的操作的工作流程）**

StateFlow 允许使用 AutoGen 代理从面向状态的角度构建工作流程。这种模式允许定义更结构化和确定性的工作流程。通过自定义发言者选择方法，可以轻松实现面向状态的工作流程，从而精确控制在工作流程的每个阶段由哪个代理发言。

#### **5. 将外部工具和函数集成到 AutoGen 代理中**

##### **5.1 工具和函数的概念**

在 AutoGen 中，工具是指代理可以执行的特定操作，例如网络搜索、代码执行或 API 调用。函数是指可以注册并由代理调用的 Python 代码。工具和函数的使用扩展了 LLM 驱动的代理的能力，使其能够执行超出其固有知识范围的操作。

##### **5.2 集成工具和函数的方法**

AutoGen 提供了多种集成工具和函数的方法：

- **使用** `function_map`：在代理初始化期间，可以使用`function_map`参数将函数注册到代理 。

- **使用** `register_function`**方法**：可以在代理创建后，使用代理的`register_function`方法动态地添加工具 。

- **使用** `@assistant.register_for_llm()`**装饰器**：专门用于注册 LLM 可以调用的函数 。

- **使用** `@user_proxy.register_for_execution()`**装饰器**：用于注册 UserProxyAgent 可以执行的函数 。

- **在代理的** `llm_config`**中指定工具**：可以使用`function_list`参数，其格式与 OpenAI API 的函数调用规范一致 。

**表 4：集成工具和函数的方法**

```csv
**方法**,**描述**,**示例/用法**
使用`function_map`,在代理初始化期间注册函数。,"`user_proxy = UserProxyAgent(..., function_map={'func_name': func_impl})`"
使用`register_function`,在代理创建后动态添加函数。,`agent.register_function(function_map={'func_name': func_impl})`
`@assistant.register_for_llm()`,注册 LLM 可以调用的函数。,"`@assistant.register_for_llm(description='...')\ndef func_name(...)`"
`@user_proxy.register_for_execution()`,注册 UserProxyAgent 可以执行的函数。,`@user_proxy.register_for_execution()\ndef func_name(...)`
`llm_config` (function_list),在代理的 LLM 配置中指定工具。,`llm_config={'functions': [...]}`
```

##### **5.3 工具集成示例**

AutoGen 支持多种工具集成，例如：

- **网络搜索**：可以使用内置工具或自定义函数实现 。

- **代码执行**：通过配置`code_execution_config`实现 。

- **外部 API 集成**：例如，与 ElevenLabs（文本转语音）、Stability AI（图像生成）和 Groq API 集成

- **访问数据库和本地文件**。

- **使用 LangChain 工具**：可以利用 LangChain 中丰富的工具生态系统 。

#### **6. AutoGen 的高级特性和定制**

##### **6.1 自定义代理**

AutoGen 允许通过继承`BaseChatAgent`类来创建自定义代理。这为完全控制代理行为提供了可能。创建自定义代理需要实现`on_messages()`和`on_reset()`方法，这些方法是定义代理如何响应消息和管理状态的核心。文档中提供了自定义代理的示例，如 CountDownAgent、ArithmeticAgent 和 GeminiAssistantAgent，展示了如何为特定任务构建专门的代理。

##### **6.2 定制代理行为**

AutoGen 允许对预设代理的行为进行定制。对于 AssistantAgent，可以通过覆盖默认的系统消息来改变其角色和指令。对于 UserProxyAgent，可以根据需要定制`human_input_mode`。此外，还可以使用`register_reply`方法注册自定义的回复函数，以实现更复杂和上下文相关的自动响应。在群聊中，还可以定制发言者的选择逻辑。

##### **6.3 内存和状态管理**

AutoGen 中的代理是状态化的，它们会维护对话历史，这使得它们能够进行上下文相关的交互。AutoGen 还支持保存和恢复代理的状态，这对于长时间运行的任务和恢复中断的对话非常重要。此外，AutoGen 引入了任务中心记忆的概念，旨在提高代理的学习能力和自适应性。

#### **7. AutoGen 的实际用例和应用**

##### **7.1 软件开发**

AutoGen 在软件开发领域具有广泛的应用潜力，包括自动化代码生成、执行和调试。它可以用于生成数据模型、API 控制器、客户端代码和文档，从而提高开发效率并确保代码一致性。AutoGen 还可以与 Roslyn（用于 .NET）等工具集成，进行代码分析和重构。

##### **7.2 研究与开发**

AutoGen 在研究领域也具有重要价值，可以用于文献综述和信息检索，自动化收集和综合信息的过程。此外，AutoGen 还可以用于假设验证和科学发现，展示了 AI 辅助研究的潜力。

##### **7.3 客户服务与支持**

AutoGen 可以用于构建具有多代理能力的聊天机器人，从而实现更复杂和高效的客户互动。它还可以实现将客户咨询路由到不同的“部门”或专业代理，提高客户支持的质量和效率。

##### **7.4 数据分析与可视化**

AutoGen 可以自动化数据分析和洞察生成的过程，简化从数据中提取有意义信息的过程。通过群聊，AutoGen 还可以实现自动化数据可视化，有助于更好地理解和传达数据洞察。

##### **7.5 供应链优化**

AutoGen 的嵌套聊天功能可以用于解决复杂的现实世界问题，例如供应链优化（OptiGuide）。这展示了 AutoGen 在建模复杂的层级决策过程方面的能力。

##### **7.6 内容生成与编辑**

AutoGen 可以生成各种形式的内容，包括博客、文章、营销文案和销售材料，并可以编辑和完善生成的内容，提高文本的质量和准确性。

##### **7.7 其他应用**

AutoGen 的应用场景非常广泛，还包括游戏（例如，会话式国际象棋）、教育（AI 教师）、个人助理（类似 Jarvis）、网络安全（威胁检测和响应）、金融（投资组合分析）、法律咨询和机器人技术。

#### **8. 使用 AutoGen 进行开发的最佳实践**

- **从简单的对话拓扑开始**：先从双代理聊天入手，再逐步过渡到更复杂的模式。
- **优先考虑使用内置代理**：利用`AssistantAgent`和`UserProxyAgent`作为起点。
- **尝试重用内置的回复方法**：在创建自定义回复机制之前，先理解并使用默认的回复机制。
- **在初始测试阶段始终让人类参与其中**：将`human_input_mode`设置为`"ALWAYS"`，以便更好地控制和调试。
- **逐步提高代理的自主性**：一旦对小规模成功有信心，就将`human_input_mode`设置为`"NEVER"`或`"TERMINATE"`。
- **自定义发言者选择**：根据具体需求调整下一个发言者，以实现更好的控制和提高令牌效率。
- **利用函数而不是总是执行代码**：对于不需要代码执行的任务，使用函数调用。
- **将代理用于组织，而不仅仅是对话**：使用代理来代表系统内不同的角色和职责。
- **实施缓存策略**：存储过去的推理结果，以加快重复评估的速度。
- **彻底理解代理配置选项**：查阅`llm_config`、`code_execution_config`等的文档。
- **监控代理交互并在需要时进行干预**：仔细观察自动化代理，并在需要时提供人工专业知识。
- **探索 AutoGen Studio 以进行快速原型设计**：利用无需编写代码的 GUI 进行快速实验和工作流程设计。

#### **9. AutoGen 生态系统：与其他框架的集成**

##### **9.1 AutoGen 和 LangChain**

AutoGen 和 LangChain 都是流行的开源框架，旨在简化 LLM 驱动的应用程序的开发。AutoGen 侧重于 Agentic AI，支持创建多个交互代理协同解决任务的系统。LangChain 则强调可组合性，提供模块化构建块，开发者可以将其链接起来创建自定义的 LLM 工作流程。尽管两者方法不同，但它们的集成可以发挥各自的优势。例如，可以在 AutoGen 中使用 LangChain 的工具，从而利用 LangChain 丰富的工具生态系统。

##### **9.2 AutoGen 和 Semantic Kernel**

微软正积极推动 AutoGen 和 Semantic Kernel 这两个框架的战略融合。Semantic Kernel 侧重于将 AI 功能集成到企业级应用程序中，而 AutoGen 则专注于构建智能代理。未来的方向是将 AutoGen 的多代理运行时与 Semantic Kernel 对齐，为开发者提供一个统一的平台，既能进行前沿的代理设计实验，又能将这些实验平稳过渡到生产级部署。目前已经实现了在 Semantic Kernel 中托管 AutoGen 代理，以及 AutoGen 集成 Semantic Kernel 连接器的功能。

##### **9.3 AutoGen 和 Hugging Face**

AutoGen 可以与 Hugging Face 的模型集成，一种方式是通过 LiteLLM，LiteLLM 充当代理服务器，使得 AutoGen 可以像使用 OpenAI API 一样使用 Hugging Face 模型。另一种方式是在 AutoGen 中集成基于 LangChain 的自定义客户端，以加载和使用 Hugging Face 模型。这使得开发者能够利用 Hugging Face 庞大的开源语言模型库。

##### **9.4 AutoGen 和其他工具/框架**

AutoGen 还可以与其他工具和框架集成，例如用于 RAG（检索增强生成）的向量数据库，以及工作流程编排工具 LangGraph。

#### **10. AutoGen 的最新发展和未来展望**

##### **10.1 AutoGen v0.4 及更高版本**

AutoGen v0.4 是一个完全重新设计的版本，重点在于异步消息传递、模块化、可观察性、可扩展性和跨语言支持。它引入了 AutoGen Bench 用于代理性能基准测试，并重建了 AutoGen Studio，增加了实时更新、执行中控制和可视化团队构建器等增强功能。跨语言支持方面，除了 Python 之外，还增加了对 .NET 的支持，并计划支持更多语言。此外，还引入了任务中心记忆，以提高代理的学习能力和适应性。

##### **10.2 路线图和未来方向**

AutoGen 的未来发展方向包括将 AutoGen 核心与 Semantic Kernel 对齐，发布 .NET 版本的 v0.4，开发内置扩展和应用程序，并积极构建一个社区驱动的扩展和应用程序生态系统。

#### **11. 结论：掌握 AutoGen 以实现 Agentic AI**

AutoGen 作为一个强大的开源框架，为构建多代理 AI 系统提供了灵活且易于使用的工具。通过理解其核心概念、掌握不同类型的代理和对话模式、学会集成外部工具和函数以及利用其高级特性和定制选项，开发者和研究人员可以有效地利用 AutoGen 来解决各种复杂的实际问题。从软件开发到研究、客户服务和内容生成，AutoGen 的应用场景非常广泛。随着 AutoGen 的不断发展和完善，以及与其他框架的深度集成，它将在 Agentic AI 领域发挥越来越重要的作用。鼓励用户积极探索 AutoGen 的各项功能，参与到社区中，共同推动 Agentic AI 技术的进步。
