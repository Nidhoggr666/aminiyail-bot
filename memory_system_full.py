"""
نظام الذاكرة والتخزين لبوت الحكيم أمينيائيل
يحفظ كل المحادثات والملفات والسياق
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class MemorySystem:
    def __init__(self, db_path: str = "aminiyail_memory.db"):
        """تهيئة نظام الذاكرة"""
        self.db_path = db_path
        self.init_database()
        
        # نموذج لتحويل النصوص إلى vectors للبحث الدلالي
        self.embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # FAISS index للبحث السريع
        self.dimension = 384  # بُعد الـ embeddings
        self.index = faiss.IndexFlatL2(self.dimension)
        self.text_store = []  # لحفظ النصوص المقابلة للـ vectors
        
        # تحميل البيانات الموجودة
        self.load_existing_memories()
        
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول معلومات المستخدم (الحكيم أمينيائيل)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY,
                name TEXT,
                full_name TEXT,
                description TEXT,
                preferences TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        # جدول المحادثات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT,
                bot_response TEXT,
                timestamp TIMESTAMP,
                context TEXT
            )
        ''')
        
        # جدول الملفات المرفوعة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT,
                file_type TEXT,
                content TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        # جدول بيانات التدريب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                output_text TEXT,
                category TEXT,
                timestamp TIMESTAMP,
                used_for_training INTEGER DEFAULT 0
            )
        ''')
        
        # إضافة ملف المستخدم الأساسي (الحكيم أمينيائيل)
        cursor.execute('''
            INSERT OR IGNORE INTO user_profile (id, name, full_name, description, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            1,
            'الحكيم أمينيائيل',
            'ⴰⵎⵏⵉⵢⵉⵍ ⵢⵉ ⵉⵡⴰⵢⵍ',
            'الحكيم من الحكمة، وأمينيائيل مركب من أمين + يا + ئيل (رب/الملك الأسمى في العبرية، أو البحر في الأمازيغية)',
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
    def load_existing_memories(self):
        """تحميل الذكريات الموجودة إلى FAISS"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_message, bot_response FROM conversations')
        rows = cursor.fetchall()
        
        for user_msg, bot_resp in rows:
            combined_text = f"{user_msg} {bot_resp}"
            self.text_store.append(combined_text)
            
        if self.text_store:
            embeddings = self.embedder.encode(self.text_store)
            self.index.add(np.array(embeddings).astype('float32'))
            
        conn.close()
        
    def save_conversation(self, user_id: int, user_message: str, bot_response: str, context: str = ""):
        """حفظ محادثة جديدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, user_message, bot_response, timestamp, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_message, bot_response, datetime.now(), context))
        
        conn.commit()
        conn.close()
        
        # إضافة إلى FAISS للبحث السريع
        combined_text = f"{user_message} {bot_response}"
        self.text_store.append(combined_text)
        embedding = self.embedder.encode([combined_text])
        self.index.add(np.array(embedding).astype('float32'))
        
        # حفظ كبيانات تدريب
        self.save_training_data(user_message, bot_response, "conversation")
        
    def save_training_data(self, input_text: str, output_text: str, category: str):
        """حفظ بيانات للتدريب المستقبلي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_data (input_text, output_text, category, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (input_text, output_text, category, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def save_file(self, user_id: int, file_name: str, file_type: str, content: str):
        """حفظ ملف مرفوع"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO uploaded_files (user_id, file_name, file_type, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, file_name, file_type, content, datetime.now()))
        
        conn.commit()
        conn.close()
        
    def search_similar_conversations(self, query: str, top_k: int = 5) -> List[str]:
        """البحث عن محادثات مشابهة"""
        if not self.text_store:
            return []
            
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.text_store):
                results.append(self.text_store[idx])
                
        return results
        
    def get_user_profile(self, user_id: int = 1) -> Dict:
        """الحصول على ملف المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profile WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'full_name': row[2],
                'description': row[3],
                'preferences': row[4],
                'created_at': row[5]
            }
        return {}
        
    def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على آخر المحادثات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp 
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'user_message': row[0],
                'bot_response': row[1],
                'timestamp': row[2]
            })
            
        return list(reversed(conversations))  # ترتيب من الأقدم للأحدث
        
    def get_training_data(self, limit: int = 1000, unused_only: bool = True) -> List[Dict]:
        """الحصول على بيانات التدريب"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if unused_only:
            cursor.execute('''
                SELECT id, input_text, output_text, category 
                FROM training_data 
                WHERE used_for_training = 0 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        else:
            cursor.execute('''
                SELECT id, input_text, output_text, category 
                FROM training_data 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
        rows = cursor.fetchall()
        conn.close()
        
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'input': row[1],
                'output': row[2],
                'category': row[3]
            })
            
        return data
        
    def mark_training_data_used(self, data_ids: List[int]):
        """تمييز بيانات التدريب كمستخدمة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for data_id in data_ids:
            cursor.execute('''
                UPDATE training_data 
                SET used_for_training = 1 
                WHERE id = ?
            ''', (data_id,))
            
        conn.commit()
        conn.close()
        
    def get_conversation_count(self) -> int:
        """الحصول على عدد المحادثات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
