import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # AI 服务配置 - 通义千问
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
    QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-plus')  # 可选: qwen-turbo, qwen-plus, qwen-max
    
    # 科大讯飞语音识别配置
    XFYUN_APP_ID = os.getenv('XFYUN_APP_ID', '')
    XFYUN_API_KEY = os.getenv('XFYUN_API_KEY', '')
    XFYUN_API_SECRET = os.getenv('XFYUN_API_SECRET', '')
    
    # 高德地图配置（Web 端 JS API）
    AMAP_API_KEY = os.getenv('AMAP_API_KEY', '')
    AMAP_SECRET_KEY = os.getenv('AMAP_SECRET_KEY', '')
    
    # Supabase 配置（云端数据同步）
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
    
    # 数据库配置
    DATABASE_PATH = 'travel_planner.db'
