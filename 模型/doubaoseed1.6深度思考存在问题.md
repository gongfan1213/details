# 深度思考严重问题
非Hermes-style模板


使用qwen以往模型写法


https://github.com/QwenLM/Qwen3


https://docs.vllm.ai/en/latest/features/tool_calling.html

<img width="1832" height="1140" alt="image" src="https://github.com/user-attachments/assets/9b87dff5-c161-45b9-9d1e-e8960860d3cb" />


根据提供的代码片段和功能描述，以下是新增或修改的代码整理：


### **1. 测试用例新增（`test_anthropic_proxy.py`）**
```python
def test_function_call_parsing_with_whitespace(self):
    """Test function call parsing with realistic whitespace/newlines from logs."""
    from anthropic_proxy.converter import parse_function_calls_from_thinking
    
    # 测试包含真实日志格式的函数调用解析（带换行和空格）
    thinking_with_whitespace = """I need to update the README to include the MAX_RETRIES environment variable configuration.

<|FunctionCallBegin|>[
{"name": "Edit", "parameters": {"file_path": "/Users/test/README.md", "old_string": "- Enhanced client reliability", "new_string": "- Enhanced client reliability with MAX_RETRIES configuration"}}
]<|FunctionCallEnd|>

Let me proceed with this edit."""

    cleaned_thinking, function_calls = parse_function_calls_from_thinking(
        thinking_with_whitespace
    )

    # 验证函数调用解析结果
    self.assertEqual(len(function_calls), 1)
    tool_call = function_calls[0]
    self.assertIn("id", tool_call)
    self.assertEqual(tool_call["type"], "function")
    self.assertEqual(tool_call["function"]["name"], "Edit")

    # 验证函数参数
    import json
    arguments = json.loads(tool_call["function"]["arguments"])
    self.assertIn("file_path", arguments)
    self.assertIn("old_string", arguments)
    self.assertIn("new_string", arguments)
    self.assertEqual(arguments["file_path"], "/Users/test/README.md")

    # 验证清理后的思考内容
    self.assertNotIn("<|FunctionCallBegin|>", cleaned_thinking)
    self.assertNotIn("<|FunctionCallEnd|>", cleaned_thinking)
    self.assertIn("I need to update the README", cleaned_thinking)
    self.assertIn("Let me proceed with this edit.", cleaned_thinking)

    print("✅ Function call parsing with whitespace test passed")

def test_complex_conversation_flow(self):
    """Test a complex multi-turn conversation with tools."""
    print("🧪 Testing complex conversation flow...")
```


### **2. 功能代码优化（`anthropic_proxy/converter.py`）**
#### **新增正则表达式与解析逻辑**
```python
import re
import json
import logging

# 优化正则表达式，支持多行和任意空白字符
FUNCTION_CALL_REGEX = re.compile(
    r"<\|FunctionCallBegin\|>(\[.*?\])<\|FunctionCallEnd\|>", 
    re.DOTALL | re.MULTILINE
)

def parse_function_calls_from_thinking(thinking_text):
    """从思考文本中提取函数调用并清理文本"""
    function_calls = []
    cleaned_text = thinking_text
    
    # 查找所有函数调用块
    for match in FUNCTION_CALL_REGEX.finditer(thinking_text):
        function_call_str = match.group(1).strip()  # 新增strip()处理空白
        logging.debug(f"Extracted function call JSON: {function_call_str}")
        
        try:
            # 解析函数调用JSON
            function_call_list = json.loads(function_call_str)
            for call in function_call_list:
                # 为每个函数调用添加唯一ID和类型
                function_calls.append({
                    "id": str(uuid.uuid4()),
                    "type": "function",
                    "function": {
                        "name": call["name"],
                        "arguments": json.dumps(call["parameters"])
                    }
                })
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse function call: {function_call_str}")
            logging.error(f"Error: {str(e)}")
            continue
    
    # 清理原始文本中的函数调用标记
    cleaned_text = FUNCTION_CALL_REGEX.sub("", cleaned_text).strip()
    return cleaned_text, function_calls
```


### **3. 文档更新（`README.md` 新增内容）**
```markdown
### 环境变量配置
- `MAX_RETRIES`: 设置API请求自动重试次数（默认值：2）。
  ```bash
  export MAX_RETRIES=5  # 设置最大重试5次
  ```
```


### **4. 脚本更新（`Makefile` 新增目标）**
```makefile
start:
    ./claude.sh

.PHONY: test clean start  # 添加start到PHONY目标
```


### **5. 其他补充**
#### **增强错误处理**
```python
# 在关键解析步骤增加错误日志
try:
    # 解析函数调用
    ...
except json.JSONDecodeError as e:
    logging.error(f"Failed to parse function call JSON: {function_call_str}")
    logging.error(f"Error details: {str(e)}")
    # 可选：添加更友好的错误提示或回退逻辑
```

#### **新增工具函数**
```python
def generate_unique_id():
    """生成唯一ID（用于函数调用标识）"""
    return str(uuid.uuid4())
```


这些新增代码主要围绕函数调用解析的健壮性、测试覆盖度以及项目文档和工具链的完善。

```
  def test_function_call_parsing_with_whitespace(self):
        """Test function call parsing with realistic whitespace/newlines from logs."""
        from anthropic_proxy.converter import parse_function_calls_from_thinking
        
        # Test realistic format with newlines and whitespace (like from actual logs)
        thinking_with_whitespace = """I need to update the README to include the MAX_RETRIES environment variable configuration.

<|FunctionCallBegin|>[
{"name": "Edit", "parameters": {"file_path": "/Users/test/README.md", "old_string": "- Enhanced client reliability", "new_string": "- Enhanced client reliability with MAX_RETRIES configuration"}}
]<|FunctionCallEnd|>

Let me proceed with this edit."""

        cleaned_thinking, function_calls = parse_function_calls_from_thinking(
            thinking_with_whitespace
        )

        # Verify function call was parsed correctly
        self.assertEqual(len(function_calls), 1)

        tool_call = function_calls[0]
        self.assertIn("id", tool_call)
        self.assertEqual(tool_call["type"], "function")
        self.assertEqual(tool_call["function"]["name"], "Edit")

        # Verify arguments contain expected data
        import json
        arguments = json.loads(tool_call["function"]["arguments"])
        self.assertIn("file_path", arguments)
        self.assertIn("old_string", arguments)
        self.assertIn("new_string", arguments)
        self.assertEqual(arguments["file_path"], "/Users/test/README.md")

        # Verify thinking content was cleaned
        self.assertNotIn("<|FunctionCallBegin|>", cleaned_thinking)
        self.assertNotIn("<|FunctionCallEnd|>", cleaned_thinking)
        self.assertIn("I need to update the README", cleaned_thinking)
        self.assertIn("Let me proceed with this edit.", cleaned_thinking)

        print("✅ Function call parsing with whitespace test passed")

```
