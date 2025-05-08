from flask import Flask, request, jsonify  
import os  
import requests  
from flask_cors import CORS  
  
app = Flask(__name__)  
CORS(app, resources={r"/summarize": {"origins": "*"}})  
  
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"  
TIMEOUT = 90  
MIN_WORD_COUNT = 10  # تغيير الشرط إلى عدد الكلمات  
  
@app.route('/')  
def home():  
    return jsonify({  
        "message": "مرحبا! استخدم /summarize لتلخيص النصوص",  
        "example_request": {  
            "url": "/summarize",  
            "method": "POST",  
            "body": {"text": "النص الذي تريد تلخيصه هنا..."}  
        }  
    })  
  
@app.route('/summarize', methods=['POST'])  
def summarize():  
    try:  
        if not request.is_json:  
            return jsonify({"error": "يجب إرسال البيانات بصيغة JSON"}), 400  
  
        data = request.get_json()  
        text = data.get('text', '').strip()  
  
        # حساب عدد الكلمات الأصلية  
        original_words = len(text.split()) if text else 0  
  
        # التحقق من الحد الأدنى لعدد الكلمات  
        if original_words < MIN_WORD_COUNT:  
            return jsonify({  
                "error": f"النص قصير جدًا! الحد الأدنى {MIN_WORD_COUNT} كلمة",  
                "word_count": original_words  
            }), 400  
  
        # إعداد معاملات النموذج  
        payload = {  
            "inputs": text,  
            "parameters": {  
                "max_length": 300,  
                "min_length": max(50, int(original_words * 0.2)),  
                "do_sample": True,  
                "no_repeat_ngram_size": 3  
            }  
        }  
  
        # إرسال الطلب إلى Hugging Face  
        response = requests.post(  
            API_URL,  
            headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"},  
            json=payload,  
            timeout=TIMEOUT  
        )  
  
        # معالجة الاستجابة  
        if response.status_code != 200:  
            error_data = response.json()  
            return jsonify({  
                "error": "خطأ من واجهة Hugging Face",  
                "details": error_data.get('error', 'Unknown error'),  
                "status_code": response.status_code  
            }), 502  
  
        result = response.json()  
          
        if isinstance(result, list) and len(result) > 0:  
            summary_text = result[0].get('summary_text', '').strip()  
            summary_words = len(summary_text.split())  # حساب كلمات الملخص  
  
            return jsonify({  
                "summary": summary_text,  
                "original_words": original_words,  # إرسال عدد الكلمات  
                "summary_words": summary_words  
            })  
              
        return jsonify({"error": "تنسيق الاستجابة غير متوقع"}), 500  
  
    except requests.Timeout:  
        return jsonify({"error": "انتهت مهلة الاتصال بالنموذج"}), 504  
          
    except requests.RequestException as e:  
        return jsonify({"error": f"فشل الاتصال: {str(e)}"}), 503  
          
    except Exception as e:  
        return jsonify({"error": f"خطأ داخلي: {str(e)}"}), 500  
  
if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=7860, debug=False)
