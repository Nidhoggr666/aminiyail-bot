FROM python:3.11-slim

WORKDIR /app

# تثبيت المكتبات الأساسية
RUN apt-get update && apt-get install -y \
    git \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p models lora_adapters uploads generated_images

# تعريف المنفذ
EXPOSE 7860

# متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# تشغيل التطبيق
CMD ["python", "app.py"]
