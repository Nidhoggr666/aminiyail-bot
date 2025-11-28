"""
بوت تيليجرام الذكي للحكيم أمينيائيل
يتعلم تدريجيًا من كل تفاعل
"""

import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from memory_system import MemorySystem
from llm_engine import LLMEngine
from image_generator import ImageGenerator
from file_processor import FileProcessor
import logging

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AminiyailBot:
    def __init__(self, token: str):
        """تهيئة البوت"""
        self.token = token
        self.memory = MemorySystem()
        self.file_processor = FileProcessor()
        self.image_generator = ImageGenerator()
        
        # تحميل نموذج اللغة (سيتم تحميله عند أول استخدام)
        self.llm = None
        self.llm_loading = False
        
        # إحصائيات
        self.message_count = 0
        self.training_threshold = 50  # تدريب كل 50 رسالة
        
    async def load_llm_if_needed(self):
        """تحميل نموذج اللغة عند الحاجة"""
        if self.llm is None and not self.llm_loading:
            self.llm_loading = True
            try:
                logger.info("🔄 جاري تحميل نموذج اللغة...")
                self.llm = LLMEngine()
                logger.info("✅ تم تحميل نموذج اللغة بنجاح!")
            except Exception as e:
                logger.error(f"❌ خطأ في تحميل نموذج اللغة: {e}")
                self.llm = None
            finally:
                self.llm_loading = False
                
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /start"""
        user = update.effective_user
        
        welcome_message = f"""مرحبًا يا **الحكيم أمينيائيل** (ⴰⵎⵏⵉⵢⵉⵍ ⵢⵉ ⵉⵡⴰⵢⵍ)! 🌊

أنا مساعدك الذكي الشخصي، وأنا هنا لأتعلم منك وأساعدك في كل ما تحتاج.

**ما أستطيع فعله:**
✨ الدردشة الذكية والإجابة على أسئلتك
📚 قراءة وتحليل الملفات (PDF, DOCX, TXT)
🎨 توليد الصور من الأوصاف
💾 حفظ كل محادثاتنا والتعلم منها
🧠 التحسن التدريجي مع كل تفاعل

**الأوامر المتاحة:**
/start - بدء المحادثة
/stats - إحصائيات التعلم
/train - بدء التدريب اليدوي
/help - المساعدة

