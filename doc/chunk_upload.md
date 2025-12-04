
# 分塊上傳的資料庫模型設計

聚焦在資料庫層面，分析如何修改現有的 [`models.py`](filemanageportal/backend/src/models.py:1) 來支援分塊上傳與斷點續傳。

## 🎯 核心問題分析

### **是否需要使用 Blob Storage 特性？**

**答案：不一定需要，但可以利用。**

根據現有的 [`StorageService`](filemanageportal/backend/src/storage.py:19) 架構，系統支援兩種儲存模式：

1. **Local Storage** - 不需要 Blob Storage 特性
2. **Supabase Storage** - 可以利用 Blob Storage 的 Multipart Upload 特性

---

## 📊 資料庫模型設計方案

### **方案 A：純資料庫追蹤（推薦用於 Local Storage）**

新增 `ChunkedUpload` 模型到 [`models.py`](filemanageportal/backend/src/models.py:1)：

```python
class ChunkedUpload(db.Model):
    """
    追蹤分塊上傳的狀態
    適用於 Local Storage 和 Supabase Storage
    """
    
    __tablename__ = 'chunked_uploads'
    
    # === 主鍵與關聯 ===
    id = db.Column(db.String(36), primary_key=True)  # UUID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user = db.relationship('User', backref='chunked_uploads')
    
    # === 檔案基本資訊 ===
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)  # 總大小（bytes）
    mime_type = db.Column(db.String(100), nullable=True)
    file_hash = db.Column(db.String(64), nullable=True)  # 用於去重
    
    # === 分塊配置 ===
    chunk_size = db.Column(db.Integer, nullable=False, default=5242880)  # 5MB
    total_chunks = db.Column(db.Integer, nullable=False)
    
    # === 上傳進度追蹤（核心欄位）===
    uploaded_chunks = db.Column(db.JSON, nullable=False, default=list)
    # 格式: [0, 1, 2, 5, 7] - 已上傳的塊索引
    # 或更詳細: [{"index": 0, "hash": "abc123", "size": 5242880}, ...]
    
    # === 狀態管理 ===
    status = db.Column(
        db.String(20), 
        nullable=False, 
        default='pending',
        index=True
    )
    # 狀態值:
    # - pending: 已初始化，尚未開始上傳
    # - uploading: 上傳中
    # - merging: 正在合併分塊
    # - completed: 已完成
    # - failed: 失敗
    # - expired: 已過期
    
    # === 儲存路徑 ===
    temp_dir = db.Column(db.String(512), nullable=False)
    # Local: "uploads/temp/user_123/upload_uuid/"
    # Supabase: "temp/user_123/upload_uuid/"
    
    storage_path = db.Column(db.String(512), nullable=True)
    # 完成後的最終路徑，對應到 File.file_path
    
    storage_mode = db.Column(db.String(20), nullable=False)
    # "local" 或 "supabase"
    
    # === 時間戳記 ===
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    # 預設 24 小時後過期: created_at + timedelta(hours=24)
    
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # === 關聯到最終檔案 ===
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    # 完成後指向建立的 File 記錄
    
    # === 輔助方法 ===
    
    def get_progress_percentage(self) -> float:
        """計算上傳進度百分比"""
        if self.total_chunks == 0:
            return 0.0
        return (len(self.uploaded_chunks) / self.total_chunks) * 100
    
    def get_uploaded_size(self) -> int:
        """計算已上傳的大小（bytes）"""
        return len(self.uploaded_chunks) * self.chunk_size
    
    def is_complete(self) -> bool:
        """檢查是否所有塊都已上傳"""
        return len(self.uploaded_chunks) == self.total_chunks
    
    def is_expired(self) -> bool:
        """檢查是否已過期"""
        return datetime.utcnow() > self.expires_at
    
    def get_missing_chunks(self) -> list:
        """取得尚未上傳的塊索引"""
        all_chunks = set(range(self.total_chunks))
        uploaded = set(self.uploaded_chunks)
        return sorted(list(all_chunks - uploaded))
    
    def mark_chunk_uploaded(self, chunk_index: int) -> None:
        """標記某個塊已上傳（冪等操作）"""
        if chunk_index not in self.uploaded_chunks:
            self.uploaded_chunks.append(chunk_index)
            self.uploaded_chunks.sort()
            
            if self.status == 'pending':
                self.status = 'uploading'
            
            self.updated_at = datetime.utcnow()
            
            # 使用 flag_modified 確保 JSON 欄位更新
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(self, 'uploaded_chunks')
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'chunk_size': self.chunk_size,
            'total_chunks': self.total_chunks,
            'uploaded_chunks': self.uploaded_chunks,
            'missing_chunks': self.get_missing_chunks(),
            'status': self.status,
            'progress': self.get_progress_percentage(),
            'uploaded_size': self.get_uploaded_size(),
            'storage_mode': self.storage_mode,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        return f'<ChunkedUpload {self.id} ({self.get_progress_percentage():.1f}%)>'
```

---

### **方案 B：利用 Supabase Multipart Upload（進階）**

