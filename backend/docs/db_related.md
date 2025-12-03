flask db init：初始化 migrations 資料夾

flask db migrate -m "描述"：產生遷移腳本

flask db upgrade：套用遷移






## db schema

```
-- users 表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80),
    email VARCHAR(120),
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN
);

-- files 表
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    user_id INTEGER,  -- 外鍵列（實際存儲）
    file_size BIGINT,
    uploaded_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

```