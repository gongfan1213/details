https://www.analyticsvidhya.com/blog/2025/01/agentic-rag-system-architectures/


https://www.analyticsvidhya.com/blog/2024/11/rag-vs-agentic-rag/


# 元信息
- 网页类型: 普通网站
- 标题: 7种用于构建AI代理的智能RAG系统架构



搜索

## 7种用于构建AI代理的智能RAG系统架构

网址

[https://www.analyticsvidhya.com/blog/2025/01/agentic-rag-system-architectures/]()

对我来说，2024年不仅是使用大型语言模型（LLMs）生成内容的一年，更是理解其内部工作原理的一年。在探索大型语言模型、检索增强生成（RAG）等技术的过程中，我发现了AI代理的潜力——它们是能够在最少人工干预的情况下执行任务和做出决策的自主系统。回顾2023年，检索增强生成（RAG）备受关注，而2024年则随着智能RAG工作流的发展，在各个行业推动了创新。展望未来，2025年将成为“AI代理之年”，自主系统将彻底改变生产力，重塑行业格局，借助智能RAG系统释放前所未有的可能性。

这些工作流由具备复杂决策和任务执行能力的自主AI代理提供支持，它们提高了生产力，并改变了个人和组织解决问题的方式。从静态工具向动态、代理驱动流程的转变，带来了前所未有的效率，为更具创新性的2025年奠定了基础。今天，我们将探讨智能RAG系统的类型。在本指南中，我们将深入了解各类智能RAG的架构等内容。

#### 目录

- [智能RAG系统：RAG与智能AI系统的结合]()

- [为什么我们要关注智能RAG系统？]()

- [智能RAG：融合RAG与AI代理]()

- [智能RAG路由器]()

- [查询规划智能RAG]()

- [自适应RAG]()

- [智能纠正RAG]()

- [自我反思RAG]()

- [推测性RAG]()

- [自路由智能RAG]()

- [结论]()

#### 智能RAG系统：RAG与智能AI系统的结合

为了简单理解智能RAG，让我们剖析这个术语：它是RAG与AI代理的融合。如果您不了解这些术语，别担心！我们很快就会深入探讨它们。

现在，我将阐述RAG和智能AI系统（AI代理）。

##### 什么是RAG（检索增强生成）？

![概念图片]()

来源：作者

**RAG**是一个框架，旨在通过将外部知识源整合到生成过程中，提升生成式AI模型的性能。其工作原理如下：

- **检索组件**：这部分从外部知识库、数据库或其他数据存储库中获取相关信息。这些来源可以包括结构化或非结构化数据，如文档、API，甚至实时数据流。

- **增强**：检索到的信息用于指导生成模型。这确保输出在事实准确性上更可靠，以外部数据为依据，且具有丰富的上下文。

- **生成**：生成式AI系统（如GPT）将检索到的知识与其自身的推理能力相结合，生成最终输出。

当处理复杂查询或需要最新的、特定领域知识的场景时，RAG特别有价值。

##### 什么是AI代理？

![概念图片]()

来源：[Dipanjan Sarkar]()

以下是AI代理工作流对查询“2024年欧洲杯谁赢了？告诉我更多细节！”的响应过程：

1. **初始指令提示**：用户输入查询，例如“2024年欧洲杯谁赢了？告诉我更多细节！”。

1. **大型语言模型处理和工具选择**：大型语言模型（LLM）解读查询，并决定是否需要外部工具（如网络搜索）。它发起一个**函数调用**以获取更多细节。

1. **工具执行和上下文检索**：所选工具（如搜索API）检索相关信息。在这里，它获取了2024年欧洲杯决赛的细节。

1. **响应生成**：新信息与原始查询相结合。大型语言模型生成完整的最终响应：“2024年7月在柏林举行的决赛中，西班牙以2-1击败英格兰，赢得了2024年欧洲杯。”

简而言之，智能AI系统具有以下核心组件：

##### 大型语言模型（LLMs）：操作的核心

大型语言模型作为中央处理单元，负责解读输入并生成有意义的响应。

- **输入查询**：用户提出的问题或命令，启动AI的操作。

- **理解查询**：AI分析输入以掌握其含义和意图。

- **生成响应**：基于查询，AI制定适当且连贯的回复。

##### 工具整合：执行任务的“双手”

外部工具增强了AI的功能，使其能够执行超越文本交互的特定任务。

- **文档阅读器工具**：处理文本文档并提取见解。

- **分析工具**：进行数据分析，提供可操作的见解。

- **对话工具**：促进交互式和动态的对话能力。

##### 记忆系统：上下文智能的关键

记忆使AI能够保留并利用过去的交互，以提供更具上下文感知的响应。

- **短期记忆**：保存近期交互，用于即时的上下文使用。

- **长期记忆**：长期存储信息，供持续参考。

- **语义记忆**：保留一般知识和事实，以支持有依据的交互。

这展示了AI如何整合用户提示、工具输出和自然语言生成。

以下是[AI代理]()的定义：

**AI代理**是自主软件系统，旨在通过与环境交互来执行特定任务或实现特定目标。AI代理的关键特征包括：

1. **感知**：它们感知或检索有关环境的数据（例如，从API或用户输入中）。

1. **推理**：它们分析数据以做出明智的决策，通常利用像GPT这样的AI模型进行自然语言理解。

1. **行动**：它们在现实或虚拟世界中执行行动，例如生成响应、触发工作流或修改系统。

1. **学习**：高级代理通常会根据反馈或新数据随时间调整和改进其性能。

AI代理可以处理多个领域的任务，如客户服务、数据分析、工作流自动化等。

#### 为什么我们要关注智能RAG系统？

首先，以下是基本检索增强生成（RAG）的局限性：

1. **何时检索**：系统可能难以确定何时需要检索，可能导致答案不完整或准确性较低。

1. **文档质量**：检索到的文档可能与用户的问题不太匹配，这会削弱响应的相关性。

1. **生成错误**：模型可能会“幻觉”，添加不准确或不相关的信息，而这些信息并不受检索到的内容支持。

1. **答案精确性**：即使有相关文档，生成的响应也可能无法直接或充分地回答用户的查询，使输出的可靠性降低。

1. **推理问题**：系统无法对复杂查询进行推理，阻碍了细致的理解。

1. **适应性有限**：传统系统无法动态调整策略，如选择API调用或网络搜索。

##### 智能RAG的重要性

了解[智能RAG]()系统有助于我们针对上述挑战部署合适的解决方案，完成特定任务，并确保与预期用例保持一致。其重要性如下：

1. **量身定制的解决方案**：

- 不同类型的智能RAG系统针对不同程度的自主性和复杂性而设计。例如：

- **智能RAG路由器**：智能RAG路由器是一个模块化框架，根据查询的意图和复杂性，动态地将任务路由到适当的检索、生成或行动组件。
- **自我反思RAG**：自我反思RAG整合了内省机制，使系统能够通过在最终确定输出之前，反复评估检索相关性、生成质量和决策准确性，来评估和完善其响应。

- 了解这些类型可确保优化设计和资源利用。

1. **风险管理**：

- 智能系统涉及决策，这可能带来错误行动、过度依赖或滥用等风险。了解每种类型的范围和局限性可以减轻这些风险。

1. **创新与可扩展性**：

- 区分不同类型使企业能够将其系统从基本实施扩展到能够处理企业级挑战的复杂代理。

简而言之，智能RAG可以进行规划、适应和迭代，以找到用户问题的正确解决方案。

#### 智能RAG：融合RAG与AI代理

结合AI代理和RAG工作流，以下是智能RAG的架构：

![概念图片]()

来源：作者

智能RAG结合了RAG的结构化检索和知识整合能力，以及AI代理的自主性和适应性。其工作原理如下：

1. **动态知识检索**：配备RAG的代理可以实时检索特定信息，确保它们使用最新且与上下文相关的数据进行操作。

1. **智能决策**：代理处理检索到的数据，应用高级推理生成解决方案、完成任务或深入准确地回答问题。

1. **面向任务的执行**：与静态RAG管道不同，智能RAG系统可以执行多步骤任务，根据不断变化的目标调整，或基于反馈循环改进其方法。

1. **持续改进**：通过学习，代理随着时间的推移改进其检索策略、推理能力和任务执行，变得更加高效和有效。

##### 智能RAG的应用

智能RAG的应用如下：

- **客户支持**：通过访问实时数据源，自动检索并提供对用户查询的准确响应。

- **内容创作**：在法律或医疗等复杂领域生成富含上下文的内容，并以检索到的知识为支持。

- **研究辅助**：通过自主收集和综合来自庞大数据库的相关材料，为研究人员提供帮助。

- **工作流自动化**：通过将检索驱动的决策整合到业务流程中，简化企业运营。

智能RAG代表了检索增强生成和自主AI代理之间的强大协同作用，使系统能够以无与伦比的智能、适应性和相关性进行操作。它是构建不仅信息丰富，而且能够独立执行复杂的、知识密集型任务的AI系统的重要一步。

要了解更多，请阅读：[RAG与智能RAG：综合指南]()。

希望现在您对智能RAG有了充分的了解，在下一节中，我将介绍一些重要且流行的智能RAG系统类型及其架构。

#### 1. 智能RAG路由器

如前所述，“智能”一词意味着系统的行为类似于智能代理，能够推理并决定使用哪些工具或方法来检索和处理数据。通过利用检索（例如数据库搜索、网络搜索、语义搜索）和生成（例如大型语言模型处理），该系统确保以最有效的方式回答用户的查询。

同样地，

智能RAG路由器是旨在动态地将用户查询路由到适当的工具或数据源的系统，以增强大型语言模型（LLMs）的能力。这种路由器的主要目的是将检索机制与大型语言模型的生成优势相结合，以提供准确且具有丰富上下文的响应。

这种方法弥合了大型语言模型的静态知识（基于预先存在的数据训练）与对动态知识检索的需求（来自实时或特定领域的数据源）之间的差距。通过结合检索和生成，智能RAG路由器支持以下应用：

- 问答

- 数据分析

- 实时信息检索

- 推荐生成

![概念图片]()

来源：作者

##### 智能RAG路由器的架构

图中所示的架构详细展示了智能RAG路由器的运作方式。让我们分解其组件和流程：

1. **用户输入和查询处理**

- **用户输入**：用户提交查询，这是系统的入口点。它可以是一个问题、一条命令或对特定数据的请求。

- **查询**：用户输入被解析并格式化为系统可以解释的查询。

1. **检索代理**

- **检索代理**作为核心处理单元。它充当协调者，决定如何处理查询。它评估：

- 查询的意图。
- 所需信息的类型（结构化、非结构化、实时、推荐）。

1. **路由器**

- **路由器**确定处理查询的适当工具：

- **向量搜索**：使用语义嵌入检索相关文档或数据。
- **网络搜索**：从互联网获取实时信息。
- **推荐系统**：基于先前的用户交互或上下文相关性，推荐内容或结果。
- **文本转SQL**：将自然语言查询转换为SQL命令，以访问结构化数据库。

1. **工具**：此处列出的工具是模块化且专门化的：

- **向量搜索A和B**：旨在搜索语义嵌入，以匹配向量形式的内容，非常适合非结构化数据，如文档、PDF或书籍。

- **网络搜索**：访问外部的实时网络数据。

- **推荐系统**：利用AI模型提供针对用户的建议。

1. **数据源**：系统连接到各种数据源：

- 结构化数据库：用于组织良好的信息（例如，基于SQL的系统）。

- 非结构化来源：PDF、书籍、研究论文等。

- 外部存储库：用于语义搜索、推荐和实时网络查询。

1. **大型语言模型整合**：一旦检索到数据，就会将其输入到大型语言模型中：

- 大型语言模型将检索到的信息与其生成能力相结合，创建连贯的、人类可读的响应。

1. **输出**：最终响应以清晰且可操作的格式发送回用户。

##### 智能RAG路由器的类型

以下是智能RAG路由器的类型：

##### 1. 单一智能RAG路由器

![概念图片]()

来源：作者

- 在这种设置中，有**一个统一的代理**负责所有路由、检索和决策任务。

- 更简单且更集中，适用于数据源或工具有限的系统。

- 用例：具有单一类型查询的应用程序，例如检索特定文档或处理基于SQL的请求。

在单一智能RAG路由器中：

1. **查询提交**：用户提交查询，由单个**检索代理**处理。

1. **通过单一代理路由**：**检索代理**评估查询，并将其传递给**单个路由器**，路由器决定使用哪种工具（例如向量搜索、网络搜索、文本转SQL、推荐系统）。

1. **工具访问**：

- 路由器根据需要将查询连接到一个或多个工具。

- 每个工具从其各自的数据源获取数据：

- **文本转SQL**与PostgreSQL或MySQL等数据库交互，处理结构化查询。
- **语义搜索**从PDF、书籍或非结构化来源检索数据。
- **网络搜索**获取实时在线信息。
- **推荐系统**根据上下文或用户档案提供建议。

1. **大型语言模型整合**：检索后，数据被传递到**大型语言模型**，该模型将其与生成能力相结合以生成响应。

1. **输出**：响应以清晰、可操作的格式返回给用户。

这种方法集中化，对于数据源和工具有限的简单用例非常高效。

##### 2. 多个智能RAG路由器

![概念图片]()

来源：作者

- 这种架构涉及**多个代理**，每个代理处理特定类型的任务或查询。

- 更模块化和可扩展，适用于具有多种工具和数据源的复杂系统。

- 用例：多功能系统，满足各种用户需求，例如跨多个领域的研究、分析和决策。

在多个智能RAG路由器中：

1. **查询提交**：用户提交查询，最初由**检索代理**处理。

1. **分布式检索代理**：系统采用**多个检索代理**，而非单个路由器，每个代理专门处理特定类型的任务。例如：

- **检索代理1**可能处理基于SQL的查询。

- **检索代理2**可能专注于语义搜索。

- **检索代理3**可能优先处理推荐或网络搜索。

1. **工具的独立路由器**：每个**检索代理**根据其范围，将查询路由到共享池中的指定工具（例如向量搜索、网络搜索等）。

1. **工具访问和数据检索**：

- 每个工具根据其检索代理的要求从相应的来源获取数据。

- 多个代理可以并行操作，确保高效处理各种查询类型。

1. **大型语言模型整合和合成**：所有检索到的数据都被传递到**大型语言模型**，该模型综合信息并生成连贯的响应。

1. **输出**：最终处理后的响应返回给用户。

这种方法模块化且可扩展，适用于具有多种工具和高查询量的复杂系统。

智能RAG路由器结合了智能决策、强大的检索机制和大型语言模型，创建了一个多功能的查询-响应系统。该架构将用户查询最佳地路由到适当的工具和数据源，确保高度的相关性和准确性。无论是使用单一还是多个路由器设置，设计都取决于系统的复杂性、可扩展性需求和应用要求。

#### 2. 查询规划智能RAG

查询规划智能RAG（检索增强生成）是一种方法，旨在通过跨不同数据源利用多个可并行的子查询，高效处理复杂查询。这种方法结合了智能查询划分、分布式处理和响应合成，以提供准确且全面的结果。

![概念图片]()

来源：作者

##### 查询规划智能RAG的核心组件

核心组件如下：

1. **用户输入和查询提交**

- **用户输入**：用户向系统提交查询或请求。

- 输入查询经过处理后传递到下游进行进一步处理。

1. **查询规划器**：**查询规划器**是协调过程的核心组件。它：

- 解释用户提供的**查询**。

- 为下游组件生成适当的**提示**。

- 决定调用哪些工具（查询引擎）来回答查询的特定部分。

1. **工具**

- **工具**是专门的管道（例如**RAG管道**），包含查询引擎，例如：

- **查询引擎1**
- **查询引擎2**

- 这些管道负责从外部知识源（例如数据库、文档或API）检索相关信息或上下文。

- 检索到的信息被发送回查询规划器进行整合。

1. **大型语言模型（LLM）**

- **大型语言模型**作为复杂推理、自然语言理解和响应生成的合成引擎
##### Key Highlights 核心亮点
- **Modular Design**: The architecture allows for flexibility in tool selection and integration.
**模块化设计**：该架构在工具选择和集成方面具有灵活性。
- **Efficient Query Planning**: The Query Planner acts as an intelligent intermediary, optimizing which components are used and in what order.
**高效的查询规划**：查询规划器充当智能中介，优化组件的使用及其顺序。
- **Retrieval-Augmented Generation**: By leveraging RAG pipelines, the system enhances the LLM’s knowledge with up-to-date and domain-specific information.
**检索增强生成**：通过利用RAG管道，该系统利用最新的特定领域信息增强大语言模型的知识。
- **Iterative Interaction**: The Query Planner ensures iterative collaboration between the tools and the LLM, refining the response progressively.
**迭代交互**：查询规划器确保工具与大语言模型之间进行迭代协作，逐步优化响应。


#### 3. Adaptive RAG 3. 自适应检索增强生成
Adaptive Retrieval-Augmented Generation (Adaptive RAG) is a method that enhances the flexibility and efficiency of large language models (LLMs) by tailoring the query handling strategy to the complexity of the incoming query.
自适应检索增强生成（Adaptive RAG）是一种通过根据传入查询的复杂性定制查询处理策略，来提高大型语言模型（LLMs）的灵活性和效率的方法。

##### Key Idea of Adaptive RAG 自适应检索增强生成的核心思想
Adaptive RAG dynamically chooses between different strategies for answering questions—ranging from simple single-step approaches to more complex multi-step or even no-retrieval processes—based on the **complexity** of the query. This selection is facilitated by a **classifier**, which analyzes the query’s nature and determines the optimal approach.
自适应检索增强生成根据查询的**复杂性**，在不同的问答策略之间动态选择——从简单的单步方法到更复杂的多步方法，甚至是无检索过程。这种选择由**分类器**辅助完成，分类器会分析查询的性质并确定最佳方法。

![notion image]()
Source:[Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity]()
来源：[《自适应检索增强生成：通过问题复杂性学习适应检索增强大型语言模型》]()

##### Comparison with Other Methods 与其他方法的比较
Here’s the comparison with single-step, multi-step and adaptive approach:
以下是与单步、多步和自适应方法的比较：

1. **Single-Step Approach 单步方法**
- **How it Works**: For both simple and complex queries, a single round of retrieval is performed, and an answer is generated directly from the retrieved documents.
**工作原理**：无论是简单查询还是复杂查询，都只执行一轮检索，并直接根据检索到的文档生成答案。
- **Limitation**:
**局限性**：
- Works well for **simple queries** like “When is the birthday of Michael F. Phelps?” but fails for **complex queries** like “What currency is used in Billy Giles’ birthplace?” due to insufficient intermediate reasoning.
适用于**简单查询**，如“迈克尔·菲尔普斯的生日是什么时候？”，但对于**复杂查询**，如“比利·贾尔斯的出生地使用什么货币？”，由于中间推理不足而无法给出正确答案。
- This results in **inaccurate answers** for complex cases.
这导致在复杂情况下产生**不准确的答案**。

2. **Multi-Step Approach 多步方法**
- **How it Works**: Queries, whether simple or complex, go through multiple rounds of retrieval, generating intermediate answers iteratively to refine the final response.
**工作原理**：无论查询是简单还是复杂，都要经过多轮检索，迭代生成中间答案以优化最终响应。
- **Limitation**:
**局限性**：
- Though powerful, it introduces unnecessary **computational overhead** for simple queries. For example, repeatedly processing “When is the birthday of Michael F. Phelps?” is inefficient and redundant.
尽管功能强大，但它给简单查询带来了不必要的**计算开销**。例如，反复处理“迈克尔·菲尔普斯的生日是什么时候？”既低效又多余。

3. **Adaptive Approach 自适应方法**
- **How it Works**: This approach uses a **classifier** to determine the query’s complexity and choose the appropriate strategy:
**工作原理**：这种方法使用**分类器**来确定查询的复杂性并选择合适的策略：
- **Straightforward Query**: Directly generate an answer without retrieval (e.g., “Paris is the capital of what?”).
**简单直接的查询**：无需检索直接生成答案（例如，“巴黎是哪个国家的首都？”）。
- **Simple Query**: Use a single-step retrieval process.
**简单查询**：使用单步检索过程。
- **Complex Query**: Employ multi-step retrieval for iterative reasoning and answer refinement.
**复杂查询**：采用多步检索进行迭代推理和答案优化。
- **Advantages 优势**
- Reduces unnecessary overhead for simple queries while ensuring high accuracy for complex ones.
减少简单查询的不必要开销，同时确保复杂查询的高准确性。
- Adapts flexibly to a variety of query complexities.
能灵活适应各种复杂程度的查询。

![notion image]()
Source: Author
来源：作者

##### Adaptive RAG Framework 自适应检索增强生成框架
- **Classifier Role**:
**分类器的作用**：
- A smaller language model predicts query complexity.
一个较小的语言模型预测查询的复杂性。
- It is trained using automatically labelled datasets, where the labels are derived from past model outcomes and inherent patterns in the data.
它使用自动标记的数据集进行训练，这些标签来自过去的模型结果和数据中固有的模式。

- **Dynamic Strategy Selection**:
**动态策略选择**：
- For simple or straightforward queries, the framework avoids wasting computational resources.
对于简单或直接的查询，该框架避免浪费计算资源。
- For complex queries, it ensures sufficient iterative reasoning through multiple retrieval steps.
对于复杂查询，它通过多步检索确保有足够的迭代推理。

##### RAG System Architecture Flow from LangGraph LangGraph的检索增强生成系统架构流程
Here’s another example of an adaptive RAG System architecture flow from LangGraph:
以下是来自LangGraph的自适应检索增强生成系统架构流程的另一个示例：

![notion image]()
Source:[Adaptive RAG]()
来源：[《自适应检索增强生成》]()

##### 1. Query Analysis 1. 查询分析
The process begins with analyzing the user query to determine the most appropriate pathway for retrieving and generating the answer.
该过程首先分析用户查询，以确定检索和生成答案的最合适路径。

- **Step 1: Route Determination 步骤1：路径确定**
- The query is classified into categories based on its relevance to the existing index (database or vector store).
根据查询与现有索引（数据库或向量存储）的相关性将其分类。
- **[Related to Index]**: If the query is aligned with the indexed content, it is routed to the RAG module for retrieval and generation.
**[与索引相关]**：如果查询与索引内容一致，则将其路由到检索增强生成模块进行检索和生成。
- **[Unrelated to Index]**: If the query is outside the scope of the index, it is routed for a **web search** or another external knowledge source.
**[与索引无关]**：如果查询超出索引范围，则将其路由到**网络搜索**或其他外部知识源。

- **Optional Routes**: Additional pathways can be added for more specialized scenarios, such as domain-specific tools or external APIs.
**可选路径**：可以为更专业的场景添加额外路径，例如特定领域工具或外部API。

##### 2. RAG + Self-Reflection 2. 检索增强生成 + 自反思
If the query is routed through the **RAG module**, it undergoes an iterative, self-reflective process to ensure high-quality and accurate responses.
如果查询通过**检索增强生成模块**路由，则会经历一个迭代的自反思过程，以确保响应的高质量和准确性。

1. **Retrieve Node 检索节点**
- Retrieves documents from the indexed database based on the query.
根据查询从索引数据库中检索文档。
- These documents are passed to the next stage for evaluation.
这些文档被传递到下一阶段进行评估。

2. **Grade Node 评分节点**
- Assesses the relevance of the retrieved documents.
评估检索到的文档的相关性。
- Decision Point:
决策点：
- If documents are relevant: Proceed to generate an answer.
如果文档相关：继续生成答案。
- If documents are irrelevant: The query is rewritten for better retrieval and the process loops back to the retrieve node.
如果文档不相关：重写查询以更好地进行检索，然后流程返回到检索节点。

3. **Generate Node 生成节点**
- Generates a response based on the relevant documents.
根据相关文档生成响应。
- The generated response is evaluated further to ensure accuracy and relevance.
对生成的响应进行进一步评估，以确保其准确性和相关性。

4. **Self-Reflection Steps 自反思步骤**
- **Does it answer the question?**
**它回答问题了吗？**
- If yes: The process ends, and the answer is returned to the user.
如果是：流程结束，答案返回给用户。
- If no: The query undergoes another iteration, potentially with additional refinements.
如果否：查询进行另一轮迭代，可能会进行额外的优化。

- **Hallucinations Check 幻觉检查**
- If hallucinations are detected (inaccuracies or made-up facts): The query is rewritten, or additional retrieval is triggered for correction.
如果检测到幻觉（不准确或虚构的事实）：重写查询，或触发额外的检索进行纠正。

5. **Re-write Question Node 重写问题节点**
- Refines the query for better retrieval results and loops it back into the process.
优化查询以获得更好的检索结果，并将其返回到流程中。
- This ensures that the model adapts dynamically to handle edge cases or incomplete data.
这确保模型能动态适应以处理边缘情况或不完整数据。

##### 3. Web Search for Unrelated Queries 3. 无关查询的网络搜索
If the query is deemed unrelated to the indexed knowledge base during the Query Analysis stage:
如果在查询分析阶段确定查询与索引知识库无关：
- **Generate Node with Web Search**: The system directly performs a web search and uses the retrieved data to generate a response.
**带网络搜索的生成节点**：系统直接执行网络搜索，并使用检索到的数据生成响应。
- **Answer with Web Search**: The generated response is delivered directly to the user.
**带网络搜索的答案**：生成的响应直接传递给用户。

In essence, **Adaptive RAG** is an intelligent and resource-aware framework that improves response quality and computational efficiency by leveraging tailored query strategies.
本质上，**自适应检索增强生成**是一个智能且具有资源感知能力的框架，它通过利用定制的查询策略来提高响应质量和计算效率。


#### 4. Agentic Corrective RAG 4. 智能体纠正型检索增强生成
A low-quality retriever often introduces significant irrelevant information, hindering generators from accessing accurate knowledge and potentially leading them astray.
低质量的检索器往往会引入大量不相关的信息，阻碍生成器获取准确的知识，并可能导致其误入歧途。

![notion image]()
Source:[Corrective Retrieval Augmented Generation]()
来源：[《纠正性检索增强生成》]()

Likewise, here are some issues with RAG:
同样，检索增强生成存在一些问题：

##### Issues with Traditional RAG (Retrieval-Augmented Generation) 传统检索增强生成的问题
- **Low-Quality Retrievers**: These can introduce a substantial amount of irrelevant or misleading information. This not only impedes the model’s ability to acquire accurate knowledge but also increases the risk of hallucinations during generation.
**低质量检索器**：它们会引入大量不相关或误导性的信息。这不仅阻碍模型获取准确知识的能力，还会增加生成过程中出现幻觉的风险。
- **Undiscriminating Utilization**: Many conventional RAG systems indiscriminately incorporate all retrieved documents, irrespective of their relevance. This leads to the integration of unnecessary or incorrect data.
**不加区分的利用**：许多传统的检索增强生成系统不加区分地整合所有检索到的文档，不管其相关性如何。这导致不必要或不正确的数据被整合。
- **Inefficient Document Processing**: Current RAG methods often treat complete documents as knowledge sources, even though large portions of retrieved text may be irrelevant, diluting the quality of generation.
**低效的文档处理**：当前的检索增强生成方法通常将完整文档视为知识源，尽管检索到的文本中很大一部分可能不相关，从而降低生成质量。
- **Dependency on Static Corpora**: Retrieval systems that rely on fixed databases can only provide limited or suboptimal documents, failing to adapt to dynamic information needs.
**对静态语料库的依赖**：依赖固定数据库的检索系统只能提供有限或次优的文档，无法适应动态的信息需求。

##### Corrective RAG (CRAG) 纠正性检索增强生成
CRAG aims to address the above issues by introducing mechanisms to self-correct retrieval results, enhancing document utilization, and improving generation quality.
纠正性检索增强生成旨在通过引入自我纠正检索结果、提高文档利用率和改善生成质量的机制来解决上述问题。

##### Key Features: 主要特点：
- **Retrieval Evaluator**: A lightweight component to assess the relevance and reliability of retrieved documents for a query. This evaluator assigns a confidence degree to the documents.
**检索评估器**：一个轻量级组件，用于评估检索到的文档与查询的相关性和可靠性。该评估器为文档分配置信度。
- **Triggered Actions**: Depending on the confidence score, different retrieval actions—Correct, Ambiguous, or Incorrect—are triggered.
**触发动作**：根据置信度得分，触发不同的检索动作——正确、模糊或错误。
- **Web Searches for Augmentation**: Recognizing the limitations of static databases, CRAG integrates large-scale web searches to supplement and improve retrieval results.
**用于增强的网络搜索**：认识到静态数据库的局限性，纠正性检索增强生成整合了大规模网络搜索，以补充和改进检索结果。
- **Decompose-Then-Recompose Algorithm**: This method selectively extracts key information from retrieved documents, discarding irrelevant sections to refine the input to the generator.
**分解-再重组算法**：这种方法从检索到的文档中选择性地提取关键信息，丢弃不相关的部分，以优化生成器的输入。
- **Plug-and-Play Capability**: CRAG can seamlessly integrate with existing RAG-based systems without requiring extensive modifications.
**即插即用能力**：纠正性检索增强生成可以与现有的基于检索增强生成的系统无缝集成，无需大量修改。

##### Corrective RAG Workflow 纠正性检索增强生成工作流程
![notion image]()
Source: Dipanjan Sarkar
来源：迪潘詹·萨卡尔

##### Step 1: Retrieval 步骤1：检索
Retrieve context documents from a vector database using the input query. This is the initial step to gather potentially relevant information.
使用输入查询从向量数据库中检索上下文文档。这是收集潜在相关信息的初始步骤。

##### Step 2: Relevance Check 步骤2：相关性检查
Use a **Large Language Model (LLM)** to evaluate whether the retrieved documents are relevant to the input query. This ensures the retrieved documents are appropriate for the question.
使用**大型语言模型（LLM）** 评估检索到的文档是否与输入查询相关。这确保检索到的文档适合该问题。

##### Step 3: Validation of Relevance 步骤3：相关性验证
- If **all documents are relevant (Correct)**, no specific corrective action is required, and the process can proceed to generation.
如果**所有文档都相关（正确）**，则不需要特定的纠正措施，流程可以进入生成阶段。
- If **ambiguity** or **incorrectness** is detected, proceed to Step 4.
如果检测到**模糊性**或**不正确性**，则进入步骤4。

##### Step 4: Query Rephrasing and Search 步骤4：查询重述和搜索
If documents are ambiguous or incorrect:
如果文档模糊或不正确：
1. Rephrase the query based on insights from the LLM.
根据大语言模型的见解重述查询。
2. Conduct a web search or alternative retrieval to fetch updated and accurate context information.
进行网络搜索或替代检索，以获取更新和准确的上下文信息。

##### Step 5: Response Generation 步骤5：响应生成
Send the refined query and relevant context documents (corrected or original) to the LLM for generating the final response. The type of response depends on the quality of retrieved or corrected documents:
将优化后的查询和相关的上下文文档（纠正后的或原始的）发送给大语言模型，以生成最终响应。响应的类型取决于检索到的或纠正后的文档的质量：
- **Correct**: Use the query with retrieved documents.
**正确**：将查询与检索到的文档一起使用。
- **Ambiguous**: Combine original and new context documents.
**模糊**：结合原始和新的上下文文档。
- **Incorrect**: Use the corrected query and newly retrieved documents for generation.
**不正确**：使用纠正后的查询和新检索到的文档进行生成。

This workflow ensures high accuracy in responses through iterative correction and refinement.
该工作流程通过迭代纠正和优化确保响应的高准确性。

##### Agentic Corrective RAG System Workflow 智能体纠正型检索增强生成系统工作流程
The idea is to couple a RAG system with a few checks in place and perform web searches if there is a lack of relevant context documents to the given user query as follows:
其理念是将检索增强生成系统与一些检查相结合，如果缺乏与给定用户查询相关的上下文文档，则执行网络搜索，具体如下：

![notion image]()
Source: Dipanjan Sarkar
来源：迪潘詹·萨卡尔

1. **Question**: This is the input from the user, which starts the process.
**问题**：这是来自用户的输入，启动整个流程。
2. **Retrieve (Node
3. 
# 自适应rag
)：系统查询向量数据库，检索可能回答用户问题的上下文文档。
3. **Grade (Node)**：大型语言模型（LLM）评估检索到的文档是否与查询相关。
- 如果所有文档都被认为相关，系统继续生成答案。
- 如果有任何文档不相关，系统转而重述查询并尝试网络搜索。

##### 步骤1 – 检索节点
系统根据查询从向量数据库中检索文档，提供上下文或答案。

##### 步骤2 – 评分节点
大型语言模型评估文档相关性：
- **全部相关**：进入答案生成阶段。
- **部分不相关**：标记问题并优化查询。

##### 评分后的分支场景
- **步骤3A – 生成答案节点**：如果所有文档都相关，大型语言模型快速生成响应。
- **步骤3B – 重写查询节点**：对于不相关的结果，重述查询以获得更好的检索效果。
- **步骤3C – 网络搜索节点**：通过网络搜索收集额外的上下文信息。
- **步骤3D – 生成答案节点**：使用优化后的查询和新数据生成答案。

我们可以通过将特定功能步骤作为图中的节点并使用LangGraph来实现，从而构建出智能体纠正型检索增强生成系统。节点中的关键步骤包括向大型语言模型发送提示以执行特定任务，详见以下详细工作流程：

![notion image]()
Source:[A Comprehensive Guide to Building Agentic RAG Systems with LangGraph]()
来源：[《使用LangGraph构建智能体检索增强生成系统的综合指南》]()

**智能体纠正型检索增强生成架构**通过纠正步骤增强检索增强生成（RAG），以获得准确答案：
1. **查询与初始检索**：用户查询从向量数据库中检索上下文文档。
2. **文档评估**：**大型语言模型评分提示**评估每个文档的相关性（是或否）。
3. **决策节点**：
   - **全部相关**：直接进入答案生成阶段。
   - **存在不相关文档**：触发纠正步骤。
4. **查询重述**：**大型语言模型重述提示**重写查询，以优化网络检索效果。
5. **额外检索**：通过网络搜索检索更优的上下文文档。
6. **响应生成**：**检索增强生成提示**仅使用经过验证的上下文生成答案。

简而言之，纠正性检索增强生成（CRAG）的作用如下：
- **错误纠正**：该架构通过识别不相关文档并检索更优文档，迭代提高上下文准确性。
- **智能体行为**：系统根据大型语言模型的评估动态调整其动作（例如重述查询、进行网络搜索）。
- **真实性保证**：通过将生成步骤锚定在经过验证的上下文文档上，该框架最大限度地降低了生成幻觉或错误响应的风险。


#### 5. Self-Reflective RAG 5. 自反思检索增强生成
Self-reflective RAG (Retrieval-Augmented Generation) is an advanced approach in natural language processing (NLP) that combines the capabilities of retrieval-based methods with generative models while adding an additional layer of self-reflection and logical reasoning. For instance, self-reflective RAG helps in retrieval, re-writing questions, discarding irrelevant or hallucinated documents and re-try retrieval. In short, it was introduced to capture the idea of using an LLM to self-correct poor-quality retrieval and/or generations.
自反思检索增强生成（Self-reflective RAG）是自然语言处理（NLP）中的一种高级方法，它结合了基于检索的方法和生成模型的能力，同时增加了一层自反思和逻辑推理。例如，自反思检索增强生成有助于检索、重写问题、丢弃不相关或存在幻觉的文档以及重新尝试检索。简而言之，引入它是为了实现利用大型语言模型自我纠正低质量检索和/或生成结果的理念。

##### Key Components of Self Route 自路由的关键组件
- **Decision-making by LLMs**: Queries are evaluated to determine if they can be answered with the given retrieved context.
**大型语言模型的决策**：对查询进行评估，以确定是否可以利用给定的检索上下文来回答。
- **Routing**: If a query is answerable, response is generated immediately. Otherwise, it is routed to a long-context model with the full context documents to generate the response.
**路由**：如果查询可以被回答，则立即生成响应。否则，将其路由到具有完整上下文文档的长上下文模型以生成响应。
- **Efficiency and Accuracy**: This design balances cost-efficiency (avoiding unnecessary computation cost and time) and accuracy (leveraging long-context models only when needed).
**效率与准确性**：这种设计平衡了成本效益（避免不必要的计算成本和时间）和准确性（仅在需要时利用长上下文模型）。

##### Key Features of Self-RAG 自反思检索增强生成的主要特点
1. **On-Demand Adaptive Retrieval**：
**按需自适应检索**：
- Unlike traditional RAG methods, which retrieve a fixed set of passages beforehand, SELF-RAG dynamically decides whether retrieval is necessary based on the ongoing generation process.
与传统的检索增强生成方法预先检索固定数量的段落不同，自反思检索增强生成根据正在进行的生成过程动态决定是否需要检索。
- This decision is made using **reflection tokens**, which act as signals during the generation process.
这一决定是通过**反思令牌**做出的，反思令牌在生成过程中充当信号。

![notion image]()
Source:[SELF-RAG: LEARNING TO RETRIEVE, GENERATE, AND CRITIQUE THROUGH SELF-REFLECTION]()
来源：[《自反思检索增强生成：通过自我反思学习检索、生成和评判》]()

2. **Reflection Tokens**： These are special tokens integrated into the LLMs workflow, serving two purposes:
**反思令牌**：这些是集成到大型语言模型工作流程中的特殊令牌，具有两个用途：
- **Retrieval Tokens**： Indicate whether more information is needed from external sources.
**检索令牌**：指示是否需要从外部来源获取更多信息。
- **Critique Tokens**： Self-evaluate the generated text to assess quality, relevance, or completeness.
**评判令牌**：对生成的文本进行自我评估，以评估其质量、相关性或完整性。
- By using these tokens, the LLMs can decide when to retrieve and ensure generated text aligns with cited sources.
通过使用这些令牌，大型语言模型可以决定何时进行检索，并确保生成的文本与引用的来源一致。

3. **Self-Critique for Quality Assurance**：
**用于质量保证的自我评判**：
- The LLM critiques its own outputs using the generated critique tokens. These tokens validate aspects like relevance, support, or completeness of the generated segments.
大型语言模型使用生成的评判令牌对自己的输出进行评判。这些令牌验证生成片段的相关性、支持性或完整性等方面。
- This mechanism ensures that the final output is not only coherent but also well-supported by retrieved evidence.
这种机制确保最终输出不仅连贯，而且有检索到的证据充分支持。

4. **Controllable and Flexible**： Reflection tokens allow the model to adapt its behavior during inference, making it suitable for diverse tasks, such as answering questions requiring retrieval or generating self-contained outputs without retrieval.
**可控制且灵活**：反思令牌允许模型在推理过程中调整其行为，使其适用于各种任务，例如回答需要检索的问题或生成无需检索的独立输出。

5. **Improved Performance**： By combining dynamic retrieval and self-critique, SELF-RAG surpasses standard RAG models and large language models (LLMs) in generating high-quality outputs that are better supported by evidence.
**性能提升**：通过结合动态检索和自我评判，自反思检索增强生成在生成有更好证据支持的高质量输出方面，超过了标准的检索增强生成模型和大型语言模型（LLMs）。

Basic RAG flows involve an LLM generating outputs based on retrieved documents. Advanced RAG approaches, like routing, allow the LLM to select different retrievers based on the query. Self-reflective RAG adds feedback loops, re-generating queries or re-retrieving documents as needed. State machines, ideal for such iterative processes, define steps (e.g., retrieval, query refinement) and transitions, enabling dynamic adjustments like re-querying when retrieved documents are irrelevant.
基本的检索增强生成流程包括大型语言模型根据检索到的文档生成输出。先进的检索增强生成方法（如路由）允许大型语言模型根据查询选择不同的检索器。自反思检索增强生成增加了反馈循环，根据需要重新生成查询或重新检索文档。状态机非常适合这种迭代过程，它定义了步骤（例如检索、查询优化）和转换，能够进行动态调整，例如当检索到的文档不相关时重新查询。

![notion image]()
Source: LangGraph
来源：LangGraph

##### The Architecture of Self-reflective RAG 自反思检索增强生成的架构
![notion image]()
Source: Author
来源：作者

我设计了一个自反思检索增强生成（Retrieval-Augmented Generation）架构。以下是其流程和组件：
1. 流程从查询（绿色所示）开始
2. **第一个决策点**：“是否需要检索？”
   - 如果不需要：查询直接进入大型语言模型进行处理
   - 如果需要：系统进入检索步骤
3. **知识库集成**
   - 知识库（紫色所示）与“相关文档检索”步骤相连
   - 该检索过程提取可能与回答查询相关的信息
4. **相关性评估**
   - 检索到的文档经过“评估相关性”步骤
   - 文档被分类为“相关”或“不相关”
   - 不相关的文档触发另一次检索尝试
   - 相关的文档被传递给大型语言模型
5. **大型语言模型处理**
   - 大型语言模型（黄色所示）处理查询以及相关的检索信息
   - 生成初始答案（绿色所示）
6. **验证过程**
   - 系统执行**幻觉检查**：确定生成的答案是否与提供的上下文一致（避免无根据或虚构的响应）。
7. **自我反思**
   - “评判生成的响应”步骤（蓝色所示）对答案进行评估
   - 这是该架构的“自反思”部分
   - 如果答案不令人满意，系统可以触发查询重写并重新开始流程
8. **最终输出**：一旦生成“准确答案”，它就成为最终输出

##### Grading and Generation Decisions 评分与生成决策
- **Retrieve Node**： Handles the initial retrieval of documents.
**检索节点**：处理文档的初始检索。
- **Grade Documents**： Assesses the quality and relevance of the retrieved documents.
**文档评分**：评估检索到的文档的质量和相关性。
- **Transform Query**： If no relevant documents are found, the query is adjusted for re-retrieval.
**转换查询**：如果未找到相关文档，则调整查询以重新检索。
- **Generation Process**：
**生成过程**：
- Decides whether to generate an answer directly based on the retrieved documents.
决定是否直接根据检索到的文档生成答案。
- Uses **conditional edges** to iteratively refine the answer until it is deemed useful.
使用**条件边**迭代优化答案，直到认为其有用为止。

##### Workflow of Traditional RAG and Self-Rag 传统检索增强生成与自反思检索增强生成的工作流程
![notion image]()
Source:[SELF-RAG: LEARNING TO RETRIEVE, GENERATE, AND CRITIQUE THROUGH SELF-REFLECTION]()
来源：[《自反思检索增强生成：通过自我反思学习检索、生成和评判》]()

以下是使用示例提示“美国各州的名字是怎么来的？”展示的传统检索增强生成和自反思检索增强生成的工作流程：

##### Traditional RAG Workflow 传统检索增强生成工作流程
1. **步骤1 –** 检索K个文档：检索特定文档，例如：
   - “在50个州中，有11个是以个人名字命名的”
   - “各州的热门名字。在得克萨斯州，艾玛是一个热门的婴儿名字”
   - “加利福尼亚是以一本西班牙书中的虚构岛屿命名的”
2. **步骤2 –** 利用检索到的文档生成：
   - 将原始提示（“美国各州的名字是怎么来的？”）与所有检索到的文档结合
   - 语言模型综合所有信息生成一个响应
   - 这可能导致矛盾或混合不相关的信息（例如声称加利福尼亚是以克里斯托弗·哥伦布的名字命名的）

##### Self-RAG Workflow 自反思检索增强生成工作流程
1. **步骤1 –** 按需检索：
   - 从提示“美国各州的名字是怎么来的？”开始
   - 初步检索关于州名来源的信息
2. **步骤2 –** 并行生成片段：
   - 创建多个独立的片段，每个片段都有自己的：
     - 提示 + 检索到的信息
     - 事实验证
     - 示例：
       - 片段1：关于以人名命名的州的事实
       - 片段2：关于得克萨斯州命名的信息
       - 片段3：关于加利福尼亚州名字起源的详细信息
3. **步骤3 –** 评判与选择：
   - 评估所有生成的片段
   - 挑选最准确/相关的片段
   - 必要时可以检索额外信息
   - 将经过验证的信息整合到最终响应中

##### 自反思检索增强生成的主要改进在于
- 将响应分解为更小的、可验证的部分
- 独立验证每个部分
- 必要时可以动态检索更多信息
- 仅将经过验证的信息组合到最终响应中

如底部示例“写一篇关于你最棒的暑假的文章”所示：
- 传统检索增强生成仍然会不必要地尝试检索文档
- 自反思检索增强生成认识到不需要检索，并直接根据个人经验生成内容。


#### 6. Speculative RAG 6. 推测性检索增强生成
Speculative RAG is a smart framework designed to make large language models (LLMs) both **faster** and **more accurate** when answering questions. It does this by splitting the work between two kinds of language models:
推测性检索增强生成是一个智能框架，旨在使大型语言模型（LLMs）在回答问题时既**更快**又**更准确**。它通过将工作分配给两种语言模型来实现这一点：
1. A **small, specialized model** that drafts potential answers quickly.
一个**小型的、专门的模型**，可快速起草潜在答案。
2. A **large, general-purpose model** that double-checks these drafts and picks the best one.
一个**大型的、通用的模型**，用于仔细检查这些草稿并挑选出最佳的一个。

![notion image]()
Source: Author
来源：作者

##### Why Do We Need Speculative RAG? 为什么我们需要推测性检索增强生成？
When you ask a question, especially one that needs precise or up-to-date information (like _“What are the latest features of the new iPhone?”_ ), regular LLMs often struggle because:
当你提出一个问题，特别是需要精确或最新信息的问题（如“新款iPhone的最新功能是什么？”）时，普通的大型语言模型往往难以应对，原因如下：
1. **They can “hallucinate”**： This means they might confidently give answers that are wrong or made up.
**它们可能会“产生幻觉”**：这意味着它们可能会自信地给出错误或虚构的答案。
2. **They rely on outdated knowledge**： If the model wasn’t trained on recent data, it can’t help with newer facts.
**它们依赖过时的知识**：如果模型没有使用最新数据进行训练，就无法提供最新的事实。
3. **Complex reasoning takes time**： If there’s a lot of information to process (like long documents), the model might take forever to respond.
**复杂推理需要时间**：如果有大量信息需要处理（如长文档），模型可能需要很长时间才能做出响应。

That’s where Retrieval-Augmented Generation (RAG) steps in. RAG retrieves real-time, relevant documents (like from a database or search engine) and uses them to generate answers. But here’s the issue: RAG can still be **slow** and **resource-heavy** when handling lots of data.
这就是检索增强生成（RAG）发挥作用的地方。检索增强生成检索实时的、相关的文档（如来自数据库或搜索引擎），并利用它们生成答案。但问题是：当处理大量数据时，检索增强生成仍然可能**很慢**且**消耗大量资源**。

Speculative RAG fixes this by adding **specialized teamwork**： (1) a specialist RAG drafter, and (2) a generalist RAG verifier
推测性检索增强生成通过增加**专门的协作**来解决这个问题：（1）一个专业的检索增强生成起草者，（2）一个通用的检索增强生成验证者

##### How Speculative RAG Works? 推测性检索增强生成如何工作？
Imagine Speculative RAG as a two-person team solving a puzzle:
可以将推测性检索增强生成想象成一个两人团队解决谜题：
1. **Step 1: Gather Clues** A “retriever” goes out and fetches documents with information related to your question. For example, if you ask, _“Who played Doralee Rhodes in the 1980 movie Nine to Five?”_ , it pulls articles about the movie and maybe the musical.
**步骤1：收集线索** “检索器”出去获取与你的问题相关的信息文档。例如，如果你问“在1980年的电影《朝九晚五》中，谁扮演了多莉·罗兹？”，它会提取关于这部电影的文章，可能还有关于这部音乐剧的文章。
2. **Step 2: Drafting Answers (Small Model)** A smaller, faster language model (the **specialist drafter**) works on these documents. Its job is to:
**步骤2：起草答案（小型模型）** 一个更小、更快的语言模型

（**专业起草模型**）基于这些文档进行处理。其任务是：
- 快速生成多个可能的答案草稿
- 为每个草稿标注依据（即引用文档中的具体内容）

3. **步骤3：验证与选择（大型模型）** 一个更强大的大型语言模型（**通用验证模型**）接手工作：
- 检查所有草稿的准确性和相关性
- 对比不同草稿及其引用依据
- 选择最佳草稿，或结合多个草稿的优点生成最终答案
- 如果发现所有草稿都存在问题，可能会要求重新检索信息或重新起草

通过这种分工，推测性检索增强生成能够在保证答案质量的同时，大幅提高响应速度——小型模型负责快速产出，大型模型负责精准把控。

##### 推测性检索增强生成的核心优势
- **效率提升**：小型模型快速起草减少了大型模型的计算负担，加快了整体流程。
- **准确性更高**：大型模型的验证环节降低了错误答案或幻觉内容出现的概率。
- **资源优化**：避免了大型模型在简单任务上的不必要消耗，更合理地分配计算资源。
- **灵活性增强**：能够根据问题的难度动态调整起草和验证的强度，平衡速度与质量。

例如，在回答“2023年诺贝尔物理学奖得主是谁？”这个问题时：
- 小型起草模型会迅速检索相关新闻报道，生成几个可能的答案（包括得主姓名和贡献）。
- 大型验证模型会逐一核对这些答案，确认信息来源的可靠性，最终选出最准确的结果。

这种协作模式使得推测性检索增强生成在处理需要实时信息或复杂推理的问题时，表现得比传统检索增强生成或单纯的大型语言模型更高效、更可靠。


#### 7. Multi-Modal RAG 7. 多模态检索增强生成
传统的检索增强生成主要处理文本类数据（如文档、网页文字等），而**多模态检索增强生成**则将这一框架扩展到了更广泛的内容类型，能够同时处理和融合**文本、图像、音频、视频**等多种模态的信息，从而生成更丰富、更全面的响应。

##### 多模态检索增强生成的核心目标
多模态检索增强生成旨在解决传统文本检索增强生成的局限性——许多现实世界的问题需要结合非文本信息才能得到充分回答。例如：
- 当用户询问“这张图片里的建筑叫什么名字？”时，系统需要先理解图像内容，再结合文本知识给出答案。
- 当用户问“这段音频中提到的歌曲出自哪部电影？”时，系统需要处理音频信息并关联相关文本数据。

其核心目标是实现跨模态的信息检索与融合，让大型语言模型能够理解和运用多种类型的信息来回答问题或完成任务。

##### 多模态检索增强生成的关键组件
1. **多模态数据源**：包含文本、图像、音频、视频等多种类型的数据库或资源库。
2. **多模态嵌入模型**：将不同模态的内容转换为统一的向量表示（嵌入），使跨模态的比较和检索成为可能。例如：
   - 文本嵌入模型（如BERT）将文字转换为向量
   - 图像嵌入模型（如CLIP）将图像转换为向量
   - 音频嵌入模型（如Wav2Vec）将声音转换为向量
3. **多模态检索器**：根据用户查询（可能是文本、图像或其他类型），从多模态数据源中检索相关的跨模态信息。例如，用户输入一张动物图片，检索器能找到相关的文本描述、同类动物的视频等。
4. **多模态理解与生成模型**：能够处理和融合检索到的多模态信息，生成符合用户需求的响应（可能是文本、图像描述、甚至是生成新的图像或音频）。

##### 多模态检索增强生成的工作流程
1. **用户输入（多模态查询）**：用户可能输入文本问题（如“描述这张图片的内容”）、图像（如直接上传一张风景照并询问“这是哪里”）、音频片段（如一段音乐并询问“这首歌的歌词是什么”）等。
2. **查询转换**：将用户的多模态查询转换为统一的向量表示（通过对应的嵌入模型）。
3. **跨模态检索**：检索器在多模态数据库中查找与查询向量最相似的内容（可能是文本、图像、音频等）。例如，用户输入“展示太阳系行星的图片”，检索器会返回相关的图像及对应的文本说明。
4. **多模态信息融合**：系统将检索到的不同模态信息进行整合，提取关键内容。例如，结合图像中的视觉特征和文本中的描述性信息，形成对某一事物的完整理解。
5. **生成响应**：大型语言模型或多模态生成模型基于融合后的信息，生成符合用户需求的响应。响应的形式可以是文本（如回答问题）、图像标注、音频描述等。

##### 多模态检索增强生成的应用场景
- **图像问答**：用户上传图片并提问（如“这张照片拍摄于哪个城市？”），系统结合图像内容和文本知识给出答案。
- **视频内容分析**：检索视频中的关键片段，并生成文字摘要或解释（如“解释这段视频中实验的原理”）。
- **音频检索与解读**：根据一段音频（如鸟鸣、乐器声），检索相关的文本信息并解释（如“这是什么鸟的叫声？”）。
- **跨模态内容生成**：根据文本描述生成相关图像（如“生成一张‘未来城市’的图片”），或根据图像生成详细的文字描述。

##### 多模态检索增强生成的挑战
- **模态差异**：不同类型的数据（如文本和图像）在结构和特征上存在巨大差异，如何实现有效的跨模态嵌入和比对是一大难点。
- **信息融合难度**：将不同模态的信息无缝整合，避免出现冲突或遗漏，需要复杂的融合策略。
- **数据复杂性**：非文本数据（如视频、音频）通常体积更大，处理和存储的成本更高，对检索效率的要求也更严格。
- **生成一致性**：确保生成的响应与多模态输入的内容保持一致（如文本描述准确反映图像内容），避免出现跨模态的“幻觉”。

尽管存在挑战，多模态检索增强生成极大地扩展了人工智能系统处理信息的范围，使其能够更贴近现实世界中人类对多感官信息的理解和运用方式，为更丰富的人机交互场景提供了可能。


#### 8. Conclusion 8. 结论
检索增强生成（RAG）技术通过将大型语言模型的生成能力与外部知识检索相结合，有效解决了模型幻觉、知识过时等问题，已成为自然语言处理领域的重要框架。随着研究的深入，检索增强生成不断演化出更先进的形态：

- **自适应检索增强生成**通过动态调整策略，平衡了简单与复杂查询的处理效率；
- **智能体纠正型检索增强生成**引入自我纠正机制，提高了检索结果的准确性；
- **自反思检索增强生成**增加了自我评判和迭代优化的环节，进一步提升了响应质量；
- **推测性检索增强生成**通过分工协作，在保证质量的同时提升了效率；
- **多模态检索增强生成**则突破了文本限制，实现了跨类型信息的融合与运用。

这些进阶技术共同推动检索增强生成向更智能、更高效、更灵活的方向发展。未来，随着多模态融合能力的增强、检索策略的优化以及与智能体技术的深度结合，检索增强生成有望在更多领域（如教育、医疗、智能客服等）发挥关键作用，为用户提供更精准、更全面、更及时的信息服务。

无论是处理简单的事实查询，还是复杂的多步骤推理任务，检索增强生成及其衍生技术都展现出了强大的潜力，成为连接大型语言模型与外部知识的重要桥梁，推动人工智能系统向更可靠、更实用的方向迈进。
