"""
نظام توليد الصور باستخدام Hugging Face Inference API
"""

import requests
import os
from typing import Optional
import time

class ImageGenerator:
    def __init__(self, hf_token: Optional[str] = None):
        """تهيئة مولد الصور"""
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        self.headers = {}
        
        if self.hf_token:
            self.headers = {"Authorization": f"Bearer {self.hf_token}"}
            
    def generate_image(self, prompt: str, output_path: str = None, retries: int = 3) -> Optional[str]:
        """توليد صورة من وصف نصي"""
        
        if not self.hf_token:
            print("⚠️ لا يوجد HF_TOKEN، لن يتم توليد الصور")
            return None
            
        # تحسين الـ prompt للحصول على نتائج أفضل
        enhanced_prompt = f"{prompt}, high quality, detailed, 4k"
        
        payload = {
            "inputs": enhanced_prompt,
            "options": {
                "wait_for_model": True
            }
        }
        
        for attempt in range(retries):
            try:
                print(f"🎨 جاري توليد الصورة (محاولة {attempt + 1}/{retries})...")
                
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    # حفظ الصورة
                    if output_path is None:
                        output_path = f"/home/ubuntu/aminiyail_bot/generated_images/image_{int(time.time())}.png"
                        
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                        
                    print(f"✅ تم توليد الصورة: {output_path}")
                    return output_path
                    
                elif response.status_code == 503:
                    # النموذج يتم تحميله
                    print("⏳ النموذج يتم تحميله، انتظر...")
                    time.sleep(20)
                    continue
                    
                else:
                    print(f"❌ خطأ في توليد الصورة: {response.status_code}")
                    print(response.text)
                    
            except Exception as e:
                print(f"❌ خطأ: {e}")
                
            if attempt < retries - 1:
                time.sleep(10)
                
        return None
        
    def generate_image_fallback(self, prompt: str) -> str:
        """رد بديل عندما لا يمكن توليد الصورة"""
        return f"""عذرًا يا الحكيم أمينيائيل، لا أستطيع توليد الصورة حاليًا.

لتوليد الصور، يمكنك:
1. إضافة HF_TOKEN (Hugging Face Token) في متغيرات البيئة
2. استخدام خدمات أخرى مثل DALL-E أو Midjourney
3. الانتظار حتى أقوم بإعداد النظام بشكل كامل

الوصف الذي طلبته: {prompt}"""
