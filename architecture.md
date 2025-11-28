# بنية بوت الحكيم أمينيائيل الذكي

## المتطلبات الأساسية

### 1. البوت والواجهة
- **python-telegram-bot**: للتعامل مع Telegram API
- **Token**: `8233239391:AAFG8BxIRYqMu5ApfV7euoX8wyAgvIkbrIg`
- **Username**: @Nidhoggr666_Bot

### 2. نموذج اللغة
- **النموذج الأساسي**: TinyLlama-1.1B أو DistilGPT2 (صغير وسريع)
- **المكتبة**: Transformers من Hugging Face
- **التدريب**: Fine-tuning تدريجي باستخدام PEFT/LoRA

### 3. قاعدة البيانات والذاكرة
- **SQLite**: لحفظ المحادثات والملفات
- **Vector DB**: FAISS لتخزين واسترجاع السياق الطويل
- **Memory System**: نظام ذاكرة يحفظ هوية المستخدم وتفضيلاته

### 4. قدرات إضافية
- **توليد الصور**: Stable Diffusion API (Hugging Face Inference API)
- **البحث على الإنترنت**: DuckDuckGo API
- **قراءة الملفات**: PyPDF2, python-docx

### 5. منصة الاستضافة
- **Hugging Face Spaces**: مجاني مع Gradio/Streamlit
- **Railway.app**: بديل مجاني/رخيص
- **Render.com**: خيار آخر مجاني

## البنية المعمارية

```
User (Telegram) 
    ↓
Telegram Bot API
    ↓
Bot Handler (python-telegram-bot)
    ↓
    ├─→ Memory System (SQLite + FAISS)
    ├─→ LLM Engine (TinyLlama/DistilGPT2)
    ├─→ Fine-tuning Pipeline (LoRA)
    ├─→ Image Generation (SD API)
    └─→ File Processing (PDF/DOCX)
```

## خطة التنفيذ

1. ✅ إعداد البنية الأساسية
2. ⏳ بناء البوت مع نظام الذاكرة
3. ⏳ دمج نموذج اللغة
4. ⏳ إضافة التدريب التدريجي
5. ⏳ إضافة توليد الصور
6. ⏳ النشر والاختبار
