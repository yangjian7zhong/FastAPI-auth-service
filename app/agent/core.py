import json
import re
import httpx
from app.core.config import settings
from app.agent.tools import TOOLS, TOOL_DESCRIPTIONS

async def run_agent(query: str, max_iterations: int = 3) -> dict:
    """
    手动实现 Agent 推理循环（ReAct 风格）
    """
    messages = [
        {"role": "system", "content": f"""你是一个智能助手。你可以使用以下工具：
{chr(10).join([f'- {name}: {desc}' for name, desc in TOOL_DESCRIPTIONS.items()])}
请严格按照以下格式输出：
Thought: 你的思考过程
Action: 工具名称
Action Input: 工具输入（JSON格式）
或者：
Thought: 我有了答案
Final Answer: 最终回答
"""},
        {"role": "user", "content": query}
    ]

    tool_results = []
    final_answer = None

    for _ in range(max_iterations):
        # 调用 DeepSeek API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0
                },
                timeout=30.0
            )
            data = response.json()
            assistant_msg = data["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": assistant_msg})

        # 解析 Action / Final Answer
        action_match = re.search(r"Action:\s*(\w+)\s*Action Input:\s*(\{.*\})", assistant_msg, re.DOTALL)
        final_match = re.search(r"Final Answer:\s*(.+)", assistant_msg, re.DOTALL)

        if final_match:
            final_answer = final_match.group(1).strip()
            break

        if action_match:
            tool_name = action_match.group(1).strip()
            tool_input = action_match.group(2).strip()
            try:
                input_data = json.loads(tool_input)
            except:
                input_data = {"query": tool_input}
            tool_func = TOOLS.get(tool_name)
            if tool_func:
                result = tool_func(**input_data)
                tool_results.append({"tool": tool_name, "result": result})
                messages.append({
                    "role": "user",
                    "content": f"工具执行结果：{result}\n请根据结果继续思考并给出最终答案。"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": f"错误：未找到工具 '{tool_name}'，请选择可用工具。"
                })
        else:
            # 没有 Action 也没有 Final，强制要求 Final Answer
            messages.append({
                "role": "user",
                "content": "请直接给出最终答案（以 'Final Answer:' 开头）。"
            })

    if not final_answer:
        # 如果循环结束还没有 Final Answer，取最后一条 assistant 消息
        last_assistant = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), None)
        if last_assistant:
            final_answer = last_assistant

    return {
        "output": final_answer or "无法生成回答",
        "intermediate_steps": tool_results
    }