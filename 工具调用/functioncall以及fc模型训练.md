query

执行完之后返回给大模型的，也可以继续执行工具的，reAct:reason+工具+观察+结果的

当然可以！我们来详细解释一下你提供的这段代码中各个参数的含义：

```python
for tool_call in tool_calls:
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    print(f"Tool: {tool_name}, Args: {tool_args}")
    if tool_name == "get_current_weather":
        print(f"Weather in {tool_args['location']}, {tool_args['country']}: {tool_args['weather']}")
```

### 逐行解释

1. `for tool_call in tool_calls:`
   - 这行代码表示遍历`tool_calls`这个列表。`tool_calls`应该是一个包含多个“工具调用”对象的集合，每个对象都代表一次工具的调用。

2. `tool_name = tool_call.function.name`
   - 这里从每个`tool_call`对象中，获取其`function`属性下的`name`字段。这个`tool_name`就是被调用的工具的名称，比如 `"get_current_weather"`。

3. `tool_args = json.loads(tool_call.function.arguments)`
   - 这里从`tool_call.function.arguments`中获取参数，并用`json.loads`将其从JSON字符串解析为Python字典。`tool_args`就是本次工具调用时传递的所有参数，通常是一个字典，比如：
     ```python
     {
         "location": "Shanghai",
         "country": "China",
         "weather": "Sunny"
     }
     ```

4. `print(f"Tool: {tool_name}, Args: {tool_args}")`
   - 打印出工具名称和参数，方便调试和查看。

5. `if tool_name == "get_current_weather":`
   - 判断当前工具调用的名称是否为`get_current_weather`，如果是，则执行下面的打印。

6. `print(f"Weather in {tool_args['location']}, {tool_args['country']}: {tool_args['weather']}")`
   - 取出参数字典中的`location`（地点）、`country`（国家）、`weather`（天气情况），并格式化输出。例如：
     ```
     Weather in Shanghai, China: Sunny
     ```

---

### 参数含义总结

- `tool_calls`：工具调用对象的列表，每个元素代表一次工具的调用。
- `tool_call.function.name`：工具的名称（字符串），比如 `"get_current_weather"`。
- `tool_call.function.arguments`：工具调用时传递的参数（JSON字符串），需要用`json.loads`解析成字典。
- `tool_args['location']`：地点，比如 `"Shanghai"`。
- `tool_args['country']`：国家，比如 `"China"`。
- `tool_args['weather']`：天气情况，比如 `"Sunny"`。

如果你还有具体哪个参数不明白，可以告诉我，我再详细解释！

# 训练一个自己的fu n cation call模型

```
from enum import Enum
from functools import partial
import pandas as pd
import torch
import json

from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from datasets import load_dataset
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig, TaskType

seed = 42
set_seed(seed)

import os
```


```
import subprocess
import os

# 这是 aistackdc 用于 Github/huggingface 下载加速的方式
result = subprocess.run('bash -c "source /etc/network/turbo && env | grep proxy"', shell=True, capture_output=True, text=True)
output = result.stdout
for line in output.splitlines():
    if '=' in line:
        var, value = line.split('=', 1)
        os.environ[var] = value


model_name = "Qwen/Qwen2.5-0.5B-Instruct"
dataset_name = "Jofthomas/hermes-function-calling-thinking-V1"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 备注：这里的 model 
tokenizer.chat_template = "{{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported') }}{% endif %}{% for message in messages %}{{ '<|im_start|>' + message['role'] + '\n' + message['content'] | trim + '<|im_end|>\n' }}{% endfor %}{% if add_generation_prompt %}{{'<|im_start|>assistant\n'}}{% endif %}"


def preprocess(sample):
    messages = sample["messages"]
    first_message = messages[0]

    # Instead of adding a system message, we merge the content into the first user message
    if first_message["role"] == "system":
        system_message_content = first_message["content"]
        # Merge system content with the first user message
        messages[1]["content"] = system_message_content + "Also, before making a call to a function take the time to plan the function to take. Make that thinking process between <think>{your thoughts}</think>\n\n" + messages[1]["content"]
        # Remove the system message from the conversation
        messages.pop(0)

    return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}


dataset = load_dataset(dataset_name)
dataset = dataset.rename_column("conversations", "messages")
```



