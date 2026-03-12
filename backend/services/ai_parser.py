"""AI-powered note parsing service using OpenAI-compatible API (DashScope/智谱)."""

import base64
import json
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("SHINOGRAPH_MODEL", "qwen-vl-plus")
DEFAULT_TEXT_MODEL = os.getenv("SHINOGRAPH_TEXT_MODEL", "qwen-plus")

PARSE_PROMPT = """你是一个知识图谱构建助手。请分析这段笔记内容，提取以下信息并返回 JSON：

{
  "raw_text": "完整文本内容",
  "summary": "一段简洁的摘要（50字以内）",
  "entities": [
    {"name": "概念名", "category": "学科/领域", "description": "一句话描述"}
  ],
  "relations": [
    {"source": "概念A", "target": "概念B", "relation": "关系类型", "description": "关系说明"}
  ],
  "qa_pairs": [
    {"question": "基于内容生成的问题", "answer": "对应答案"}
  ]
}

关系类型包括: contains(包含), causes(因果), contrasts(对比), extends(扩展), similar(相似)
请生成 2-5 个有价值的问答对，帮助用户回顾这段知识。
只返回 JSON，不要其他文字。"""


def _extract_json(text: str) -> dict:
    """Extract JSON from AI response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


class AIParser:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("API_KEY", ""),
            base_url=base_url or os.getenv("PROVIDER_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        )
        self.vision_model = model or DEFAULT_MODEL
        self.text_model = os.getenv("SHINOGRAPH_TEXT_MODEL") or DEFAULT_TEXT_MODEL

    def parse_image(self, image_data: bytes, media_type: str = "image/png") -> dict:
        """Parse a note screenshot into structured knowledge."""
        b64 = base64.standard_b64encode(image_data).decode("utf-8")
        response = self.client.chat.completions.create(
            model=self.vision_model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
                    {"type": "text", "text": PARSE_PROMPT},
                ],
            }],
        )
        return _extract_json(response.choices[0].message.content)

    def parse_text(self, text: str) -> dict:
        """Parse raw text into structured knowledge."""
        response = self.client.chat.completions.create(
            model=self.text_model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"{PARSE_PROMPT}\n\n以下是笔记文本：\n{text}",
            }],
        )
        return _extract_json(response.choices[0].message.content)

    def chat_with_context(self, question: str, context: str) -> str:
        """Answer a question using knowledge graph context."""
        response = self.client.chat.completions.create(
            model=self.text_model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"基于以下知识库内容回答用户的问题。如果知识库中没有相关信息，请坦诚说明。\n\n"
                    f"【知识库内容】\n{context}\n\n"
                    f"【用户问题】\n{question}"
                ),
            }],
        )
        return response.choices[0].message.content
