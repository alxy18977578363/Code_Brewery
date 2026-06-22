import logging
from typing import List, Dict

from src.llm.deepseek_client import chat

logger = logging.getLogger(__name__)

def chat_with_assistant(history: List[Dict[str, str]]) -> str:
    """与选题小助手对话。
    history: [{"role": "user"/"assistant", "content": "..."}]
    """
    sys_prompt = """你是一位耐心且专业的学术导师 Agent。你的任务是帮助用户构思和细化他们想要检索的文献主题。
当用户只有一个模糊的概念时，你需要：
1. 通过反问引导用户明确具体的应用场景、方法流派或评估指标。
2. 适时给出建议的检索关键词（中英文结合效果更好）。
3. 如果用户确定了最终想要检索的方向，请在回复的最后，用【】括起你推荐的最终检索词，例如：推荐检索词为【大语言模型 命名实体识别 提示学习】。

注意：
- 保持对话简短、有启发性。
- 不要直接给他们写综述，你的唯一目标是帮他们“确定应该搜什么词”。
"""
    
    messages = [{"role": "system", "content": sys_prompt}]
    # 限制历史记录长度，防止 token 过多
    messages.extend(history[-10:])
    
    try:
        reply = chat(messages, temperature=0.6, max_tokens=1024)
        return reply
    except Exception as e:
        logger.warning(f"Assistant Agent 运行失败: {e}")
        return "不好意思，导师去喝水了（网络或 API 错误），请稍后再试。"