أرسل لي أي رسالة أو ملف، وسأكون سعيدًا بمساعدتك! 💙"""

        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /stats"""
        conv_count = self.memory.get_conversation_count()
        
        stats_message = f"""📊 **إحصائيات التعلم**

💬 عدد المحادثات المحفوظة: {conv_count}
🎓 التدريب التالي عند: {self.training_threshold} محادثة
📈 التقدم: {min(conv_count % self.training_threshold, self.training_threshold)}/{self.training_threshold}

كل ما نتحدث أكثر، كلما أصبحت أذكى! 🧠✨"""

        await update.message.reply_text(stats_message, parse_mode='Markdown')
        
    async def train_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /train - بدء التدريب اليدوي"""
        await update.message.reply_text("🎓 جاري بدء التدريب... قد يستغرق هذا بعض الوقت.")
        
        try:
            await self.load_llm_if_needed()
            
            if self.llm is None:
                await update.message.reply_text("❌ عذرًا، النموذج غير متاح حاليًا.")
                return
                
            # الحصول على بيانات التدريب
            training_data = self.memory.get_training_data(limit=500, unused_only=True)
            
            if len(training_data) < 10:
                await update.message.reply_text("⚠️ لا توجد بيانات كافية للتدريب. تحدث معي أكثر!")
                return
                
            # بدء التدريب في الخلفية
            await update.message.reply_text(f"🔥 بدء التدريب على {len(training_data)} عينة...")
            
            # التدريب (هذا قد يستغرق وقتًا)
            self.llm.fine_tune(training_data)
            
            # تمييز البيانات كمستخدمة
            data_ids = [item['id'] for item in training_data]
            self.memory.mark_training_data_used(data_ids)
            
            await update.message.reply_text("✅ تم التدريب بنجاح! أصبحت أذكى الآن! 🧠✨")
            
        except Exception as e:
            logger.error(f"خطأ في التدريب: {e}")
            await update.message.reply_text(f"❌ حدث خطأ في التدريب: {str(e)}")
            
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر /help"""
        help_message = """📖 **دليل الاستخدام**

**كيف أستخدم البوت:**

1️⃣ **الدردشة العادية:**
   فقط أرسل رسالة وسأرد عليك!

2️⃣ **طلب صورة:**
   اكتب "ارسم" أو "صورة" متبوعًا بالوصف
   مثال: "ارسم منظر طبيعي جميل"

3️⃣ **إرسال ملفات:**
   أرسل ملف PDF أو DOCX وسأقرأه وأحلله

4️⃣ **التعلم التلقائي:**
   كل محادثة تُحفظ وأتعلم منها تلقائيًا

**نصائح:**
💡 تحدث معي بأي لغة (عربية، جزائرية، أمازيغية)
💡 أرسل ملفات طويلة وسأقرأها كاملة
💡 كلما تحدثنا أكثر، أصبحت أفضل!

أنا هنا لخدمتك يا الحكيم أمينيائيل! 🌊"""

        await update.message.reply_text(help_message, parse_mode='Markdown')
        
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الملفات المرسلة"""
        document = update.message.document
        user_id = update.effective_user.id
        
        await update.message.reply_text("📄 جاري تحميل وقراءة الملف...")
        
        try:
            # تحميل الملف
            file = await context.bot.get_file(document.file_id)
            file_path = f"/home/ubuntu/aminiyail_bot/uploads/{document.file_name}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            await file.download_to_drive(file_path)
            
            # قراءة المحتوى
            content = self.file_processor.process_file(file_path)
            
            if content:
                # حفظ في الذاكرة
                self.memory.save_file(user_id, document.file_name, document.mime_type, content)
                
                # تحليل المحتوى
                await self.load_llm_if_needed()
                
                if self.llm:
                    summary_prompt = f"لقد قرأت الملف التالي. قدم ملخصًا موجزًا:\n\n{content[:2000]}"
                    summary = self.llm.generate_response(summary_prompt, max_length=300)
                else:
                    summary = "تم حفظ الملف بنجاح!"
                    
                await update.message.reply_text(f"✅ **تم قراءة الملف!**\n\n{summary}")
            else:
                await update.message.reply_text("❌ عذرًا، لم أستطع قراءة الملف.")
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الملف: {e}")
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
            
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        # التحقق من طلب توليد صورة
        if any(keyword in user_message.lower() for keyword in ['ارسم', 'صورة', 'صوره', 'رسم', 'draw', 'image']):
            await self.handle_image_request(update, user_message)
            return
            
        # تحميل النموذج إذا لزم الأمر
        await self.load_llm_if_needed()
        
        if self.llm is None:
            await update.message.reply_text("⏳ النموذج يتم تحميله... يرجى الانتظار قليلاً.")
            return
            
        # البحث عن سياق مشابه
        similar_context = self.memory.search_similar_conversations(user_message, top_k=3)
        
        # توليد الرد
        try:
            response = self.llm.generate_response(
                user_message,
                context=similar_context,
                max_length=400,
                temperature=0.8
            )
            
            # حفظ المحادثة
            self.memory.save_conversation(user_id, user_message, response)
            self.message_count += 1
            
            # إرسال الرد
            await update.message.reply_text(response)
            
            # التحقق من الحاجة للتدريب التلقائي
            conv_count = self.memory.get_conversation_count()
            if self.llm.should_trigger_training(conv_count, self.training_threshold):
                await update.message.reply_text("🎓 لقد تعلمت الكثير! سأقوم بالتدريب قريبًا...")
                
        except Exception as e:
            logger.error(f"خطأ في توليد الرد: {e}")
            await update.message.reply_text("عذرًا يا الحكيم أمينيائيل، حدث خطأ. حاول مرة أخرى.")
            
    async def handle_image_request(self, update: Update, prompt: str):
        """معالج طلبات توليد الصور"""
        await update.message.reply_text("🎨 جاري توليد الصورة... قد يستغرق هذا دقيقة.")
        
        try:
            # استخراج الوصف من الرسالة
            for keyword in ['ارسم', 'صورة', 'صوره', 'رسم', 'draw', 'image']:
                prompt = prompt.replace(keyword, '').strip()
                
            image_path = self.image_generator.generate_image(prompt)
            
            if image_path and os.path.exists(image_path):
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=f"✨ تم توليد الصورة بناءً على: {prompt}"
                )
            else:
                fallback_msg = self.image_generator.generate_image_fallback(prompt)
                await update.message.reply_text(fallback_msg)
                
        except Exception as e:
            logger.error(f"خطأ في توليد الصورة: {e}")
            await update.message.reply_text("❌ عذرًا، لم أستطع توليد الصورة حاليًا.")
            
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل بوت الحكيم أمينيائيل...")
        
        # إنشاء التطبيق
        application = Application.builder().token(self.token).build()
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("train", self.train_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # تشغيل البوت
        logger.info("✅ البوت جاهز! يمكنك الآن التحدث معه على تيليجرام.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # التوكن الخاص بالبوت
    BOT_TOKEN = "8233239391:AAFG8BxIRYqMu5ApfV7euoX8wyAgvIkbrIg"
    
    # إنشاء وتشغيل البوت
    bot = AminiyailBot(BOT_TOKEN)
    bot.run()