### 数据形式
```
{'messages': [{'content': "You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions.Here are the available tools:<tools> [{'type': 'function', 'function': {'name': 'get_stock_price', 'description': 'Get the current stock price of a company', 'parameters': {'type': 'object', 'properties': {'company': {'type': 'string', 'description': 'The name of the company'}}, 'required': ['company']}}}, {'type': 'function', 'function': {'name': 'get_movie_details', 'description': 'Get details about a movie', 'parameters': {'type': 'object', 'properties': {'title': {'type': 'string', 'description': 'The title of the movie'}}, 'required': ['title']}}}] </tools>Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']}For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:\n<tool_call>\n{tool_call}\n</tool_call>",
   'role': 'system'},
  {'content': 'Hi, can you tell me the current stock price of Apple?',
   'role': 'human'},
  {'content': "<think>Alright, the user asked for the current stock price of Apple. Looking at the tools available, there's a function called get_stock_price which exactly fits this request. I'll need to call this function with the parameter company set to 'Apple' to retrieve the information the user is asking for. This seems like the most straightforward and appropriate action to take.\n</think><tool_call>\n{'name': 'get_stock_price', 'arguments': {'company': 'Apple'}}\n</tool_call>",
   'role': 'model'},
  {'content': "<tool_response>\n{'stock_price': '$150.75'}\n</tool_response>",
   'role': 'tool'},
  {'content': 'The current stock price of Apple is $150.75.', 'role': 'model'},
  {'content': "That's great. Can you also tell me the stock price for Microsoft?",
   'role': 'human'},
  {'content': "<think>Alright, let me try to figure out how to handle this user's request. The user first asked about Apple's stock price, and I responded by calling the get_stock_price function with 'Apple' as the argument. The tool provided the price, and I passed that information back to the user.\n\nNow, the user is asking for the stock price of Microsoft. I need to determine the appropriate action here. Looking at the tools available, there's still the get_stock_price function, which is designed to fetch current stock prices. Since the user is requesting another company's stock price, it makes sense to use the same function again but with the company name changed to Microsoft. \n\nI shouldn't assume any other tools are needed because the available functions are specifically tailored for stock prices and movie details. In this case, the relevant function is get_stock_price. I should ensure that the function is called with the correct parameter, 'Microsoft' in this case, to retrieve the accurate information the user is seeking. This approach is efficient and aligns directly with the user's request without making unnecessary assumptions or using unrelated tools.\n</think><tool_call>\n{'name': 'get_stock_price', 'arguments': {'company': 'Microsoft'}}\n</tool_call>",
   'role': 'model'},
  {'content': "<tool_response>\n{'stock_price': '$210.22'}\n</tool_response>",
   'role': 'tool'},
  {'content': 'The current stock price of Microsoft is $210.22.',
   'role': 'model'},
  {'content': 'Thank you for the information.', 'role': 'human'},
  {'content': "You're welcome! If you have any other questions, feel free to ask.",
   'role': 'model'}]}
```

```
# 改成和 qwen 对应 assistant / user 的格式
def convert_model_to_assistant(sample):
    messages = sample["messages"]
    for message in messages:
        if message["role"] == "model":
            message["role"] = "assistant"
        if message["role"] == "human":
            message["role"] = "user"
    return sample

dataset = dataset.map(convert_model_to_assistant)
```


```
{'messages': [{'content': "You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions.Here are the available tools:<tools> [{'type': 'function', 'function': {'name': 'get_stock_price', 'description': 'Get the current stock price of a company', 'parameters': {'type': 'object', 'properties': {'company': {'type': 'string', 'description': 'The name of the company'}}, 'required': ['company']}}}, {'type': 'function', 'function': {'name': 'get_movie_details', 'description': 'Get details about a movie', 'parameters': {'type': 'object', 'properties': {'title': {'type': 'string', 'description': 'The title of the movie'}}, 'required': ['title']}}}] </tools>Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']}For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:\n<tool_call>\n{tool_call}\n</tool_call>",
   'role': 'system'},
  {'content': 'Hi, can you tell me the current stock price of Apple?',
   'role': 'user'},
  {'content': "<think>Alright, the user asked for the current stock price of Apple. Looking at the tools available, there's a function called get_stock_price which exactly fits this request. I'll need to call this function with the parameter company set to 'Apple' to retrieve the information the user is asking for. This seems like the most straightforward and appropriate action to take.\n</think><tool_call>\n{'name': 'get_stock_price', 'arguments': {'company': 'Apple'}}\n</tool_call>",
   'role': 'assistant'},
  {'content': "<tool_response>\n{'stock_price': '$150.75'}\n</tool_response>",
   'role': 'tool'},
  {'content': 'The current stock price of Apple is $150.75.',
   'role': 'assistant'},
  {'content': "That's great. Can you also tell me the stock price for Microsoft?",
   'role': 'user'},
  {'content': "<think>Alright, let me try to figure out how to handle this user's request. The user first asked about Apple's stock price, and I responded by calling the get_stock_price function with 'Apple' as the argument. The tool provided the price, and I passed that information back to the user.\n\nNow, the user is asking for the stock price of Microsoft. I need to determine the appropriate action here. Looking at the tools available, there's still the get_stock_price function, which is designed to fetch current stock prices. Since the user is requesting another company's stock price, it makes sense to use the same function again but with the company name changed to Microsoft. \n\nI shouldn't assume any other tools are needed because the available functions are specifically tailored for stock prices and movie details. In this case, the relevant function is get_stock_price. I should ensure that the function is called with the correct parameter, 'Microsoft' in this case, to retrieve the accurate information the user is seeking. This approach is efficient and aligns directly with the user's request without making unnecessary assumptions or using unrelated tools.\n</think><tool_call>\n{'name': 'get_stock_price', 'arguments': {'company': 'Microsoft'}}\n</tool_call>",
   'role': 'assistant'},
  {'content': "<tool_response>\n{'stock_price': '$210.22'}\n</tool_response>",
   'role': 'tool'},
  {'content': 'The current stock price of Microsoft is $210.22.',
   'role': 'assistant'},
  {'content': 'Thank you for the information.', 'role': 'user'},
  {'content': "You're welcome! If you have any other questions, feel free to ask.",
   'role': 'assistant'}]}
```


