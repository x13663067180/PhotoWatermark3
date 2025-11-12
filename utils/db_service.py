import sqlite3
import hashlib
import json
from datetime import datetime
from config import Config

class DatabaseService:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 旅行计划表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS travel_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 费用记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_id) REFERENCES travel_plans (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """创建用户"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True, '注册成功'
        except sqlite3.IntegrityError:
            return False, '用户名或邮箱已存在'
        except Exception as e:
            return False, f'注册失败: {str(e)}'
    
    def authenticate_user(self, username, password):
        """验证用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_user_by_id(self, user_id):
        """根据 ID 获取用户"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def save_travel_plan(self, user_id, plan_data):
        """保存旅行计划"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        title = plan_data.get('destination', '未命名计划')
        plan_json = json.dumps(plan_data, ensure_ascii=False)
        
        cursor.execute(
            'INSERT INTO travel_plans (user_id, title, plan_data) VALUES (?, ?, ?)',
            (user_id, title, plan_json)
        )
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return plan_id
    
    def get_user_plans(self, user_id):
        """获取用户的所有计划"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, title, created_at, updated_at FROM travel_plans WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        )
        
        plans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return plans
    
    def get_plan_by_id(self, plan_id, user_id):
        """获取特定计划"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM travel_plans WHERE id = ? AND user_id = ?',
            (plan_id, user_id)
        )
        
        plan = cursor.fetchone()
        conn.close()
        
        if plan:
            plan_dict = dict(plan)
            plan_dict['plan_data'] = json.loads(plan_dict['plan_data'])
            return plan_dict
        return None
    
    def delete_plan(self, plan_id, user_id):
        """删除旅行计划"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 先删除关联的费用记录
            cursor.execute('DELETE FROM expenses WHERE plan_id = ? AND user_id = ?', (plan_id, user_id))
            
            # 再删除计划
            cursor.execute('DELETE FROM travel_plans WHERE id = ? AND user_id = ?', (plan_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除计划失败: {e}")
            return False
    
    def add_expense(self, plan_id, user_id, expense_data):
        """添加费用记录"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                '''INSERT INTO expenses (plan_id, user_id, category, amount, description, date)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (plan_id, user_id, expense_data['category'], expense_data['amount'],
                 expense_data.get('description', ''), expense_data['date'])
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加费用记录失败: {e}")
            return False
