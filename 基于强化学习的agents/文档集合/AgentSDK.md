### **第一章：OpenAI Agents SDK 概览**

#### **1.1 什么是 OpenAI Agents SDK？**
OpenAI Agents SDK 是一个旨在帮助开发者轻松构建智能 AI 助手的轻量级但功能强大的框架。它并非从零开始构建，而是 OpenAI 对先前实验性项目 Swarm 的一次生产就绪的升级。该 SDK 的核心目标是简化创建具备推理能力、能够使用各种工具以及可以进行多 Agent 协作的 AI 应用程序的过程。对于希望利用大型语言模型 (LLM) 的强大功能来创建能够自主执行任务的复杂工作流的开发者来说，Agents SDK 提供了一个结构化的、易于理解的平台。

Agents SDK 的设计理念围绕着三个基本概念：Agent（代理）、Handoff（移交）和 Guardrails（护栏）。Agent 是指配置了特定指令和工具的 LLM，它们能够独立思考并采取行动。Handoff 允许一个 Agent 将任务委托给另一个更专业的 Agent，从而实现 Agent 之间的协作。Guardrails 则是在 Agent 运行过程中并行工作的安全机制，用于验证输入和输出，确保 Agent 的行为符合预期。

#### **1.2 为何选择 Agents SDK？**
选择 OpenAI Agents SDK 有诸多优势。首先，该 SDK 的设计注重易用性，学习曲线平缓，开发者无需学习复杂的抽象概念即可快速上手。其次，Agents SDK 秉持“Python 优先”的原则，开发者可以使用熟悉的 Python 语言特性来编排和控制 Agent 的行为，这大大降低了开发门槛。

Agents SDK 内置了 Agent 循环机制，能够自动处理工具的调用、工具返回结果的反馈以及循环的持续，直至 LLM 完成任务。此外，强大的 Handoff 功能使得在多个 Agent 之间协调和委托任务变得非常便捷，开发者可以构建出复杂的、模块化的 Agent 系统。

安全性是 Agents SDK 的另一个重要考量。Guardrails 功能允许开发者并行运行输入验证和安全检查，一旦发现不符合预期的输入，可以及时终止 Agent 的运行，从而保障系统的安全。Function Tools 的引入使得将任何 Python 函数转化为 Agent 可以使用的工具变得简单，并且 SDK 能够自动生成工具的 Schema，方便 LLM 理解和调用。最后，内置的 Tracing 功能为开发者提供了强大的工作流可视化、调试和监控能力，可以清晰地了解 Agent 的每一步操作，便于发现和解决问题。

#### **1.3 Agents SDK 的核心概念**
OpenAI Agents SDK 的核心在于理解其关键组成部分，这些组件共同协作，使得构建复杂的 Agent 应用程序成为可能。

- **Agent (代理)**：Agent 是 Agents SDK 的核心，本质上是一个配置了指令和工具的 LLM。开发者可以为 Agent 设置系统提示等指令，指定其可以使用的工具，以及定义在需要时可以将任务移交给哪些其他 Agent。Agent 还可以配置可选的输入/输出 Guardrails 和更高级的模型参数。
- **Tool (工具)**：工具是 Agent 可以调用的外部功能，用于执行诸如获取数据、运行代码或与外部 API 交互等特定操作。工具可以是同步或异步的 Python 函数，Agents SDK 允许开发者将任何 Python 函数轻松地转化为工具供 Agent 使用。
- **Handoff (移交)**：Handoff 是一种机制，允许一个 Agent 将任务的控制权转移给另一个 Agent，以便更专业地处理特定的子任务。这对于构建需要多个 Agent 协同工作的复杂系统非常有用。
- **Guardrail (护栏)**：Guardrails 是一组安全检查措施，可以在 Agent 运行过程中并行执行，用于验证用户输入和 Agent 的输出是否符合预期的安全和合规标准。Guardrails 可以帮助防止恶意使用和意外后果，确保 Agent 的行为在开发者设定的范围之内。
- **Tracing (追踪)**：Tracing 是 Agents SDK 内置的功能，用于记录 Agent 运行过程中的每一个步骤，包括 LLM 的调用、工具的调用以及 Agent 之间的移交等。Tracing 对于调试、分析和监控 Agent 的行为至关重要，开发者可以通过 Tracing 信息了解 Agent 的决策过程，并进行性能优化。
- **Context (上下文)**：Context 是一个可以在 Agent 运行过程中存储和共享数据的可变对象。开发者可以创建任何 Python 对象作为 Context，并在 Agent 运行的各个阶段（包括工具函数中）访问和修改 Context 对象中的数据，这对于维护会话状态和在多个步骤之间传递信息非常有用。
- **Output Types (输出类型)**：Agents SDK 允许开发者指定 Agent 最终输出的结构。虽然默认情况下 Agent 的输出是自由格式的文本，但开发者可以定义特定的 Python 类型（例如 Pydantic 模型）来确保 Agent 返回结构化的 JSON 格式数据。

