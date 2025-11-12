from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from config import Config
from utils.ai_service import AIService
from utils.voice_service import VoiceService
from utils.db_service import DatabaseService
from utils.supabase_service import SupabaseService
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 初始化服务
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 根据配置选择数据库服务
if Config.USE_SUPABASE:
    print("使用 Supabase 云端数据库")
    db_service = SupabaseService()
else:
    print("使用本地 SQLite 数据库")
    db_service = DatabaseService()

ai_service = AIService()
voice_service = VoiceService()

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user_data = db_service.get_user_by_id(user_id)
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user_data = db_service.authenticate_user(username, password)
        if user_data:
            user = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user)
            return jsonify({'success': True, 'message': '登录成功'})
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    success, message = db_service.create_user(username, email, password)
    return jsonify({'success': success, 'message': message})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/planner')
@login_required
def planner():
    return render_template('planner.html', username=current_user.username)

@app.route('/api/generate-plan', methods=['POST'])
@login_required
def generate_plan():
    data = request.get_json()
    user_input = data.get('input', '')
    
    # 使用 AI 生成旅行计划
    plan = ai_service.generate_travel_plan(user_input)
    
    # 保存计划到数据库
    plan_id = db_service.save_travel_plan(current_user.id, plan)
    
    return jsonify({
        'success': True,
        'plan': plan,
        'plan_id': plan_id
    })

@app.route('/api/my-plans', methods=['GET'])
@login_required
def get_my_plans():
    plans = db_service.get_user_plans(current_user.id)
    return jsonify({'success': True, 'plans': plans})

@app.route('/api/plan/<int:plan_id>', methods=['GET'])
@login_required
def get_plan(plan_id):
    plan = db_service.get_plan_by_id(plan_id, current_user.id)
    if plan:
        return jsonify({'success': True, 'plan': plan})
    return jsonify({'success': False, 'message': '计划不存在'}), 404

@app.route('/api/plan/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_plan(plan_id):
    """删除旅行计划"""
    try:
        # 检查计划是否存在且属于当前用户
        plan = db_service.get_plan_by_id(plan_id, current_user.id)
        if not plan:
            return jsonify({'success': False, 'message': '计划不存在或无权限删除'}), 404
        
        # 删除计划
        if hasattr(db_service, 'delete_plan'):
            success = db_service.delete_plan(plan_id, current_user.id)
        else:
            # 如果是 SQLite，手动删除
            conn = db_service.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM travel_plans WHERE id = ? AND user_id = ?', (plan_id, current_user.id))
            conn.commit()
            conn.close()
            success = True
        
        if success:
            return jsonify({'success': True, 'message': '计划已删除'})
        else:
            return jsonify({'success': False, 'message': '删除失败'}), 500
    except Exception as e:
        print(f"删除计划错误: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/expense', methods=['POST'])
@login_required
def add_expense():
    data = request.get_json()
    plan_id = data.get('plan_id')
    expense_data = data.get('expense')
    
    success = db_service.add_expense(plan_id, current_user.id, expense_data)
    return jsonify({'success': success})

@app.route('/api/voice-config', methods=['GET'])
def get_voice_config():
    return jsonify(voice_service.get_client_config())

@app.route('/api/map-config', methods=['GET'])
def get_map_config():
    """获取地图配置"""
    return jsonify({
        'amap_key': Config.AMAP_API_KEY,
        'amap_secret': Config.AMAP_SECRET_KEY
    })

if __name__ == '__main__':
    # 只有使用本地数据库时才需要初始化
    if not Config.USE_SUPABASE:
        db_service.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
