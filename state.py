from typing import List, Dict, Any, TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, Any]], add]   # 对话历史
    current_task: str                                # 当前任务类型
    tool_results: List[Dict]                         # 工具执行结果
    next_agent: str                                 # 下一个要执行的Agent
    iteration: int                                  # 迭代次数
    final_answer: str                               # 最终回答