#### **1.4 Agents SDK 的架构概览**
OpenAI Agents SDK 的架构设计围绕着 Agent、Tool、Handoff、Guardrail 和 Tracing 这些核心概念。SDK 强调“Python 优先”的设计理念，这意味着开发者可以使用他们熟悉的 Python 语言结构来控制 Agent 的工作流程，而不是需要学习新的领域特定语言 (DSL)。

Agents SDK 本身负责处理许多底层的编排任务，例如工具的调用、工具返回结果的传递以及 Agent 循环的执行等。这使得开发者可以将精力更多地集中在 Agent 的业务逻辑和工作流程的设计上，而无需过多关注底层的实现细节。此外，SDK 内置了 Tracing 功能，这为开发者提供了一个强大的工具，可以可视化地查看 Agent 的每一步操作，从而方便进行调试和性能优化。

### **第二章：快速开始：环境搭建与基础 Agent**

#### **2.1 环境搭建**
在使用 OpenAI Agents SDK 之前，需要先搭建好开发环境。首先，确保你的系统中已经安装了 Python 和 pip。建议创建一个新的项目目录并初始化一个 Python 虚拟环境，以隔离项目依赖。在命令行中执行以下操作：
```notion-code bash
mkdir my_project
cd my_project
python -m venv .venv
```
创建虚拟环境后，需要激活它。在 macOS/Linux 系统中，执行：
```notion-code bash
source .venv/bin/activate
```
在 Windows 系统中，执行：
```notion-code bash
.venv\Scripts\activate
```
激活虚拟环境后，就可以使用 pip 安装 Agents SDK 了：
```notion-code bash
pip install openai-agents
```
最后一步是设置 OpenAI API 密钥为环境变量。如果还没有 API 密钥，请访问 OpenAI 平台获取。在 macOS/Linux 系统中，执行：
```notion-code bash
export OPENAI_API_KEY=sk-...
```
在 Windows 系统中，执行：
```notion-code bash
set OPENAI_API_KEY=sk-...
```

#### **2.2 创建你的第一个 Agent**
环境搭建完成后，就可以创建你的第一个 Agent 了。首先，需要从`agents`模块导入`Agent`类。然后，可以使用名称和指令来定义一个基本的 Agent。例如，创建一个简单的数学辅导 Agent：
```notion-code python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```
在这个例子中，我们创建了一个名为 "Math Tutor" 的 Agent，并赋予了它关于如何回答数学问题的指令。

#### **2.3 运行 Agent**
要运行创建的 Agent，需要从`agents`模块导入`Runner`类。然后，可以使用`Runner.run()`方法（用于异步执行）或`Runner.run_sync()`方法（用于同步执行）来执行 Agent。Agent 的运行机制是一个循环过程。当调用`Runner.run()`时，SDK 会启动一个循环，该循环首先将用户输入和历史对话传递给 LLM。LLM 根据 Agent 的指令决定是生成最终答案、调用工具还是移交给另一个 Agent。如果 LLM 调用了一个工具，SDK 会处理工具的调用，并将工具的响应反馈给 LLM，然后 LLM 再次生成响应。这个过程会一直持续到 LLM 生成最终答案或者达到设定的最大循环次数。

