from flask import Flask, render_template_string, request, jsonify
import random
import os
import json
from datetime import datetime

app = Flask(__name__)

# База данных экспертов
EXPERTS = [
    {
        "name": "Александр Смирнов",
        "specialization": ["Строительство", "Производство", "Логистика"],
        "response_time": "15 минут",
        "expertise_level": "Эксперт высшей категории"
    },
    {
        "name": "Елена Васильева",
        "specialization": ["Торговля", "Финансы", "Маркетинг"],
        "response_time": "10 минут",
        "expertise_level": "Бизнес-консультант"
    },
    {
        "name": "Михаил Козлов",
        "specialization": ["IT", "Маркетинг", "Производство"],
        "response_time": "20 минут",
        "expertise_level": "Технический директор"
    },
    {
        "name": "Ольга Новикова",
        "specialization": ["Образование", "Логистика", "Общепит", "Финансы"],
        "response_time": "25 минут",
        "expertise_level": "Старший консультант"
    }
]

INDUSTRIES = [
    "Строительство", "Торговля", "Образование", "Производство",
    "IT", "Маркетинг", "Финансы", "Логистика", "Общепит"
]

# Файл для хранения вопросов
QUESTIONS_FILE = "questions.json"

def save_question(email, question, industry, expert):
    """Сохраняет вопрос в файл"""
    question_data = {
        "email": email,
        "question": question,
        "industry": industry,
        "expert": expert["name"],
        "asked_at": datetime.now().isoformat()
    }
    
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except:
        questions = []
    
    questions.append(question_data)
    
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Контур Эксперт - Чат-бот консультаций</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Inter', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 600px;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            padding: 25px 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 28px;
            margin-bottom: 5px;
            letter-spacing: 1px;
        }
        
        .chat-header p {
            font-size: 14px;
            opacity: 0.95;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.bot {
            justify-content: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #ffdec2;
        }
        
        .user .message-content {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
        }
        
        .industry-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .industry-btn {
            background: #fff5ed;
            border: 1px solid #ffdec2;
            padding: 10px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 12px;
            color: #ff6b35;
            font-weight: 500;
        }
        
        .industry-btn:hover {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            border: 1px solid transparent;
            transform: translateY(-2px);
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #f0f0f0;
        }
        
        .chat-input input {
            width: 100%;
            padding: 12px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .chat-input input:focus {
            outline: none;
            border-color: #ff6b35;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        .input-group input {
            flex: 1;
            margin-bottom: 0;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.3s;
            font-weight: 600;
        }
        
        .chat-input button:hover {
            transform: scale(1.02);
        }
        
        .expert-card {
            background: #fff5ed;
            padding: 15px;
            border-radius: 12px;
            margin-top: 10px;
            border-left: 4px solid #ff6b35;
        }
        
        .expert-name {
            font-weight: bold;
            color: #ff6b35;
            font-size: 16px;
        }
        
        .expert-detail {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .typing {
            color: #ff6b35;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤵 КОНТУР ЭКСПЕРТ</h1>
            <p>Профессиональные консультации для вашего бизнеса</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    👋 Здравствуйте! Я помогу вам связаться с экспертом.<br>
                    Какой у Вас вопрос к эксперту?
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="email" id="emailInput" placeholder="📧 Ваш email для ответа" />
            <div class="input-group">
                <input type="text" id="questionInput" placeholder="💬 Введите ваш вопрос..." />
                <button onclick="sendQuestion()">Отправить</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentState = 'awaiting_question';
        let userQuestion = '';
        let userEmail = '';
        
        function addMessage(text, isUser = false) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            messageDiv.innerHTML = `<div class="message-content">${text}</div>`;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addIndustryButtons() {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            let industries = {{ industries | tojson }};
            let buttonsHtml = '<div class="message-content">📋 Пожалуйста, выберите вашу отрасль:<br><br><div class="industry-buttons">';
            industries.forEach(industry => {
                buttonsHtml += `<button class="industry-btn" onclick="selectIndustry('${industry}')">${industry}</button>`;
            });
            buttonsHtml += '</div></div>';
            
            messageDiv.innerHTML = buttonsHtml;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function selectIndustry(industry) {
            addMessage(industry, true);
            addMessage('<div class="typing">🔍 Подбираем лучшего эксперта...</div>');
            
            try {
                const response = await fetch('/find_expert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        industry: industry,
                        question: userQuestion,
                        email: userEmail
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const expertHtml = `
                        <div class="expert-card">
                            <div class="expert-name">🤵 ${data.expert.name}</div>
                            <div class="expert-detail">📊 ${data.expert.expertise_level}</div>
                            <div class="expert-detail">🎯 Специализация: ${data.expert.specialization.join(', ')}</div>
                            <div class="expert-detail">⏱️ Время ожидания: ${data.expert.response_time}</div>
                            <div class="expert-detail">💼 Ваша отрасль: ${data.industry}</div>
                            <div class="expert-detail">📧 Ответ придёт на: ${userEmail}</div>
                        </div>
                        <br>✨ Эксперт ${data.expert.name} подготовит ответ.<br>
                        ⏰ В течение ${data.expert.response_time} вы получите консультацию на почту.<br>
                        Спасибо за обращение!
                    `;
                    addMessage(expertHtml);
                    addMessage('📧 Письмо-подтверждение отправлено на вашу почту!', false);
                } else {
                    addMessage('❌ Извините, произошла ошибка: ' + (data.error || 'Неизвестная ошибка'), false);
                }
            } catch (error) {
                addMessage('❌ Ошибка соединения. Пожалуйста, обновите страницу и попробуйте снова.', false);
            }
            
            currentState = 'completed';
        }
        
        async function sendQuestion() {
            if (currentState !== 'awaiting_question') return;
            
            const emailInput = document.getElementById('emailInput');
            const questionInput = document.getElementById('questionInput');
            
            const email = emailInput.value.trim();
            const question = questionInput.value.trim();
            
            if (!email) {
                addMessage('⚠️ Пожалуйста, укажите ваш email для получения ответа.', false);
                return;
            }
            
            if (!question) {
                addMessage('⚠️ Пожалуйста, введите ваш вопрос.', false);
                return;
            }
            
            if (!email.includes('@') || !email.includes('.')) {
                addMessage('⚠️ Пожалуйста, введите корректный email (например: name@mail.ru).', false);
                return;
            }
            
            addMessage(question, true);
            userQuestion = question;
            userEmail = email;
            
            addMessage('✅ Ваш вопрос принят! Теперь выберите вашу отрасль.', false);
            addIndustryButtons();
            
            currentState = 'awaiting_industry';
            questionInput.value = '';
            questionInput.disabled = true;
            emailInput.disabled = true;
        }
        
        // Отправка по Enter
        document.addEventListener('DOMContentLoaded', function() {
            const input = document.getElementById('questionInput');
            if (input) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendQuestion();
                    }
                });
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    print("Главная страница загружена")
    return render_template_string(HTML_TEMPLATE, industries=INDUSTRIES)

@app.route('/find_expert', methods=['POST'])
def find_expert():
    print("=" * 50)
    print("Получен POST запрос на /find_expert")
    
    try:
        data = request.get_json()
        print(f"Данные запроса: {data}")
        
        industry = data.get('industry')
        question = data.get('question')
        email = data.get('email')
        
        print(f"Отрасль: {industry}")
        print(f"Email: {email}")
        print(f"Вопрос: {question[:100] if question else 'None'}...")
        
        # Ищем подходящего эксперта
        suitable_experts = [e for e in EXPERTS if industry in e['specialization']]
        print(f"Найдено подходящих экспертов: {len(suitable_experts)}")
        
        if suitable_experts:
            expert = random.choice(suitable_experts)
        else:
            expert = EXPERTS[0]
        
        print(f"Выбран эксперт: {expert['name']}")
        
        # Сохраняем вопрос в файл
        try:
            save_question(email, question, industry, expert)
            print("Вопрос сохранён в questions.json")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
        
        response = {
            'success': True,
            'expert': expert,
            'industry': industry,
            'question': question
        }
        
        print(f"Отправляем ответ: {response}")
        print("=" * 50)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"ОШИБКА в /find_expert: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Для хостинга на Render
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Запуск веб-чата...")
    print("📱 Откройте в браузере: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=port, debug=True)