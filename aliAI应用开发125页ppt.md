https://365.kdocs.cn/l/csh4lC6glPsd

<img width="901" height="476" alt="image" src="https://github.com/user-attachments/assets/4a52bc6c-8e9e-4a77-bad0-c7690b9b816f" />


<img width="897" height="500" alt="image" src="https://github.com/user-attachments/assets/a279df54-0c3c-4714-86f5-8d7c2694d0be" />


<img width="1065" height="613" alt="image" src="https://github.com/user-attachments/assets/3e98c2c8-18f7-49e8-8f4f-b532e5d73074" />

一个ai agent其实是一个系统，包括一下三个的核心的内容

使用大语言模型llm来推理的

可以通过工具执行各类的行动

执行思考think-》执行action->自省observe->纠错，不仅是重复思考到自省的持续改进这样的一个循环的

# 推理模式-ReAct模式

推理reason

使用llm分析，理解上下文，明确用户任务目标

行动Act

基于推理的结果执行对应的行动

观测observe

评估执行行动后得到的结果

自省reflect

评估是否需要继续推理-》行动->观察来得到更趋近于用户目标的结果

# sandbox

<img width="1077" height="596" alt="image" src="https://github.com/user-attachments/assets/bbf4c4e9-003a-4b90-9e05-5049d4527c04" />

<img width="1064" height="581" alt="image" src="https://github.com/user-attachments/assets/a29166e4-f74a-4e88-899a-83dcc9751e8d" />

# rl sandbox

<img width="1062" height="547" alt="image" src="https://github.com/user-attachments/assets/55b5caf2-93d7-4846-b770-459cfe30fb16" />

# browser use snadbox

<img width="1062" height="547" alt="image" src="https://github.com/user-attachments/assets/58e33550-31b7-417e-8ff6-450bd4393ccf" />

# code snadbox
<img width="1077" height="571" alt="image" src="https://github.com/user-attachments/assets/e8bbd698-e590-4816-880f-8e03870290da" />

# llm生产小木当中客户必然遇到的问题

<img width="1040" height="560" alt="image" src="https://github.com/user-attachments/assets/f34706e6-4673-4315-9b49-0f23bf5ee079" />

# mcp

模型上下文协议是一个开源的协议，让llm能够以标准化的方式连接到外部的数据员和工具，

<img width="967" height="531" alt="image" src="https://github.com/user-attachments/assets/9799acf9-bfa1-4e0e-9efb-ba92b990fa22" />


核心是通过自然语言描述清楚有哪些mcp server，承担什么作用，有哪些mcp tool，承担什么作用的，大语言模型通过推理去选择最合适的mcp server以及mpc tool，本质上提示词工程

<img width="1082" height="469" alt="image" src="https://github.com/user-attachments/assets/7e9697e0-109a-435c-b81d-da8dade51dfc" />



<img width="1063" height="535" alt="image" src="https://github.com/user-attachments/assets/39441123-d52f-49fe-b055-a980c6cadd7f" />



<img width="1071" height="594" alt="image" src="https://github.com/user-attachments/assets/f594d83e-b8b3-41c5-9a94-1fe1be0e6768" />

<img width="1079" height="583" alt="image" src="https://github.com/user-attachments/assets/c0c0a391-315f-45ee-9d2b-0344e868321d" />

<img width="1090" height="551" alt="image" src="https://github.com/user-attachments/assets/61e42c8f-61fc-4a14-9b34-45ec97dfc419" />

<img width="1083" height="580" alt="image" src="https://github.com/user-attachments/assets/0510b96b-2251-48b8-a0aa-80a49d70773d" />

<img width="1080" height="594" alt="image" src="https://github.com/user-attachments/assets/00fee6bb-b071-4261-96b2-10c9213f7553" />


<img width="1090" height="577" alt="image" src="https://github.com/user-attachments/assets/71ee123a-1251-46f4-af8f-a80a777e0b5e" />


<img width="1098" height="594" alt="image" src="https://github.com/user-attachments/assets/0d3105b2-e8ef-4eca-8e2c-965630d41dff" />


<img width="1096" height="597" alt="image" src="https://github.com/user-attachments/assets/c928915c-40cf-452e-8c44-9785d623e696" />

<img width="956" height="585" alt="image" src="https://github.com/user-attachments/assets/a9b766dc-3ad3-4114-bc81-e3a5f835b191" />


只关注统一公共数据源和定义mcp服务元数据规范，
- 私有化的mcp的registry
- 基于mcp服务名称以外的高级检索的能力
- mcp服务prompt的安全管控

<img width="1015" height="604" alt="image" src="https://github.com/user-attachments/assets/64e10424-4ae5-44e2-bab7-8f730f5ddd82" />


<img width="1030" height="525" alt="image" src="https://github.com/user-attachments/assets/80b9a06d-a4f8-4710-8bb9-a98406c40808" />

<img width="1078" height="597" alt="image" src="https://github.com/user-attachments/assets/ff6dac64-066f-4dd4-8bbd-b360d4e3970d" />

<img width="1017" height="586" alt="image" src="https://github.com/user-attachments/assets/a6ce53be-f6aa-48e3-a1e6-7bf337cb4e5c" />

<img width="974" height="569" alt="image" src="https://github.com/user-attachments/assets/2fc9f8c5-38a3-4224-8b3b-581ae630d35c" />


<img width="938" height="565" alt="image" src="https://github.com/user-attachments/assets/ba7a5c80-32d7-48bd-bca8-69c064021c2b" />

<img width="999" height="578" alt="image" src="https://github.com/user-attachments/assets/34683b4c-627b-427e-af6d-917b68f52ba8" />

# 观测指标

<img width="1080" height="593" alt="image" src="https://github.com/user-attachments/assets/1cc6c0cb-b81a-4cda-8da6-1bac993f1bc8" />

# python探针无侵入埋点实现原理

<img width="1037" height="554" alt="image" src="https://github.com/user-attachments/assets/ff0f96b3-e056-4c0d-96d0-4823fd1d3d55" />

<img width="1031" height="551" alt="image" src="https://github.com/user-attachments/assets/a88b698b-ecf8-44a0-81a2-a4a1b39f15d9" />

# 流失

<img width="1044" height="515" alt="image" src="https://github.com/user-attachments/assets/682f6a96-31a6-4ca7-9e81-b582d68ab709" />

<img width="1064" height="527" alt="image" src="https://github.com/user-attachments/assets/98049076-67fc-423e-897d-92436d767ba1" />

<img width="1034" height="598" alt="image" src="https://github.com/user-attachments/assets/4c04eaad-e415-4ca2-a20d-8fdbd6790cfa" />

<img width="1011" height="552" alt="image" src="https://github.com/user-attachments/assets/8bf17fc0-49df-4bab-b816-61d43f93abfd" />

<img width="1435" height="634" alt="image" src="https://github.com/user-attachments/assets/c17ab5b4-d21f-4c19-9904-0d0055ee5d16" />

<img width="1450" height="458" alt="image" src="https://github.com/user-attachments/assets/d824f7be-cb59-49c6-b18c-b9543ff5dbe0" />


