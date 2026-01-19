-- 数据库迁移：添加 is_demo 列到 users 表
-- 执行方法：在MySQL客户端中运行此SQL文件，或直接复制以下SQL语句执行

-- 1. 添加 is_demo 列（如果不存在）
ALTER TABLE users 
ADD COLUMN is_demo BOOLEAN DEFAULT FALSE 
AFTER is_active;

-- 2. 添加 password_changed_at 列（如果不存在）
ALTER TABLE users 
ADD COLUMN password_changed_at DATETIME DEFAULT NULL 
AFTER is_demo;

-- 3. 将 admin 用户设置为示例账号
UPDATE users 
SET is_demo = TRUE 
WHERE username = 'admin';

-- 4. 创建店长账户（如果不存在）
-- 用户名: nzpmrylams, 密码: yoloong819170
INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo, created_at)
SELECT 'nzpmrylams', 
       'scrypt:32768:8:1$JDxNgsMMX5mEoHa4$33f853b58bf43cc80dae378fe11d9a66dca52e8aa2365fb59d071ef0d098d13716275d34612bee6929e0bd7cf1b0e12ef9b78a102f6684634b2bd2b83dc2aef0',
       'manager', 
       '店长账户', 
       TRUE, 
       FALSE,
       NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'nzpmrylams');

-- 5. 创建前台员工账户（如果不存在）
-- 用户名: cqyg, 密码: 123456
INSERT INTO users (username, password_hash, role, real_name, is_active, is_demo, created_at)
SELECT 'cqyg', 
       'scrypt:32768:8:1$0MXszySCC4xueTsY$a812d3114073e9efa7ae76adc96d52b1747891dd2d5e0825750ca9acf1cea18de6f8ae9d500aec5df4ebce98f48dc359a855e9a593d51848625468265f383c06',
       'staff', 
       '前台员工', 
       TRUE, 
       FALSE,
       NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'cqyg');

-- 完成！
-- 账户信息：
-- 店长账户：用户名 nzpmrylams，密码 yoloong819170
-- 前台员工账户：用户名 cqyg，密码 123456

