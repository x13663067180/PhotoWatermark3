import dashscope
from dashscope import Generation
from config import Config
import json

class AIService:
    def __init__(self):
        dashscope.api_key = Config.DASHSCOPE_API_KEY
        self.model = Config.QWEN_MODEL
    
    def generate_travel_plan(self, user_input):
        """根据用户输入生成旅行计划"""
        system_prompt = """你是一个专业的旅行规划助手。根据用户的需求，生成详细的旅行计划。
        
请以 JSON 格式返回计划，包含以下字段：
{
  "destination": "目的地",
  "duration": "天数",
  "budget": "预算（元）",
  "travelers": "人数",
  "preferences": ["偏好1", "偏好2"],
  "itinerary": [
    {
      "day": 1,
      "date": "日期",
      "activities": [
        {
          "time": "时间",
          "activity": "活动",
          "location": "地点",
          "cost": 费用,
          "notes": "备注"
        }
      ]
    }
  ],
  "accommodation": [
    {
      "name": "酒店名称",
      "location": "位置",
      "nights": 晚数,
      "cost": 费用
    }
  ],
  "transportation": {
    "to_destination": {"type": "交通方式", "cost": 费用},
    "local": {"type": "交通方式", "cost": 费用},
    "from_destination": {"type": "交通方式", "cost": 费用}
  },
  "budget_breakdown": {
    "transportation": 费用,
    "accommodation": 费用,
    "food": 费用,
    "activities": 费用,
    "shopping": 费用,
    "emergency": 费用,
    "total": 总费用
  },
  "tips": ["建议1", "建议2"]
}"""
        
        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                result_format='message',
                temperature=0.7
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
            else:
                raise Exception(f"API 调用失败: {response.code} - {response.message}")
            
            # 尝试解析 JSON
            try:
                plan = json.loads(content)
            except json.JSONDecodeError:
                # 如果不是纯 JSON，尝试提取 JSON 部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                else:
                    plan = {"raw_response": content}
            
            return plan
            
        except Exception as e:
            print(f"AI 服务错误: {e}")
            return {
                "error": str(e),
                "destination": "未知",
                "message": "生成计划时出错，请稍后重试"
            }
    
    def analyze_budget(self, expenses, budget):
        """分析预算使用情况"""
        prompt = f"""分析以下旅行开销情况：
预算：{budget} 元
已花费：{json.dumps(expenses, ensure_ascii=False)}

请提供：
1. 预算使用分析
2. 各类别开销占比
3. 节省建议
4. 剩余预算建议"""
        
        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个旅行预算分析专家"},
                    {"role": "user", "content": prompt}
                ],
                result_format='message',
                temperature=0.7
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"预算分析出错: {response.message}"
            
        except Exception as e:
            return f"预算分析出错: {e}"
