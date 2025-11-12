from config import Config
import base64
import hashlib
import hmac
import json
from datetime import datetime
from urllib.parse import urlencode
import time

class VoiceService:
    def __init__(self):
        self.app_id = Config.XFYUN_APP_ID
        self.api_key = Config.XFYUN_API_KEY
        self.api_secret = Config.XFYUN_API_SECRET
    
    def get_client_config(self):
        """获取客户端语音识别配置"""
        return {
            'app_id': self.app_id,
            'api_key': self.api_key,
            # 注意：实际生产环境中，不应该直接暴露 API Secret
            # 应该在后端生成签名后返回给前端
        }
    
    def generate_signature(self):
        """生成科大讯飞 WebSocket 连接签名"""
        ts = str(int(time.time()))
        base_string = self.app_id + ts
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            base_string.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'ts': ts,
            'signa': signature_b64
        }
