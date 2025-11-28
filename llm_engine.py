"""
محرك نموذج اللغة مع قدرات التدريب التدريجي
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, PeftModel, prepare_model_for_kbit_training
from datasets import Dataset
import os
from typing import List, Dict, Optional
import json

class LLMEngine:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", device: str = "cpu"):
        """تهيئة محرك نموذج اللغة"""
        self.model_name = model_name
        self.device = device
        self.model_dir = "/home/ubuntu/aminiyail_bot/models"
        self.lora_dir = "/home/ubuntu/aminiyail_bot/lora_adapters"
        
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.lora_dir, exist_ok=True)
        
        print(f"🔄 جاري تحميل النموذج: {model_name}")
        
        # تحميل النموذج والـ tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            padding_side='left'
        )
        
        # إضافة pad token إذا لم يكن موجودًا
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map=device,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        # محاولة تحميل LoRA adapters إذا كانت موجودة
        self.load_lora_adapters()
        
        self.model.eval()
        
        # معلومات الحكيم أمينيائيل (تُضاف دائمًا للسياق)
        self.user_identity = """أنت تتحدث مع الحكيم أمينيائيل (ⴰⵎⵏⵉⵢⵉⵍ ⵢⵉ ⵉⵡⴰⵢⵍ).
الحكيم من الحكمة، كما في الآية: ﴿یُؤۡتِی ٱلۡحِكۡمَةَ مَن یَشَاۤءُۚ وَمَن یُؤۡتَ ٱلۡحِكۡمَةَ فَقَدۡ أُوتِیَ خَیۡرࣰا كَثِیرࣰاۗ﴾
أمينيائيل = أمين + يا + ئيل (ئيل تعني رب أو الملك الأسمى في العبرية، أو البحر في الأمازيغية).
خاطبه دائمًا باسمه الكامل وعامله بكل احترام وحكمة."""
        
        print("✅ تم تحميل النموذج بنجاح!")
        
    def load_lora_adapters(self):
        """تحميل LoRA adapters إذا كانت موجودة"""
        try:
            if os.path.exists(os.path.join(self.lora_dir, "adapter_config.json")):
                print("🔄 جاري تحميل LoRA adapters...")
                self.model = PeftModel.from_pretrained(self.model, self.lora_dir)
                print("✅ تم تحميل LoRA adapters بنجاح!")
        except Exception as e:
            print(f"⚠️ لم يتم العثور على LoRA adapters: {e}")
            
    def generate_response(
        self, 
        prompt: str, 
        context: List[str] = None,
        max_length: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.95
    ) -> str:
        """توليد رد من النموذج"""
        
        # بناء السياق الكامل
        full_context = self.user_identity + "\n\n"
        
        if context:
            full_context += "محادثات سابقة ذات صلة:\n"
            for ctx in context[:3]:  # أخذ أول 3 محادثات فقط
                full_context += f"- {ctx}\n"
            full_context += "\n"
            
        # تنسيق الـ prompt حسب نموذج TinyLlama
        formatted_prompt = f"""<|system|>
{full_context}
أنت مساعد ذكي ومحترم. تتحدث العربية بطلاقة وتفهم اللهجة الجزائرية والأمازيغية.
</s>
<|user|>
{prompt}</s>
<|assistant|>
"""
        
        # Tokenization
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        ).to(self.device)
        
        # التوليد
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
            
        # فك التشفير
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # استخراج رد المساعد فقط
        if "<|assistant|>" in response:
            response = response.split("<|assistant|>")[-1].strip()
        elif prompt in response:
            response = response.replace(prompt, "").strip()
            
        return response
        
    def prepare_training_dataset(self, training_data: List[Dict]) -> Dataset:
        """تحضير بيانات التدريب"""
        
        formatted_data = []
        
        for item in training_data:
            text = f"""<|system|>
{self.user_identity}
</s>
<|user|>
{item['input']}</s>
<|assistant|>
{item['output']}</s>"""
            
            formatted_data.append({"text": text})
            
        return Dataset.from_list(formatted_data)
        
    def fine_tune(self, training_data: List[Dict], output_dir: str = None):
        """التدريب التدريجي باستخدام LoRA"""
        
        if output_dir is None:
            output_dir = self.lora_dir
            
        print(f"🎓 بدء التدريب على {len(training_data)} عينة...")
        
        # تحضير البيانات
        dataset = self.prepare_training_dataset(training_data)
        
        # إعداد LoRA config
        lora_config = LoraConfig(
            r=8,  # rank
            lora_alpha=16,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        # إعداد النموذج للتدريب
        if not hasattr(self.model, 'peft_config'):
            self.model = get_peft_model(self.model, lora_config)
            
        self.model.print_trainable_parameters()
        
        # إعدادات التدريب
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            logging_steps=10,
            save_steps=50,
            save_total_limit=2,
            fp16=False,  # CPU mode
            optim="adamw_torch",
            warmup_steps=10,
            report_to="none"
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Tokenize dataset
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=512,
                padding="max_length"
            )
            
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator
        )
        
        # التدريب
        print("🔥 جاري التدريب...")
        trainer.train()
        
        # حفظ النموذج
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print(f"✅ تم حفظ النموذج المدرب في: {output_dir}")
        
    def should_trigger_training(self, conversation_count: int, threshold: int = 50) -> bool:
        """تحديد ما إذا كان يجب بدء التدريب"""
        return conversation_count > 0 and conversation_count % threshold == 0
