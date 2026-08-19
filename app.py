import os
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# واجهة مستخدم تعتمد على خلفية فيديو سينمائي متفاعل
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI ROBOT X</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        body {
            background-color: #000;
            color: #ffffff;
            overflow: hidden;
            height: 100vh;
            width: 100vw;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* خلفية الفيديو السينمائي متصل بالموقع */
        .video-background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
            filter: brightness(0.85) contrast(1.1);
            transition: filter 0.8s ease;
        }

        /* طبقة الأكواد والماتريكس نيون النوافي الجانبية */
        .hud-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            pointer-events: none;
            display: flex;
            justify-content: space-between;
            padding: 25px;
            font-family: monospace;
            font-size: 11px;
            color: var(--neon-color, #ff0055);
            text-shadow: 0 0 8px var(--neon-color, #ff0055);
            transition: color 0.5s ease;
            background: radial-gradient(circle, transparent 40%, rgba(0,0,0,0.7) 100%);
        }

        .hud-column {
            width: 220px;
            opacity: 0.85;
            line-height: 1.6;
        }

        /* لوحة التحكم الزجاجية الشفافة Glassmorphism */
        .ui-panel {
            position: absolute;
            bottom: 30px;
            z-index: 3;
            width: 90%;
            max-width: 480px;
            background: rgba(10, 10, 20, 0.45);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 22px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9), 0 0 20px var(--shadow-color, rgba(255, 0, 85, 0.4));
            transition: all 0.5s ease;
            text-align: center;
        }

        .brand-title {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 3px;
            margin-bottom: 10px;
            color: #ffffff;
            text-shadow: 0 0 12px var(--neon-color, #ff0055);
        }

        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--neon-color, #ff0055);
            color: var(--neon-color, #ff0055);
            margin-bottom: 18px;
            letter-spacing: 1px;
            transition: all 0.5s ease;
        }

        .chat-response {
            min-height: 40px;
            max-height: 100px;
            overflow-y: auto;
            font-size: 14px;
            color: #e2e8f0;
            margin-bottom: 15px;
            padding: 8px;
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            display: none;
        }

        .input-group {
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 14px 18px;
            color: #fff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: var(--neon-color, #ff0055);
        }

        button {
            background: var(--neon-color, #ff0055);
            border: none;
            border-radius: 12px;
            padding: 14px 22px;
            color: #fff;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 12px var(--neon-color, #ff0055);
            transition: all 0.3s ease;
        }

        button:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>

    <!-- فيديو خلفية الروبوت المتفاعل -->
    <video class="video-background" id="bg-video" autoplay loop muted playsinline>
        <source src="https://assets.mixkit.co/videos/preview/mixkit-cyberpunk-robot-head-animation-41551-large.mp4" type="video/mp4">
    </video>

    <!-- واجهة الأكواد السايبرانية HUD -->
    <div class="hud-overlay" id="hud">
        <div class="hud-column">
            [AI_ROBOT_X_SYSTEM]<br>
            > NEURAL_CORE: ONLINE<br>
            > CYBERNETIC_INTERFACE: ACTIVE<br>
            > MATRIX_STATUS: RED_NEON<br>
            > VISUAL_RENDER: 4K_REALTIME
        </div>
        <div class="hud-column" style="text-align: left;">
            0x88F011B<br>
            0x00A12C4<br>
            LATENCY: 8ms<br>
            FPS: 60.0<br>
            AUDIO_SYNC: READY
        </div>
    </div>

    <!-- لوحة التحكم السفلى -->
    <div class="ui-panel">
        <div class="brand-title">AI ROBOT X</div>
        <div class="status-badge" id="status-badge">حالة النظام: معالجة البيانات (Cyber Pink)</div>
        <div class="chat-response" id="response-box"></div>
        <div class="input-group">
            <input type="text" id="user-input" placeholder="تحدث مع AI ROBOT X..." onkeypress="if(event.key==='Enter') processInput()">
            <button onclick="processInput()">إرسال</button>
        </div>
    </div>

    <script>
        const PINK_STATE = { css: '#ff0055', text: 'حالة النظام: معالجة البيانات (Cyber Pink)' };
        const BLUE_STATE = { css: '#00f0ff', text: 'حالة النظام: متصل وفي وضع الاستجابة (Neon Blue)' };

        function updateState(newState) {
            document.documentElement.style.setProperty('--neon-color', newState.css);
            document.documentElement.style.setProperty('--shadow-color', newState.css);
            document.getElementById('status-badge').innerText = newState.text;
        }

        function processInput() {
            const input = document.getElementById('user-input');
            const responseBox = document.getElementById('response-box');
            const userText = input.value.trim();
            
            if(!userText) return;

            // التحول التلقائي إلى الأزرق النيون عند الإجابة
            updateState(BLUE_STATE);
            
            responseBox.style.display = "block";
            responseBox.innerText = "أهلاً بك! أنا AI ROBOT X. جارٍ تحليل طلبك وإعداده...";
            
            input.value = "";

            // العودة التلقائية للوردي/الأحمر النيون بعد انتهاء التحدث
            setTimeout(() => {
                updateState(PINK_STATE);
            }, 3500);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