```
dataset = dataset.map(preprocess, remove_columns="messages")
dataset = dataset["train"].train_test_split(0.1)
print(dataset)
```


```
DatasetDict({
    train: Dataset({
        features: ['text'],
        num_rows: 3213
    })
    test: Dataset({
        features: ['text'],
        num_rows: 357
    })
})
```


```
print(dataset["train"][8]["text"])
```


```
<|im_start|>human
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions.Here are the available tools:<tools> [{'type': 'function', 'function': {'name': 'get_news_headlines', 'description': 'Get the latest news headlines', 'parameters': {'type': 'object', 'properties': {'country': {'type': 'string', 'description': 'The country for which headlines are needed'}}, 'required': ['country']}}}, {'type': 'function', 'function': {'name': 'search_recipes', 'description': 'Search for recipes based on ingredients', 'parameters': {'type': 'object', 'properties': {'ingredients': {'type': 'array', 'items': {'type': 'string'}, 'description': 'The list of ingredients'}}, 'required': ['ingredients']}}}] </tools>Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']}For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:
<tool_call>
{tool_call}
</tool_call>Also, before making a call to a function take the time to plan the function to take. Make that thinking process between <think>{your thoughts}</think>

Can you get me the latest news headlines for the United States?<|im_end|>
<|im_start|>model
<think>Okay, so the user asked for the latest news headlines in the United States. I need to figure out how to respond appropriately using the tools available.

Looking at the tools provided, there's a function called get_news_headlines. That seems perfect for this situation. It requires a country code, which the user specified as the United States.

Since the user is asking specifically about the US, I'll use the country parameter as 'United States' in the function call. This should fetch the relevant news for them.

I should make sure to format the response correctly as a JSON object with the function name and arguments.
</think><tool_call>
{'name': 'get_news_headlines', 'arguments': {'country': 'United States'}}
</tool_call><|im_end|>
<|im_start|>tool
<tool_response>
{'headlines': ['US President signs new bill into law', 'Major earthquake hits California', 'NASA announces new Mars mission', 'Tech giant releases new smartphone', 'US economy shows signs of recovery']}
</tool_response><|im_end|>
<|im_start|>model
Here are the latest news headlines for the United States:
1. US President signs new bill into law
2. Major earthquake hits California
3. NASA announces new Mars mission
4. Tech giant releases new smartphone
5. US economy shows signs of recovery<|im_end|>
<|im_start|>human
That's interesting. Can you get me the news for France now?<|im_end|>
<|im_start|>model
<think>Okay, the user initially asked for the latest US news, so I used get_news_headlines with 'United States'. Now the user is asking for France, so I'll call the same function with 'France' as the country. That makes sense because the function is designed for any country.
</think><tool_call>
{'name': 'get_news_headlines', 'arguments': {'country': 'France'}}
</tool_call><|im_end|>
<|im_start|>tool
<tool_response>
{'headlines': ['French President announces new environmental policy', 'Paris Fashion Week highlights', 'France wins World Cup qualifier', 'New culinary trend sweeps across France', 'French tech startup raises millions in funding']}
</tool_response><|im_end|>
<|im_start|>model
Here are the latest news headlines for France:
1. French President announces new environmental policy
2. Paris Fashion Week highlights
3. France wins World Cup qualifier
4. New culinary trend sweeps across France
5. French tech startup raises millions in funding<|im_end|>
```


```
# Sanity check
print(tokenizer.pad_token)
print(tokenizer.eos_token)
```

```
<|endoftext|>
<|im_end|>
```

```
class ChatmlSpecialTokens(str, Enum):
    tools = "<tools>"
    eotools = "</tools>"
    think = "<think>"
    eothink = "</think>"
    tool_call="<tool_call>"
    eotool_call="</tool_call>"
    tool_response="<tool_reponse>"
    eotool_response="</tool_reponse>"
    pad_token = "<|endoftext|>"
    eos_token = "<|im_end|>"
    @classmethod
    def list(cls):
        return [c.value for c in cls]

tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        pad_token=ChatmlSpecialTokens.pad_token.value,
        additional_special_tokens=ChatmlSpecialTokens.list()
    )
tokenizer.chat_template = "{{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported') }}{% endif %}{% for message in messages %}{{ '<|im_start|>' + message['role'] + '\n' + message['content'] | trim + '<|im_end|>\n' }}{% endfor %}{% if add_generation_prompt %}{{'<|im_start|>assistant\n'}}{% endif %}"
```
user:input

model:一段话，+tool_call

role:tool + Tool_result

model:结果

遇到observation，去解析input

function_call需要模型迭代支持，每个厂商的functioncall可能不太一样的


mcp是一个通信的协议的，甚至可以理解为另外一个格式的function——call

这个协议包括了client和server两个部分的

server定义了工具

client可以解析工具，并且调用server

备注：因为client需要去解析工具结果的，因此systemprompt怎么写是client定义的




