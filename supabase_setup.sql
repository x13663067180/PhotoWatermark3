-- Supabase 数据库表结构
-- 在 Supabase SQL Editor 中执行此脚本

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 旅行计划表
CREATE TABLE IF NOT EXISTS travel_plans (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    plan_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 费用记录表
CREATE TABLE IF NOT EXISTS expenses (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES travel_plans(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_travel_plans_user_id ON travel_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_plan_id ON expenses(plan_id);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);

-- 启用行级安全策略 (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- 删除已存在的策略（如果存在）
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;
DROP POLICY IF EXISTS "Users can view own plans" ON travel_plans;
DROP POLICY IF EXISTS "Users can insert own plans" ON travel_plans;
DROP POLICY IF EXISTS "Users can update own plans" ON travel_plans;
DROP POLICY IF EXISTS "Users can delete own plans" ON travel_plans;
DROP POLICY IF EXISTS "Users can view own expenses" ON expenses;
DROP POLICY IF EXISTS "Users can insert own expenses" ON expenses;
DROP POLICY IF EXISTS "Users can update own expenses" ON expenses;
DROP POLICY IF EXISTS "Users can delete own expenses" ON expenses;

-- 用户表策略：允许所有操作（因为使用的是 anon key）
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (true);

-- 旅行计划表策略：允许所有操作
CREATE POLICY "Users can view own plans" ON travel_plans
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own plans" ON travel_plans
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own plans" ON travel_plans
    FOR UPDATE USING (true);

CREATE POLICY "Users can delete own plans" ON travel_plans
    FOR DELETE USING (true);

-- 费用记录表策略：允许所有操作
CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (true);

CREATE POLICY "Users can insert own expenses" ON expenses
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own expenses" ON expenses
    FOR UPDATE USING (true);

CREATE POLICY "Users can delete own expenses" ON expenses
    FOR DELETE USING (true);