以下是如何运行上面创建的数学辅导 Agent 的示例：
```notion-code python
from agents import Runner
import asyncio

async def main():
    result = await Runner.run(agent, "What is 2 + 2?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```
运行这段代码后，你将会在控制台看到 Agent 的输出结果，即 "4"。

### **第三章：工具的使用**

#### **3.1 什么是工具？**
在 OpenAI Agents SDK 中，工具是指 Agent 可以调用的外部函数，用于执行特定的操作。工具的主要目的是扩展 Agent 的能力，使其能够完成超出 LLM 本身知识范围的任务，例如访问最新的网络信息、检索本地文件内容或者执行复杂的计算。

#### **3.2 内置工具**
Agents SDK 提供了一些常用的内置工具，可以直接供 Agent 使用：
- **WebSearchTool (网页搜索工具)**：允许 Agent 搜索互联网上的信息，获取最新的数据和知识。
- **FileSearchTool (文件搜索工具)**：允许 Agent 在用户上传的文件中进行搜索，检索相关信息，这对于处理文档分析、知识库查询等场景非常有用。
- **ComputerTool (计算机使用工具)**：允许 Agent 模拟用户在计算机上的操作，例如点击、滚动或输入文本，从而实现一些自动化的任务。

#### **3.3 Function Tools (函数工具)**
除了内置工具外，开发者还可以使用 Function Tools 将任何 Python 函数转化为 Agent 可以调用的工具。这可以通过使用`@function_tool`装饰器来实现。Agents SDK 能够自动解析函数的参数和文档字符串，并生成相应的 Schema，供 LLM 理解和使用。开发者也可以创建自定义的 Function Tools，通过提供工具的名称、描述、参数 Schema 和一个用于执行工具调用的异步函数来实现。

#### **3.4 Agents as Tools (将 Agent 作为工具)**
Agents SDK 还支持将一个 Agent 作为另一个 Agent 的工具来使用。这允许一个 Agent 调用另一个 Agent 来完成特定的任务，而无需将控制权完全移交给被调用的 Agent。这种机制非常适用于构建复杂的 Agent 协作模式，例如一个主 Agent 可以协调多个专门的子 Agent 来完成一个复杂的任务。

#### **3.5 处理工具中的错误**
在实际应用中，工具的调用可能会因为各种原因而失败。Agents SDK 提供了`failure_error_function`参数，允许开发者在定义 Function Tool 时指定一个函数，该函数在工具调用失败时提供一个错误响应给 LLM，从而提高系统的鲁棒性。

### **第四章：多 Agent 协作**

#### **4.1 Handoff 的概念与配置**
Handoff 是 OpenAI Agents SDK 中实现多 Agent 协作的关键特性之一。它允许一个 Agent 在执行过程中，将任务的控制权移交给另一个预先定义好的 Agent。开发者可以使用 Agent 对象的`handoffs`属性来定义该 Agent 可以移交任务的目标 Agent 列表。为了辅助 Agent 在运行时决定将任务移交给哪个目标 Agent，开发者可以为每个 Handoff 定义描述信息。

#### **4.2 运行多 Agent 工作流**
使用`Runner`类可以轻松运行包含多个 Agent 的工作流。开发者只需要将初始 Agent 和用户输入传递给`Runner.run()`方法，SDK 会自动处理 Agent 之间的移交过程。

#### **4.3 Handoff 的输入和过滤器**
在定义 Handoff 时，开发者可以指定传递给下一个 Agent 的输入参数，也可以通过过滤器来控制传递的会话历史。这为开发者提供了更细粒度的控制，可以确保上下文信息在 Agent 之间正确传递。

#### **4.4 示例：构建一个多语言客服系统**
一个典型的多 Agent 协作的例子是构建一个多语言客服系统。可以创建一个充当入口的 Triage Agent，它能够识别用户输入的语言，并将请求移交给相应的语言专家 Agent 进行处理。例如，如果用户输入的是中文，Triage Agent 就将请求移交给中文客服 Agent；如果是英文，则移交给英文客服 Agent。

