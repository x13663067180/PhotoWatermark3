from supabase import create_client, Client
from config import Config
import hashlib
import json
from datetime import datetime

class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """创建用户"""
        try:
            password_hash = self.hash_password(password)
            
            data = {
                'username': username,
                'email': email,
                'password_hash': password_hash
            }
            
            result = self.supabase.table('users').insert(data).execute()
            return True, '注册成功'
        except Exception as e:
            error_msg = str(e)
            if 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                return False, '用户名或邮箱已存在'
            return False, f'注册失败: {error_msg}'
    
    def authenticate_user(self, username, password):
        """验证用户"""
        try:
            password_hash = self.hash_password(password)
            
            result = self.supabase.table('users')\
                .select('*')\
                .eq('username', username)\
                .eq('password_hash', password_hash)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"认证错误: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """根据 ID 获取用户"""
        try:
            result = self.supabase.table('users')\
                .select('*')\
                .eq('id', user_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"获取用户错误: {e}")
            return None
    
    def save_travel_plan(self, user_id, plan_data):
        """保存旅行计划"""
        try:
            title = plan_data.get('destination', '未命名计划')
            plan_json = json.dumps(plan_data, ensure_ascii=False)
            
            data = {
                'user_id': user_id,
                'title': title,
                'plan_data': plan_json
            }
            
            result = self.supabase.table('travel_plans').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]['id']
            return None
        except Exception as e:
            print(f"保存计划错误: {e}")
            return None
    
    def get_user_plans(self, user_id):
        """获取用户的所有计划"""
        try:
            result = self.supabase.table('travel_plans')\
                .select('id, title, created_at, updated_at')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"获取计划列表错误: {e}")
            return []
    
    def get_plan_by_id(self, plan_id, user_id):
        """获取特定计划"""
        try:
            result = self.supabase.table('travel_plans')\
                .select('*')\
                .eq('id', plan_id)\
                .eq('user_id', user_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                plan = result.data[0]
                plan['plan_data'] = json.loads(plan['plan_data'])
                return plan
            return None
        except Exception as e:
            print(f"获取计划详情错误: {e}")
            return None
    
    def update_plan(self, plan_id, user_id, plan_data):
        """更新旅行计划"""
        try:
            title = plan_data.get('destination', '未命名计划')
            plan_json = json.dumps(plan_data, ensure_ascii=False)
            
            data = {
                'title': title,
                'plan_data': plan_json,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('travel_plans')\
                .update(data)\
                .eq('id', plan_id)\
                .eq('user_id', user_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"更新计划错误: {e}")
            return False
    
    def delete_plan(self, plan_id, user_id):
        """删除旅行计划"""
        try:
            self.supabase.table('travel_plans')\
                .delete()\
                .eq('id', plan_id)\
                .eq('user_id', user_id)\
                .execute()
            return True
        except Exception as e:
            print(f"删除计划错误: {e}")
            return False
    
    def add_expense(self, plan_id, user_id, expense_data):
        """添加费用记录"""
        try:
            data = {
                'plan_id': plan_id,
                'user_id': user_id,
                'category': expense_data['category'],
                'amount': expense_data['amount'],
                'description': expense_data.get('description', ''),
                'date': expense_data['date']
            }
            
            result = self.supabase.table('expenses').insert(data).execute()
            return True
        except Exception as e:
            print(f"添加费用记录错误: {e}")
            return False
    
    def get_plan_expenses(self, plan_id, user_id):
        """获取计划的所有费用记录"""
        try:
            result = self.supabase.table('expenses')\
                .select('*')\
                .eq('plan_id', plan_id)\
                .eq('user_id', user_id)\
                .order('date', desc=True)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"获取费用记录错误: {e}")
            return []
