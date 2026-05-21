from flask import Flask, render_template_string, request, jsonify
import random
import os

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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Чат-бот для консультаций с экспертами</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);;
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f9f9f9;
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
            padding: 10px 15px;
            border-radius: 15px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .industry-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .industry-btn {
            background: #f0f0f0;
            border: none;
            padding: 10px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 12px;
        }
        
        .industry-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
        }
        
        .chat-input button {
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .chat-input button:hover {
            transform: scale(1.05);
        }
        
        .expert-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            border-left: 4px solid #667eea;
        }
        
        .expert-name {
            font-weight: bold;
            color: #667eea;
            font-size: 16px;
        }
        
        .expert-detail {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .typing {
            color: #999;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤵 Служба поддержки экспертов</h1>
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
        
        <div class="chat-input" style="flex-direction: column; gap: 10px;">
    <input type="email" id="emailInput" placeholder="Ваш email для ответа..." style="width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0;" />
    <div style="display: flex; gap: 10px;">
        <input type="text" id="questionInput" placeholder="Введите ваш вопрос..." style="flex: 1; padding: 10px; border-radius: 10px; border: 1px solid #e0e0e0;" />
        <button onclick="sendQuestion()" style="padding: 10px 20px; background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%); color: white; border: none; border-radius: 10px; cursor: pointer;">Отправить</button>
    </div>
</div>
    
    <script>
        let currentState = 'awaiting_question';
        let userQuestion = '';
        
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
                email: userEmail  // ← ДОБАВЬТЕ ЭТУ СТРОКУ
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
                ⏰ Через ${data.expert.response_time} вы получите консультацию на почту.<br>
                Спасибо за обращение!
            `;
            addMessage(expertHtml);
            
            // Запускаем таймер на 15 минут (демо)
            addMessage('⏳ Запущен таймер ответа. Через 15 минут придёт уведомление!', false);
            startResponseTimer();
        } else {
            addMessage('❌ Извините, произошла ошибка. Пожалуйста, попробуйте позже.');
        }
    } catch (error) {
        addMessage('❌ Ошибка соединения. Проверьте интернет.');
    }
    
    currentState = 'completed';
}

// Добавьте эту функцию для таймера
function startResponseTimer() {
    setTimeout(() => {
        addMessage('📧 Уведомление! Эксперт отправил ответ на вашу почту.', false);
        addMessage('💡 Проверьте ваш email в течение 5-10 минут.', false);
    }, 15 * 60 * 1000); // 15 минут
}
                    `;
                    addMessage(expertHtml);
                } else {
                    addMessage('❌ Извините, произошла ошибка. Пожалуйста, попробуйте позже.');
                }
            } catch (error) {
                addMessage('❌ Ошибка соединения. Проверьте интернет.');
            }
            
            currentState = 'completed';
        }
        
        async function sendQuestion() {
            if (currentState !== 'awaiting_question') return;
            
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) {
                addMessage('⚠️ Пожалуйста, введите ваш вопрос.', false);
                return;
            }
            
            addMessage(question, true);
            userQuestion = question;
            
            addMessage('✅ Ваш вопрос принят! Теперь выберите вашу отрасль.', false);
            addIndustryButtons();
            
            currentState = 'awaiting_industry';
            input.value = '';
            input.disabled = true;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, industries=INDUSTRIES)

@app.route('/find_expert', methods=['POST'])
def find_expert():
    data = request.json
    industry = data.get('industry')
    question = data.get('question')
    email = data.get('email')
    
    suitable_experts = [e for e in EXPERTS if industry in e['specialization']]
    
    if suitable_experts:
        expert = random.choice(suitable_experts)
    else:
        expert = EXPERTS[0]
    
    return jsonify({
        'success': True,
        'expert': expert,
        'industry': industry,
        'question': question
    })

# Для хостинга на Render
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Запуск веб-чата...")
    print("📱 Откройте в браузере: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=port, debug=False)