#### **4.5 父 Agent (Triage Agent) 与子 Agent 的协作**
在多 Agent 系统中，通常会有一个父 Agent（也称为 Triage Agent），它的主要职责是接收用户的初始请求，并根据请求的内容和类型，将任务分配给一个或多个子 Agent 来完成。子 Agent 通常是更专业的，能够处理特定领域或特定类型的任务。父 Agent 负责协调整个工作流程，确保各个子 Agent 能够协同工作，最终完成用户的请求。

### **第五章：保障安全：Guardrails 的应用**

#### **5.1 Guardrails 的重要性**
在构建 AI Agent 应用程序时，安全性是一个至关重要的方面。OpenAI Agents SDK 提供的 Guardrails 功能旨在帮助开发者确保 Agent 的行为在预期范围内，防止恶意使用和意外后果，并维护 Agent 的安全性和合规性。通过合理地使用 Guardrails，开发者可以确保他们的 AI Agent 符合伦理标准和政策要求。

#### **5.2 输入 Guardrails**
输入 Guardrails 在 Agent 接收用户输入之前对其进行验证。开发者可以使用快速且廉价的模型进行初步检查，例如判断用户是否在询问政治观点或试图进行恶意攻击。如果输入不符合预期，Guardrail 可以触发一个 Tripwire，立即中断 Agent 的执行，从而避免不必要的计算资源浪费和潜在的风险。

#### **5.3 输出 Guardrails**
与输入 Guardrails 相对应的是输出 Guardrails，它在 Agent 生成最终输出后对其进行验证。这可以确保 Agent 的输出符合预定义的格式或内容策略，例如不允许生成有害信息或超出业务范围的回答。

#### **5.4 实现自定义 Guardrails**
开发者可以根据自己的需求实现自定义的 Guardrails。这通常涉及到定义一个 Guardrail 函数，该函数接收输入（对于输入 Guardrail）或输出（对于输出 Guardrail），并返回一个`GuardrailFunctionOutput`对象。可以使用`@input_guardrail`和`@output_guardrail`装饰器将这些函数注册为 Agent 的 Guardrails。

### **第六章：上下文管理**

#### **6.1 Context 对象**
在 OpenAI Agents SDK 中，Context 对象扮演着至关重要的角色，它允许开发者在 Agent 运行的整个生命周期内存储和共享数据。这个 Context 对象可以是任何 Python 对象，例如字典、列表或者自定义类的实例。一个 Agent 运行过程中的所有工具都可以访问并修改这个 Context 对象，这使得在多个工具调用之间以及在 Agent 的不同步骤之间共享信息变得非常方便。

#### **6.2 本地 Context 与 Agent/LLM Context**
在 Agents SDK 中，需要区分两种类型的 Context：本地 Context 和 Agent/LLM Context。本地 Context 是指在 Python 代码中用于管理数据和依赖关系的对象。开发者可以将诸如用户信息、API 密钥、数据库连接等信息存储在本地 Context 中，并在工具函数或其他回调函数中使用。另一方面，Agent/LLM Context 是指 LLM 在生成响应时能够看到的数据。LLM 只能通过对话历史来获取信息，因此任何希望 LLM 能够感知到的信息都必须以某种方式添加到对话历史中。

#### **6.3 在工具中使用 Context**
在工具函数中访问 Context 对象通常通过`RunContextWrapper`来实现。当调用 Agent 的运行方法（例如`Runner.run()`）时，开发者可以将自定义的 Context 对象作为参数传递进去。SDK 会将这个 Context 对象包装在一个`RunContextWrapper`对象中，然后将这个包装器对象传递给所有的工具函数、生命周期钩子等。开发者可以通过访问包装器对象的`context`属性来获取原始的 Context 对象。例如，在一个工具函数中获取用户信息的示例：
```notion-code python
from dataclasses import dataclass
from agents import RunContextWrapper, function_tool

@dataclass
class UserInfo:
    name: str
    uid: int

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
    return f"User {wrapper.context.name} is 47 years old"
```

