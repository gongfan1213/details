client = OpenAI(
    baseurl="",
    api_key="",
)

tools= [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The location to get the weather for"},
                "country":{"type": "string", "description": "The country to get the weather for"},
            },
        },
        "required": ["location"],
        "additionalProperties": False,
    },
}]
message = ["role":"user","content":"深圳市的的天气怎么样"]
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=message,
    tools=tools,
    tool_choice="auto",
    #auto/required;none
)
print(response.choices[0].message.content)
tool_calls = response.choices[0].message.tool_calls
for tool_call in tool_calls:
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    print(f"Tool: {tool_name}, Args: {tool_args}")
    if tool_name == "get_current_weather":
        print(f"Weather in {tool_args['location']}, {tool_args['country']}: {tool_args['weather']}")

def get_current_weather(location, country):
    return f"Weather in {location}, {country}: sunny"

print(get_current_weather("深圳市", "中国"))
# step4将functioncall的结果返回给llm
messages = messages.append(response.choices[0].message)
messages.append({
    "role": "tool",
    "content": get_current_weather("深圳市", "中国"),
    "tool_call_id": tool_call.id,
})
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tool_choice="none",
)
print(response.choices[0].message.content)
print(tool_call.id)
# step5:再次调用llm
res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tool_choice="none",
)
print(res.choices[0].message.content)

# function
