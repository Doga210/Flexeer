#!/bin/bash
echo "🚀 بدء تشغيل مشروع Flexeer..."

# تهيئة قاعدة البيانات إذا لم تكن موجودة
if [ ! -f "Flexeer/flexeer.db" ]; then
    echo "📦 تهيئة قاعدة البيانات لأول مرة..."
    python3 Flexeer/init_db.py
fi

# تشغيل تطبيق الويب في الخلفية
echo "🌐 تشغيل تطبيق الويب على http://0.0.0.0:8080"
python3 Flexeer/api/index.py &

# تشغيل بوت التلجرام
echo "🤖 تشغيل بوت التلجرام..."
python3 auto_forward.py