#### **6.4 在 Agent 指令中使用 Context**
除了在工具中使用 Context 外，开发者还可以在 Agent 的指令中使用 Context 信息，从而根据不同的上下文定制 Agent 的行为。这通常通过使用动态指令函数来实现。开发者可以定义一个函数，该函数接收`RunContextWrapper`对象作为参数，并根据 Context 对象中的信息生成不同的提示字符串。然后，将这个函数作为 Agent 的`instructions`参数传递进去。例如，根据用户信息定制 Agent 行为的示例：
```notion-code python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper

@dataclass
class UserContext:
    name: str

def dynamic_instructions(context: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."

user_info = UserContext(name="Alice")
triage_agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)
```
在这个例子中，Agent 的指令会根据当前用户的名字动态生成。

### **第七章：追踪与调试**

#### **7.1 Tracing 的作用与优势**
OpenAI Agents SDK 内置的 Tracing 功能对于开发和维护复杂的 AI Agent 应用程序至关重要。Tracing 能够记录 Agent 运行过程中的每一个关键步骤，包括 LLM 的调用、工具的调用以及 Agent 之间的移交等。这对于开发者来说是无价的，因为它可以帮助他们调试代码、分析 Agent 的行为模式以及监控 Agent 在生产环境中的性能。

#### **7.2 查看 Traces**
Tracing 功能默认是启用的，开发者可以在 OpenAI 仪表板中查看 Agent 运行的详细信息。每个 Trace 记录都包含诸如 Trace ID、Workflow Name 和 Group ID 等属性，方便开发者对 Agent 的运行进行分组和分析。

#### **7.3 Spans 的概念**
在 Tracing 的上下文中，Span 表示 Trace 中的一个操作单元。每个 Span 都包含开始和结束时间戳，可以帮助开发者了解 Agent 运行过程中各个环节的耗时情况。

#### **7.4 自定义 Tracing Processor**
对于更高级的 Tracing 需求，Agents SDK 允许开发者使用自定义的 Tracing Processor。这允许开发者将 Tracing 数据发送到其他后端系统进行存储和分析，或者对 Tracing 数据进行自定义的处理。

### **第八章：高级主题**

#### **8.1 Streaming (流式处理)**
对于需要实时反馈用户 Agent 思考过程或工具调用进度的应用程序，Agents SDK 提供了 Streaming 功能。通过调用`Runner.run_streamed()`方法，开发者可以获取一个异步迭代器，该迭代器会逐步产生 Agent 的输出事件，包括部分文本响应和工具调用信息，从而实现更流畅的用户体验。

#### **8.2 输出类型 (Output Types)**
默认情况下，Agent 的最终输出是自由格式的文本。然而，Agents SDK 允许开发者通过`output_type`参数指定 Agent 应该产生的结构化输出格式。这对于需要 Agent 返回特定格式（例如 JSON）数据的场景非常有用，开发者可以使用 Pydantic 模型等来定义输出数据的结构。

#### **8.3 生命周期事件 (Lifecycle Events)**
Agents SDK 提供了钩子 (hooks) 机制，允许开发者在 Agent 运行过程中的特定生命周期事件发生时执行自定义的代码。例如，开发者可以在 Agent 移交任务给另一个 Agent 之前或之后执行一些日志记录或数据预处理操作。通过继承`AgentHooks`类并重写感兴趣的方法，可以轻松地 Hook 到 Agent 的生命周期事件。

#### **8.4 模型配置 (Model Configuration)**
开发者可以通过`model_settings`参数配置 Agent 使用的 LLM 的参数，例如温度 (temperature)、Top P 等。这允许开发者根据具体的应用场景调整模型的行为，例如在需要创造性输出时提高温度，或者在需要更确定性输出时降低温度。

#### **8.5 编排多个 Agent (Orchestrating Multiple Agents)**
Agents SDK 的核心优势之一是能够轻松地编排多个 Agent 协同工作。通过定义不同的 Agent 并使用 Handoff 机制，开发者可以构建出复杂的 Agent 工作流，每个 Agent 负责处理特定的任务，最终协同完成用户的目标。

### **第九章：最佳实践**
在使用 OpenAI Agents SDK 构建应用程序时，遵循一些最佳实践可以帮助开发者提高效率、确保安全性和可靠性。