如果使用 Supabase Storage，可以利用其原生的 Multipart Upload API：

```python
class ChunkedUpload(db.Model):
    """
    追蹤分塊上傳的狀態
    支援 Supabase Multipart Upload
    """
    
    # ... (基本欄位同方案 A)
    
    # === Supabase 專用欄位 ===
    supabase_upload_id = db.Column(db.String(255), nullable=True)
    # Supabase 返回的 multipart upload ID
    
    supabase_part_etags = db.Column(db.JSON, nullable=True, default=list)
    # 格式: [{"PartNumber": 1, "ETag": "abc123"}, ...]
    # Supabase 每個 part 的 ETag
    
    def add_supabase_part(self, part_number: int, etag: str) -> None:
        """記錄 Supabase part 的 ETag"""
        if self.supabase_part_etags is None:
            self.supabase_part_etags = []
        
        self.supabase_part_etags.append({
            'PartNumber': part_number,
            'ETag': etag
        })
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'supabase_part_etags')
```

---

## 🔑 關鍵設計決策

### **1. `uploaded_chunks` 欄位設計**

**選項 A：簡單陣列（推薦）**
```python
uploaded_chunks = db.Column(db.JSON, default=list)
# 值: [0, 1, 2, 5, 7]
```

**優點：**
- 簡單直觀
- 查詢快速：`len(uploaded_chunks)` 即可得知進度
- 支援斷點續傳：缺失的塊 = `set(range(total)) - set(uploaded_chunks)`

**選項 B：詳細物件陣列**
```python
uploaded_chunks = db.Column(db.JSON, default=list)
# 值: [
#   {"index": 0, "hash": "abc123", "size": 5242880, "uploaded_at": "2025-12-04T10:00:00"},
#   {"index": 1, "hash": "def456", "size": 5242880, "uploaded_at": "2025-12-04T10:00:05"}
# ]
```

**優點：**
- 可驗證每個塊的完整性（hash）
- 可追蹤每個塊的上傳時間
- 支援更細緻的錯誤處理

**缺點：**
- 資料量較大
- 查詢稍複雜

**建議：先用選項 A，需要時再升級到選項 B**

---

### **2. 是否需要 Blob Storage 特性？**

#### **Local Storage 模式：**
```
不需要 Blob Storage 特性

流程：
1. 前端上傳分塊 → 後端儲存到 temp_dir
2. 所有塊上傳完成 → 後端合併成完整檔案
3. 移動到最終位置 → 刪除 temp_dir
```

**資料庫只需追蹤：**
- `uploaded_chunks`: 哪些塊已上傳
- `temp_dir`: 暫存位置
- `status`: 當前狀態

---

#### **Supabase Storage 模式：**
```
可選擇利用 Multipart Upload API

選項 1：自己管理分塊（同 Local）
- 上傳到 temp bucket
- 合併後上傳到 final bucket

選項 2：使用 Supabase Multipart Upload
- 呼叫 createMultipartUpload()
- 上傳每個 part 並記錄 ETag
- 呼叫 completeMultipartUpload()
```

**如果使用選項 2，資料庫需額外追蹤：**
- `supabase_upload_id`: Multipart upload ID
- `supabase_part_etags`: 每個 part 的 ETag

**建議：**
- 初期使用選項 1（統一邏輯，簡單）
- 需要更好效能時升級到選項 2

---

### **3. 與現有 `File` 模型的關係**

```python
# ChunkedUpload 完成後建立 File 記錄
chunked_upload.status = 'completed'
chunked_upload.completed_at = datetime.utcnow()

# 建立最終檔案記錄
file = File(
    filename=chunked_upload.filename,
    original_filename=chunked_upload.original_filename,
    file_path=chunked_upload.storage_path,  # 最終路徑
    file_size=chunked_upload.file_size,
    mime_type=chunked_upload.mime_type,
    user_id=chunked_upload.user_id
)
db.session.add(file)
db.session.commit()

# 關聯
chunked_upload.file_id = file.id
db.session.commit()
```

**關係：**
- `ChunkedUpload` 是暫時性的上傳追蹤記錄
- `File` 是永久性的檔案記錄
- 一個 `ChunkedUpload` 完成後對應一個 `File`

---

## 📋 資料庫遷移

新增 migration：

```python
# migrations/versions/xxx_add_chunked_upload.py

def upgrade():
    op.create_table(
        'chunked_uploads',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.BigInteger, nullable=False),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('chunk_size', sa.Integer, nullable=False),
        sa.Column('total_chunks', sa.Integer, nullable=False),
        sa.Column('uploaded_chunks', sa.JSON, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('temp_dir', sa.String(512), nullable=False),
        sa.Column('storage_path', sa.String(512)),
        sa.Column('storage_mode', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('file_id', sa.Integer, sa.ForeignKey('files.id')),
    )
    
    # 建立索引
    op.create_index('ix_chunked_uploads_user_id', 'chunked_uploads', ['user_id'])
    op.create_index('ix_chunked_uploads_status', 'chunked_uploads', ['status'])