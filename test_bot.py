"""
سكريبت اختبار بسيط للبوت
"""

import os
import sys

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(__file__))

from memory_system import MemorySystem

def test_memory_system():
    """اختبار نظام الذاكرة"""
    print("🧪 اختبار نظام الذاكرة...")
    
    try:
        memory = MemorySystem()
        print("✅ تم إنشاء نظام الذاكرة بنجاح!")
        
        # اختبار حفظ محادثة
        memory.save_conversation(
            user_id=1,
            user_message="مرحبا يا صديقي",
            bot_response="مرحبًا يا الحكيم أمينيائيل! كيف يمكنني مساعدتك؟"
        )
        print("✅ تم حفظ محادثة تجريبية!")
        
        # اختبار البحث
        results = memory.search_similar_conversations("مرحبا", top_k=3)
        print(f"✅ تم البحث، النتائج: {len(results)}")
        
        # اختبار الإحصائيات
        count = memory.get_conversation_count()
        print(f"✅ عدد المحادثات: {count}")
        
        # اختبار ملف المستخدم
        profile = memory.get_user_profile()
        print(f"✅ ملف المستخدم: {profile['name']}")
        
        print("\n🎉 جميع الاختبارات نجحت!")
        return True
        
    except Exception as e:
        print(f"❌ فشل الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_token():
    """اختبار توكن البوت"""
    print("\n🧪 اختبار توكن البوت...")
    
    BOT_TOKEN = "8233239391:AAFG8BxIRYqMu5ApfV7euoX8wyAgvIkbrIg"
    
    try:
        import requests
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ البوت متصل!")
                print(f"   الاسم: {bot_info.get('first_name')}")
                print(f"   اسم المستخدم: @{bot_info.get('username')}")
                return True
        
        print(f"❌ فشل الاتصال بالبوت: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 اختبار بوت الحكيم أمينيائيل")
    print("=" * 50)
    
    # اختبار نظام الذاكرة
    memory_ok = test_memory_system()
    
    # اختبار توكن البوت
    token_ok = test_bot_token()
    
    print("\n" + "=" * 50)
    if memory_ok and token_ok:
        print("✅ جميع الاختبارات نجحت! البوت جاهز للعمل!")
    else:
        print("⚠️ بعض الاختبارات فشلت، راجع الأخطاء أعلاه")
    print("=" * 50)