- **仔细记录函数 Schema**：确保为 Agent 可以调用的每个工具函数编写清晰且详细的 Schema，以便 LLM 能够正确理解如何调用这些工具。
- **使用严格的 Schema 检查**：对于工具函数的参数，建议使用严格的 Schema 检查（例如 Pydantic 模型），以避免因参数不完整或格式错误导致的问题。
- **应用适当的 Guardrails**：根据应用程序的具体需求，应用合适的输入和输出 Guardrails，例如内容过滤、使用配额或数据验证等，以确保 Agent 的行为符合预期。
- **彻底追踪复杂的工作流**：对于涉及多个步骤或多个 Agent 的复杂工作流，务必启用并仔细查看 Tracing 信息，这对于调试和优化 Agent 的行为非常有帮助。
- **考虑使用 Handoff 处理专业任务**：如果应用程序涉及多个领域或需要处理多种语言，可以考虑使用 Handoff 将任务委派给更专业的子 Agent。
- **参考 OpenAI 的 Prompt 工程最佳实践**：遵循 OpenAI 提供的 Prompt 工程最佳实践，可以帮助开发者编写更有效的指令，引导 Agent 产生更符合预期的结果。
- **监控 API 使用情况和成本**：定期监控 API 的使用情况，并设置成本控制措施，以避免不必要的费用。

### **第十章：实际应用案例**
OpenAI Agents SDK 具有广泛的应用潜力，可以用于构建各种智能 Agent 应用程序。以下是一些实际应用案例：

- **AI 驱动的会计助手**：可以自动化记账、查询最新的税务法规并生成财务报告。
- **智能客服系统**：能够调用 API 查询订单状态、解决客户支持问题，甚至可以处理退款或取消订单等操作。
- **自动化研究助手**：可以搜索最新的市场趋势、金融数据或法律更新，并生成研究报告。
- **企业级知识管理系统**：可以利用文件搜索工具，帮助员工快速找到他们需要的文档和信息。
- **多语言翻译助手**：可以根据用户输入的语言，自动将文本翻译成目标语言。
- **内容创作助手**：可以根据用户提供的关键词和要求，自动生成文章、博客帖子或其他类型的文本内容。

### **第十一章：结论**
OpenAI Agents SDK 为开发者提供了一个强大且易于使用的平台，用于构建各种复杂的 AI Agent 应用程序。通过理解和掌握 SDK 的核心概念、环境搭建、工具使用、多 Agent 协作、安全保障、上下文管理以及追踪调试等关键方面，开发者可以充分利用 LLM 的潜力，创建出能够自主执行任务、与外部世界交互并实现特定目标的智能助手。随着 AI 技术的不断发展，Agents SDK 将在推动 AI Agent 领域的创新和应用方面发挥越来越重要的作用。


- 引用的著作

1. OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/

2. openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows, 访问时间为 三月 14, 2025， https://github.com/openai/openai-agents-python

3. A Deep Dive Into The OpenAI Agents SDK - Sid Bharath, 访问时间为 三月 14, 2025， https://www.siddharthbharath.com/openai-agents-sdk/

4. Unpacking OpenAI's Agents SDK: A Technical Deep Dive into the Future of AI Agents, 访问时间为 三月 14, 2025， https://mtugrull.medium.com/unpacking-openais-agents-sdk-a-technical-deep-dive-into-the-future-of-ai-agents-af32dd56e9d1

5. Agents SDK - OpenAI API, 访问时间为 三月 14, 2025， https://platform.openai.com/docs/guides/agents-sdk

6. New tools for building agents | OpenAI, 访问时间为 三月 14, 2025， https://openai.com/index/new-tools-for-building-agents/

7. Building AI Agents with OpenAI's Agents SDK: A Beginner's Guide | by Agen.cy - Medium, 访问时间为 三月 14, 2025， https://medium.com/@agencyai/building-ai-agents-with-openais-agents-sdk-a-beginner-s-guide-66751e5e7e05

8. Building Agentic AI Applications using OpenAI Agents SDK - ADaSci, 访问时间为 三月 14, 2025， https://adasci.org/building-agentic-ai-applications-using-openai-agents-sdk/

9. Tools - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/tools/

