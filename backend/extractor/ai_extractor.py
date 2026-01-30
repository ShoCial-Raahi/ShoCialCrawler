import os
import json
from openai import AsyncOpenAI
from config import Config

class AIExtractor:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.AI_PROVIDER_BASE_URL
        )
        with open("extractor/prompt.txt", "r") as f:
            self.prompt_template = f.read()

    async def extract(self, html_content: str):
        # Truncate HTML to avoid token limits (heuristic)
        truncated_html = html_content[:50000] # Adjust based on model
        
        prompt = self.prompt_template.replace("{{HTML_CONTENT}}", truncated_html)

        try:
            response = await self.client.chat.completions.create(
                model=Config.AI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Extraction failed: {e}")
            return None
