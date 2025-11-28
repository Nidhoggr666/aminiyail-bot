"""
ملف التشغيل على Hugging Face Spaces
"""

import os
import gradio as gr
from telegram_bot import AminiyailBot
import threading
import time

# الحصول على التوكن من متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN", "8233239391:AAFG8BxIRYqMu5ApfV7euoX8wyAgvIkbrIg")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# إعداد متغير البيئة للصور
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

# متغير عام للبوت
bot_instance = None
bot_thread = None
bot_status = "غير مشغل"

def start_bot():
    """تشغيل البوت في خيط منفصل"""
    global bot_instance, bot_status
    
    try:
        bot_status = "جاري التشغيل..."
        bot_instance = AminiyailBot(BOT_TOKEN)
        bot_instance.run()
    except Exception as e:
        bot_status = f"خطأ: {str(e)}"
        print(f"خطأ في تشغيل البوت: {e}")

def get_bot_status():
    """الحصول على حالة البوت"""
    return bot_status

def get_stats():
    """الحصول على الإحصائيات"""
    if bot_instance and bot_instance.memory:
        conv_count = bot_instance.memory.get_conversation_count()
        return f"""
📊 **إحصائيات البوت**

💬 عدد المحادثات: {conv_count}
🎓 التدريب التالي عند: {bot_instance.training_threshold} محادثة
📈 التقدم: {min(conv_count % bot_instance.training_threshold, bot_instance.training_threshold)}/{bot_instance.training_threshold}
        """
    return "البوت غير مشغل بعد"

# بدء البوت تلقائيًا عند التشغيل
def auto_start():
    global bot_thread, bot_status
    bot_status = "جاري البدء..."
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    time.sleep(2)
    bot_status = "يعمل ✅"

# واجهة Gradio
with gr.Blocks(title="بوت الحكيم أمينيائيل", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🌊 بوت الحكيم أمينيائيل الذكي
    
    **ⴰⵎⵏⵉⵢⵉⵍ ⵢⵉ ⵉⵡⴰⵢⵍ**
    
    بوت تيليجرام ذكي يتعلم تدريجيًا من كل تفاعل
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("""
            ## 📱 كيفية الاستخدام
            
            1. افتح تيليجرام
            2. ابحث عن: **@Nidhoggr666_Bot**
            3. اضغط **Start** أو أرسل `/start`
            4. ابدأ الدردشة!
            
            ## ✨ المميزات
            
            - 🧠 يتعلم من محادثاتك
            - 💾 يحفظ كل شيء
            - 🎨 يولد صور
            - 📚 يقرأ الملفات
            - 🌍 يفهم العربية والأمازيغية
            """)
            
        with gr.Column():
            status_box = gr.Textbox(
                label="حالة البوت",
                value=bot_status,
                interactive=False
            )
            
            stats_box = gr.Textbox(
                label="الإحصائيات",
                value="جاري التحميل...",
                interactive=False,
                lines=6
            )
            
            refresh_btn = gr.Button("🔄 تحديث الإحصائيات")
            refresh_btn.click(fn=get_stats, outputs=stats_box)
            
    gr.Markdown("""
    ## 🔗 الروابط المهمة
    
    - **رابط البوت**: [t.me/Nidhoggr666_Bot](https://t.me/Nidhoggr666_Bot)
    - **الكود المصدري**: متاح في هذا Space
    
    ---
    
    **صُنع بكل حب للحكيم أمينيائيل** 💙
    """)
    
    # تحديث تلقائي للحالة
    demo.load(fn=get_stats, outputs=stats_box, every=30)

# بدء البوت تلقائيًا
auto_start()

# تشغيل Gradio
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