10. OpenAI's Agents SDK: The Future Of AI-Powered Digital Employees - Spearhead, 访问时间为 三月 14, 2025， https://spearhead.so/openais-agents-sdk-the-future-of-ai-powered-digital-employees/

11. Agents - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/agents/

12. Getting Started with OpenAI Agents SDK - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=oE-gITN9ZJs

13. Agents SDK from OpenAI! | Full Tutorial - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=35nxORG1mtg

14. Mastering OpenAI's new Agents SDK & Responses API [Part 1] - DEV Community, 访问时间为 三月 14, 2025， https://dev.to/bobbyhalljr/mastering-openais-new-agents-sdk-responses-api-part-1-2al8

15. Everything you need to know about OpenAI's NEW AI Agents - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=pVuM5WAwQnY

16. Introduction to OpenAI Agents SDK (with examples) - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=yCPSj6lfx-0

17. Quickstart - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/quickstart/

18. Prompt examples - OpenAI API, 访问时间为 三月 14, 2025， https://platform.openai.com/examples

19. OpenAI Agents SDK: Clearly BEATS CrewAI & LangGraph? - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=gGJWQjynOcg

20. Context management - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/context/

21. Guardrails - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/guardrails/

22. Tracing - OpenAI Agents SDK, 访问时间为 三月 14, 2025， https://openai.github.io/openai-agents-python/tracing/

23. AI Research Revolution: Build Your Own Agent with OpenAI SDK - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=WW4M1yvPHw4

24. Best practices for prompt engineering with the OpenAI API, 访问时间为 三月 14, 2025， https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api

25. Production best practices - OpenAI API, 访问时间为 三月 14, 2025， https://platform.openai.com/docs/guides/production-best-practices

26. Issues · openai/openai-agents-python - GitHub, 访问时间为 三月 14, 2025， https://github.com/openai/openai-agents-python/issues

27. Urgent Need for Assistance: Persistent Issues with OpenAI API for Fleetmaster AI, 访问时间为 三月 14, 2025， https://community.openai.com/t/urgent-need-for-assistance-persistent-issues-with-openai-api-for-fleetmaster-ai/1058237

28. OpenAI's Agents SDK is Here & It's Fixing My AI Startup Problems - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=uUOHdxIL_fg

29. Topics tagged agents - OpenAI Developer Forum, 访问时间为 三月 14, 2025， https://community.openai.com/tag/agents


30. New tools for building agents : r/OpenAI - Reddit, 访问时间为 三月 14, 2025， https://www.reddit.com/r/OpenAI/comments/1j8vse0/new_tools_for_building_agents/

31. Integrate Project-Ready Agents - Feature requests - OpenAI Developer Forum, 访问时间为 三月 14, 2025， https://community.openai.com/t/integrate-project-ready-agents/1093996

32. Openai Agents SDK, Responses Api Tutorial - DEV Community, 访问时间为 三月 14, 2025， https://dev.to/mehmetakar/openai-agents-sdk-responses-api-tutorial-o8d

33. New tools for building agents: Responses API, web search, file search, computer use, and Agents SDK - Announcements - OpenAI Developer Forum, 访问时间为 三月 14, 2025， https://community.openai.com/t/new-tools-for-building-agents-responses-api-web-search-file-search-computer-use-and-agents-sdk/1140896

34. Agents - OpenAI API, 访问时间为 三月 14, 2025， https://platform.openai.com/docs/guides/agents

35. OpenAI Releases New Custom Agent Tools - Perplexity, 访问时间为 三月 14, 2025， https://www.perplexity.ai/page/openai-releases-new-custom-age-0SxjY06OTReWo9OK_gjQCA

36. The Agent Platform Wars Heat Up As OpenAI Releases Agents SDK - YouTube, 访问时间为 三月 14, 2025， https://www.youtube.com/watch?v=ZqT_llrJuXs

37. Use Azure OpenAI and APIM with the OpenAI Agents SDK | Microsoft Community Hub, 访问时间为 三月 14, 2025， https://techcommunity.microsoft.com/blog/azure-ai-services-blog/use-azure-openai-and-apim-with-the-openai-agents-sdk/4392537
38. 
