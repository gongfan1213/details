# 数据集处理
```
df_train = pd.DataFrame(columns=['data_source', 'prompt', 'ability', 'reward_model', 'extra_info'])
df_val = pd.DataFrame(columns=['data_source', 'prompt', 'ability', 'reward_model', 'extra_info'])
INSTRUCTIONS = """Generate code to solve the given question. \
You must conduct reasoning inside <think> and </think> before <code> and <answer> every time. \
After reasoning, if you find you need run code, you can call a code engine by <code> your code </code> and it will return the run results between <observation> and </observation>. \
You can generate and run code as many times as your want. \
After reasoning, if you find the given question has already been solved , you can directly provide the run summary inside <answer> and </answer>. \
Question: {}\n"""

data_source = []
prompt = []
ability = []
reward_model = []
extra_info = []
for idx, line in enumerate(lines[:2000]):
    line = json.loads(line)
    content = line['instruction'] + line['input']
    data_source.append('code')
    prompt.append([{"role": "user", "content": INSTRUCTIONS.format(content)}])
    ability.append('text')
    reward_model.append({
                "style": "rule",
                "ground_truth": "",
            })
    
    extra_info.append({
                'split': 'train',
                'index': idx,
                "user_message": content,
            })


df_train['data_source'] = data_source
df_train['prompt'] = prompt
df_train['ability'] = ability
df_train['reward_model'] = reward_model
df_train['extra_info'] = extra_info

df_train.to_parquet('./code_train.parquet')

data_source = []
prompt = []
ability = []
reward_model = []
extra_info = []
for idx, line in enumerate(lines[-100:]):
    line = json.loads(line)
    content = line['instruction'] + line['input']
    data_source.append('code')
    prompt.append([{"role": "user", "content": INSTRUCTIONS.format(content)}])
    ability.append('text')
    reward_model.append({
                "style": "rule",
                "ground_truth": "",
            })
    
    extra_info.append({
                'split': 'val',
                'index': idx,
                "user_message": content,
            })
df_val['data_source'] = data_source
df_val['prompt'] = prompt
df_val['ability'] = ability
df_val['reward_model'] = reward_model
df_val['extra_info'] = extra_info

df_val.to_parquet('./code_val.parquet')
```
# 2.构建奖励函数

```
import re
import random
from openai import OpenAI

client = OpenAI(base_url='http://***/v1', api_key='***')
def get_llm_output(prompt):
    
    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]

    completion = client.chat.completions.create(
        model = 'qwen3-32b',
        temperature=0.0,
        messages=messages,
        stream=False,
    )
    output = completion.choices[0].message.content
    return output


def extract_answer(text):
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()


def is_valid_sequence(content):
    
    
    
    # Check for balanced tags
    tags_to_check = ["think", "code", "observation", "answer"]
    for tag in tags_to_check:
        opening_count = len(re.findall(f"<{tag}>", content))
        closing_count = len(re.findall(f"</{tag}>", content))
        if opening_count != closing_count:
            return False, f"Mismatch in {tag} tags: {opening_count} opening vs {closing_count} closing tags"
    
    
    # 1. First split the content by any tags we recognize
    split_pattern = r"(</?(?:think|code|observation|answer)>)"
    parts = re.split(split_pattern, content)
    
    # 2. Keep track of the current position in the expected sequence
    state = "start"  # start -> think -> search -> information -> think -> ... -> answer -> end
    
    # 3. Check each part
    for i, part in enumerate(parts):
        # Skip empty parts
        if not part.strip():
            continue
            
        # Check if this is a tag
        if re.match(r"</?(?:think|code|observation|answer)>", part):
            # This is a tag, check if it's valid in the current state
            if part == "<think>" and state in ["start", "observation"]:
                state = "in_think"
            elif part == "</think>" and state == "in_think":
                state = "after_think"
            elif part == "<code>" and state == "after_think":
                state = "in_code"
            elif part == "</code>" and state == "in_code":
                state = "after_code"
            elif part == "<observation>" and state == "after_code":
                state = "in_observation"
            elif part == "</observation>" and state == "in_observation":
                state = "observation"
            elif part == "<answer>" and state == "after_think":
                state = "in_answer"
            elif part == "</answer>" and state == "in_answer":
                state = "end"
            else:
                return False, f"Unexpected tag {part} in state {state}"
        else:
            # This is content, check if it's valid in the current state
            if state in ["in_think", "in_code", "in_observation", "in_answer"]:
                # Content is allowed inside tags
                pass
            elif state in ["start", "after_think", "after_code", "observation"]:
                # Only whitespace is allowed between tags
                if part.strip():
                    return False, f"Unexpected content '{part.strip()}' between tags (state: {state})"
            else:
                return False, f"Unexpected content in state {state}"
    
    # Check final state
    if state != "end":
        return False, f"Incomplete sequence, ended in state {state}"
        
    return True, "Valid sequence format"

def answer_reward(user_message, answer):
    prompt = '''
    ## 任务目标
    根据执行过程判断是否成功解决问题
    
    ## 任务要求
    - 认真审视执行过程，做出正确的判断
    - 只输出是或否，不要输出多余内容
    
    ## 问题
    {}
    
    ## 执行过程
    {}'''
    
    result = get_llm_output(prompt.format(user_message, answer))
    if result == '是':
        return 1
    else:
        return -1



def exec_code(code: str) -> str:
    import requests
    
    url = 'http://10.250.2.24:8090/run_code'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'code': code,
        'language': 'python'
    }

    response = requests.post(url, json=data, headers=headers)
    stdout = response.json()['run_result']['stdout']
    stderr = response.json()['run_result']['stderr']
    print(stdout, stderr)
    return stdout[:1000], stderr[:1000]


def extract_code(text: str)-> str:
        
    code_block_pattern = re.compile(r'<code>(.*?)</code>', re.DOTALL)

    # Find all matches in the text
    code_blocks = code_block_pattern.findall(text)

    # If no code blocks are found, try to find indented code blocks
    if not code_blocks:
        return []
    return code_blocks
    
def code_result(solution_str):
    code_blocks = extract_code(solution_str)
    if not code_blocks:
        return '', ''
    code = code_blocks[-1]
    stdout, stderr = exec_code(code)
    return stdout, stderr
    
    

def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    
    is_valid, _ = is_valid_sequence(solution_str)
    if is_valid:
        score = 0.5
        stdout, stderr = code_result(solution_str)
        if 'error' in stderr.lower() or 'traceback' in stderr.lower():
            score -= 0.5
        else:
            score += 0.5
            user_message = extra_info['user_message']
            score += answer_reward(user_message, solution_str)
        print('+++++++++++++++++++++++++++++')
        print(solution_str)
        print('+++++++++++++++++++++++++++++')
        return score
    else:
        format_score = 0
        
        if solution_str.startswith('<think>'):
            format_score += 0.1
        if solution_str.endswith('</answer>'):
            format_score += 0.1
        
        if '</think><answer>' in solution_str.replace('\n', ''):
            format_score += 0.1
        
        if '<think>' in solution_str and '</think>' in solution_str:
            format_score += 0.02
        
        if '<code>' in solution_str and '</code>' in solution_str:
            format_score += 0.02
        
        if '<answer>' in solution_str and '</answer>' in solution_str:
            format_score += 0.02
        
        return format_score

```
# 配置文件
- grpo-trainer.yaml

