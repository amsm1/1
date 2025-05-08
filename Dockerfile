# استخدام صورة أساسية خفيفة مع Python 3.9
FROM python:3.9-slim

# تثبيت الحزم النظامية المطلوبة للبناء
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير root لتشغيل التطبيق
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# تعيين مجلد العمل ونسخ الملفات
WORKDIR /app
COPY --chown=user ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY --chown=user . .

# فتح المنفذ المطلوب لـ Hugging Face Spaces
EXPOSE 7860

# تشغيل التطبيق باستخدام خادم إنتاج (Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "--workers", "2", "app:app"]