```

  # Maximum prompt length. All prompts will be left-padded to this length.
  # An error will be reported if the length is too long.
  max_prompt_length: 1024

  # Maximum response length. Rollout in RL algorithms (e.g. PPO) generates up to this length.
  max_response_length: 4096

  # Batch size sampled for one training iteration of different RL algorithms.
  train_batch_size: 16
# 一次从训练数据当中取出多少数据
 # actor configs
  actor:

    # fsdp, fsdp2 or megatron. fsdp backend used here.
    strategy: fsdp

    # Split each sample into sub-batches of this size for PPO
    ppo_mini_batch_size: 8
# 使用多少样本更新参数
# ppo_micro_batch_size_per_gpu ：8
# 控制梯度累加的参数
# fsdp, fsdp2 or megatron. fsdp backend used here.
    strategy: fsdp

    # Split each sample into sub-batches of this size for PPO
    ppo_mini_batch_size: 8

    # [Deprecated] Global micro batch size
    ppo_micro_batch_size: null

    # Local per-GPU micro batch size
    ppo_micro_batch_size_per_gpu: 2

```

```
# Rollout model config.
  rollout:

    # actor_rollout_ref.rollout.name: hf/vllm/sglang.
    name: vllm

    # sync: LLM, async: AsyncLLM
    mode: sync

    # Sampling temperature for rollout.
    temperature: 1.0

    # Top-k sampling parameter. -1 for vLLM rollout, 0 for HF rollout.
    top_k: -1

    # Top-p sampling parameter. Default 1.0.
    top_p: 1


    # typically the same as data max prompt length
    prompt_length: ${data.max_prompt_length}

    # typically the same as data max response length
    response_length: ${data.max_response_length}

    # for vllm rollout
    # Rollout model parameters type. Align with actor model's FSDP/Megatron type.
    dtype: bfloat16

    # Fraction of GPU memory used by vLLM/SGLang for KV cache.gpu显存的占比，0.5左右不要设置太高的
    gpu_memory_utilization: 0.3
```
rollout模型生成样本的时候

tensor_model_parallel_size:2 这个要和n_gpus_per_node的数量要对应的

<img width="575" height="416" alt="image" src="https://github.com/user-attachments/assets/b4e9472f-d1a3-49cf-ad1d-e4277e21f4ac" />

n:一个提示词要生成多少的响应的

打断点，breakpoint,在main_ppo.py这个文件夹当中的，

<img width="486" height="430" alt="image" src="https://github.com/user-attachments/assets/3f4b2ea2-0c9e-46f5-9fa5-c09743a29ce2" />


<img width="664" height="500" alt="image" src="https://github.com/user-attachments/assets/de6b2b68-99fb-4a25-83dc-54d20f191c5d" />

<img width="790" height="508" alt="image" src="https://github.com/user-attachments/assets/1ff0222a-9529-4400-95da-36a800dfb317" />


logger:['tensorboard']






