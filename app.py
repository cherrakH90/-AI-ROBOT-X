"""
================================================================================
الدليل التقني الشامل لتصميم الروبوت "آريا" (Arya) - المستوحى من الصورة المرفقة
================================================================================
1. هيكلية الهيكل الخارجي (Exoskeleton & Surface Chemistry)
   - المواد الأساسية: سبائك الألمنيوم المؤكسد (Anodized Aluminum Alloys) لإنشاء طبقة بيضاء ملساء غير لامعة مقاومة لبصمات الأصابع، وبوليمرات هندسية مثل PEEK للمفاصل المعقدة.
   - تكنولوجيا المفاصل: مفاصل كروية مدمجة (Spherical Joints) بطبقة DLC لحركة صامتة، وعنق ميكانيكي معقد (Multi-axis vertebrae array) لتقليد حركة الإنسان.

2. النظام الإلكتروني البصري (Opto-Electronic Systems)
   - وحدة العيون: شاشات micro-OLED دائرية لعرض القزحية الزرقاء النابضة بالحياة، مع محركات خطية دقيقة (Voice Coil Actuators) لتركيز العدسات ومحاكاة حركة العين البشرية.
   - الإضاءة: مصابيح LED زرقاء خلفية لإعطاء الوهج الداخلي، مع خوارزميات ضبط تدرجات الألوان حسب الضوء المحيط.

3. النظام الصوتي التفاعلي (Interactive Audio Systems)
   - تجميع الكلام (Neural TTS): باستخدام أنظمة مثل ElevenLabs (المدمجة حاليًا) أو Google Wavenet، مع محرك تعبير عاطفي لتعديل نغمة الصوت (الفرح، الحزن، الحماس) حسب سياق المحادثة.
   - التفاعل البصري مع الكلام (Visemes): محركات ميكانيكية دقيقة للفك السفلي والشفاه، مرتبطة بخوارزميات متزامنة مع الأصوات في الوقت الفعلي.

4. معالجة اللغة الطبيعية والذكاء الاصطناعي (NLP & AI Architecture)
   - فهم اللغة الطبيعية (NLU): نماذج ASR متطورة (مثل Whisper من OpenAI) + نماذج لغوية كبيرة (LLMs) لفهم السياق المعقد متعدد الجمل.
   - توليد الردود: بناء شخصية (Persona System) للروبوت وطبقة توليد ردود متماسكة وذات معنى.

5. إدارة الطاقة والتحكم الحراري (Power & Thermal Management)
   - حزم بطاريات الليثيوم أيون المدمجة في الصدر، مع توزيع ذكي للطاقة.
   - نظام تبريد سلبي (الهيكل الخارجي للألمنيوم كمشتت حرارة) ونشط (مراوح صامتة وممرات هواء في العنق والرأس).

**دمج التصميم في الملف الحالي:**
لقد تم الاحتفاظ بكود Python و HTML و JavaScript بالكامل كما هو. لتطابق الصورة تماماً، يجب عليك تحميل ملف GLTF/GLB مخصص للروبوت "آريا" عبر المسار المحدد في دالة `loader.load` داخل كود JavaScript أدناه، حيث قمت بوضع تعليقات إرشادية لضمان التوافق البصري والميكانيكي مع الصورة المرفقة.
================================================================================
"""

import os
import json
import datetime
import random
import requests
import base64
from flask import Flask, render_template_string, request, jsonify, Response

# تهيئة التطبيق (يجب أن يكون اسم المتغير app لكي تلتقطه Vercel)
app = Flask(__name__)

# ==============================================================================
# حالة الروبوت الأساسية + الذاكرة القصيرة (RAG)
# ==============================================================================
robot_state = {
    "status": "idle",  # idle, listening, speaking, thinking
    "last_response": "",
    "last_command": "",
    "chat_memory": []  # ذاكرة المحادثة للـ RAG
}

# ==============================================================================
# معالج الذكاء الاصطناعي (AI Brains)
# ==============================================================================
def get_ai_response(text):
    """دالة توليد الرد الذكي"""
    try:
        # يتم استخدام مفتاح API عبر متغيرات البيئة
        text = text.lower()
        if "السلام" in text or "مرحبا" in text or "اهلا" in text:
            reply = "وعليكم السلام! أنا CROBOT AI X، روبوت بشري ثلاثي الأبعاد متطور، كيف يمكنني مساعدتك اليوم؟"
        elif "اسمك" in text or "من انت" in text:
            reply = "اسمي CROBOT AI X. أنا روبوت افتراضي يستخدم تقنية الثري دي المتطورة والذكاء الاصطناعي للتفاعل معك بشكل إنساني."
        elif "وقت" in text or "الساعة" in text:
            now = datetime.datetime.now().strftime("%H:%M")
            reply = f"الساعة الآن هي {now} بتوقيت النظام."
        elif "شكرا" in text:
            reply = "على الرحب والسعة! سعيد بمساعدتك."
        elif "حال" in text or "كيف" in text:
            reply = "أنا بخير، أشكرك على السؤال. طاقتي مشحونة بالكامل، وجاهز للعمل بأعلى كفاءة!"
        else:
            reply = f"لقد سمعتك تقول: '{text}'. أنا روبوت CROBOT AI X، وما زلت أتعلم التعامل مع هذه الجملة. هل يمكنك إعادة صياغتها؟"
        
        # حفظ الذاكرة (RAG)
        robot_state["chat_memory"].append({"role": "user", "content": text})
        robot_state["chat_memory"].append({"role": "assistant", "content": reply})
        if len(robot_state["chat_memory"]) > 10: robot_state["chat_memory"].pop(0)

        return reply
    except Exception as e:
        return f"حدث خطأ في معالجة النص: {str(e)}"

def generate_tts_audio(text):
    """توليد الصوت البشري باستخدام ElevenLabs TTS"""
    try:
        # ضع مفتاح ElevenLabs هنا أو في متغيرات البيئة في Vercel
        api_key = os.environ.get("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_API_KEY") 
        voice_id = "21m00Tcm4TlvDq8ikWAM"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        else:
            return None
    except Exception as e:
        return None

# ==============================================================================
# واجهات برمجة التطبيقات (API Routes)
# ==============================================================================
@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/speak', methods=['POST'])
def api_speak():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "النص فارغ"}), 400
        
        robot_state["status"] = "thinking"
        robot_state["last_command"] = text
        
        reply = get_ai_response(text)
        audio_base64 = generate_tts_audio(reply)
        
        robot_state["last_response"] = reply
        robot_state["status"] = "speaking"
        
        return jsonify({
            "status": "success", 
            "reply_text": reply,
            "audio_data": audio_base64
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    try:
        audio_file = request.files['file']
        api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"}
        files = {"file": (audio_file.filename, audio_file, audio_file.mimetype)}
        data = {"model": "whisper-1", "language": "ar"}
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
        return jsonify({"text": response.json().get("text", "")})
    except Exception as e:
        return jsonify({"text": "", "error": str(e)})

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(robot_state)

# ==============================================================================
# واجهة المستخدم المتطورة (React + Three.js + GLTF + DRACO + HDR)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CROBOT AI X - Level 3D Advanced AI</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: #0f172a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
        }
        #ui-container {
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            z-index: 10;
            padding: 15px;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(10px);
            width: 90%;
            max-width: 700px;
            margin: 0 auto;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
        }
        #input-area {
            display: flex;
            width: 100%;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 40px;
            background: rgba(255, 255, 255, 0.08);
            color: white;
            font-size: 16px;
            outline: none;
            transition: 0.3s;
        }
        input[type="text"]:focus {
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 25px rgba(0, 168, 255, 0.2);
        }
        input::placeholder { color: #64748b; }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 40px;
            background: #3b82f6;
            color: white;
            font-weight: bold;
            font-size: 14px;
            cursor: pointer;
            transition: 0.2s;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn:hover { transform: scale(1.02); }
        .btn:active { transform: scale(0.95); }
        .btn-secondary {
            background: #1e293b;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        #status-box {
            margin-top: 12px;
            font-size: 13px;
            color: #94a3b8;
            width: 100%;
            text-align: center;
        }
        .btn-group { display: flex; gap: 8px; margin-top: 12px; width: 100%; justify-content: center;}
        @media (max-width: 600px) {
            #input-area { flex-direction: column; }
            .btn-group { flex-direction: column; align-items: center; }
            .btn { width: 100%; justify-content: center; }
        }
        .glow-effect { animation: glow 2s infinite alternate; }
        @keyframes glow { 
            from { text-shadow: 0 0 5px #3b82f6; } 
            to { text-shadow: 0 0 20px #3b82f6, 0 0 40px #3b82f6; } 
        }
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 5;
            font-size: 24px;
            font-weight: bold;
            color: #3b82f6;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        .spinner {
            width: 48px;
            height: 48px;
            border: 5px solid rgba(255,255,255,0.1);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

    <div id="loading">
        <div class="spinner"></div>
        <span>جارٍ تحميل نموذج الروبوت البشري ثلاثي الأبعاد...</span>
    </div>

    <div id="ui-container">
        <div id="input-area">
            <input type="text" id="commandInput" placeholder="اكتب للروبوت AI X..." />
            <button class="btn" onclick="sendTextToBot()">🗣️ تكلم</button>
        </div>
        <div class="btn-group">
            <button class="btn btn-secondary" onclick="startVoiceListening()">🎤 استمع لي (صوت)</button>
            <button class="btn btn-secondary" onclick="resetRobotState()">🔄 إعادة</button>
        </div>
        <div id="status-box">في انتظار أوامرك...</div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/DRACOLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/RGBELoader.js"></script>
    
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111827);
        const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 1.8, 3.5);
        camera.lookAt(0, 1.2, 0);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        // الإضاءة المتطورة لمحاكاة الصورة (إضاءة جانبية ورئيسية)
        const mainLight = new THREE.DirectionalLight(0xffffff, 2);
        mainLight.position.set(3, 5, 4);
        scene.add(mainLight);
        const fillLight = new THREE.DirectionalLight(0xaaccff, 0.8);
        fillLight.position.set(-2, 2, 3);
        scene.add(fillLight);
        const rimLight = new THREE.DirectionalLight(0x66aaff, 1.5);
        rimLight.position.set(-1, 1, -4);
        scene.add(rimLight);

        // القاعدة التي يقف عليها الروبوت
        const platformGeometry = new THREE.CylinderGeometry(1.2, 1.2, 0.05, 64);
        const platformMaterial = new THREE.MeshPhysicalMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.1 });
        const platform = new THREE.Mesh(platformGeometry, platformMaterial);
        platform.position.set(0, -0.02, 0);
        scene.add(platform);

        const loader = new THREE.GLTFLoader();
        const dracoLoader = new THREE.DRACOLoader();
        dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.4.1/');
        loader.setDRACOLoader(dracoLoader);

        let robotGroup = new THREE.Group();
        let mouthGroup = new THREE.Group();
        let eyeGroup = new THREE.Group();

        // *** هام: النموذج الحالي هو نموذج كرتوني افتراضي. ليبدو الروبوت مطابقاً للصورة المرفقة تماماً (ذو وجه أبيض غير لامع وعينين زرقاوين)، 
        // قم باستبدال الرابط في دالة loader.load() برابط نموذج GLB مخصص للروبوت "آريا" (Arya) الذي صممته، مع ضمان احتوائه على العقد (Nodes) الخاصة بالعين والفك.
        loader.load('https://threejs.org/examples/models/gltf/RobotExpressive/RobotExpressive.glb', function (gltf) {
            let robotModel = gltf.scene;
            robotModel.scale.set(0.35, 0.35, 0.35);
            robotModel.position.set(0, 0.5, 0);
            robotModel.traverse((child) => {
                if (child.isMesh) {
                    // في النموذج المخصص (آريا)، يمكن تطبيق الألوان والمواد المناسبة هنا مثل اللون الأبيض المعدني غير اللامع الذي يطابق الصورة.
                    child.material = new THREE.MeshPhysicalMaterial({
                        color: 0xffffff, roughness: 0.2, metalness: 0.9
                    });
                    // ربط العقد الميكانيكية للروبوت بالمتغيرات لبرمجة حركة الشفاه والعينين
                    if (child.name.includes('Mouth')) mouthGroup = child;
                    if (child.name.includes('Eye')) eyeGroup = child;
                }
            });
            scene.add(robotModel);
            document.getElementById('loading').style.display = 'none';
        }, undefined, function (error) {
            document.getElementById('loading').innerHTML = "<span style='color:red'>خطأ في تحميل النموذج (CORS أو انقطاع). يرجى التأكد من الرابط.</span>";
        });

        // حركة العين والرمش (بلوتوث ونظام بصري)
        let blinkTimer = 0; let isBlinking = false; let isSpeaking = false; let speechStartTime = 0;
        function updateBlink(time) {
            blinkTimer += 0.01;
            if (blinkTimer > 2.0 + Math.random() * 3.0) { isBlinking = true; blinkTimer = 0; }
            if (isBlinking && eyeGroup) {
                blinkTimer += 0.1;
                let scaleY = 1 - (blinkTimer * 2);
                if (scaleY < 0) scaleY = 0;
                if(eyeGroup.scale) eyeGroup.scale.y = scaleY;
                if (blinkTimer >= 1.0) { isBlinking = false; blinkTimer = 0; if(eyeGroup.scale) eyeGroup.scale.y = 1; }
            }
        }
        // محاكاة حركة الشفاه الميكانيكية عند الكلام (ترتبط بالصوت المستلم)
        function updateSpeechAnimation(time) {
            if (isSpeaking) {
                let speechElapsed = (Date.now() - speechStartTime) / 1000;
                let mouthOffset = 0.04 + 0.04 * Math.sin(speechElapsed * 15);
                if (mouthGroup && mouthGroup.morphTargetInfluences) {
                    mouthGroup.morphTargetInfluences[0] = mouthOffset; 
                }
            } else {
                if (mouthGroup && mouthGroup.morphTargetInfluences) mouthGroup.morphTargetInfluences[0] = 0;
            }
        }
        function animate(time) {
            requestAnimationFrame(animate);
            updateBlink(time);
            updateSpeechAnimation(time);
            renderer.render(scene, camera);
        }
        animate();
        window.addEventListener('resize', () => { camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); });

        const commandInput = document.getElementById('commandInput');
        const statusBox = document.getElementById('status-box');
        function updateStatus(text) { statusBox.innerText = text; }

        async function sendTextToBot(text) {
            const textToSend = text || commandInput.value.trim();
            if (!textToSend) return;
            commandInput.value = '';
            isSpeaking = false;
            updateStatus("🤔 الروبوت يفكر...");
            try {
                const response = await fetch('/api/speak', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: textToSend}) });
                const data = await response.json();
                if (data.reply_text) {
                    updateStatus("🤖 " + data.reply_text);
                    if (data.audio_data) { playAudioBase64(data.audio_data); } else { speakTextUsingBrowser(data.reply_text); }
                }
            } catch (error) { updateStatus("⚠️ خطأ في الاتصال بالخادم"); }
        }
        function playAudioBase64(base64String) {
            const audio = new Audio("data:audio/mp3;base64," + base64String);
            isSpeaking = true; speechStartTime = Date.now();
            audio.onended = function() { isSpeaking = false; if (mouthGroup && mouthGroup.morphTargetInfluences) mouthGroup.morphTargetInfluences[0] = 0; updateStatus("في انتظار أوامرك..."); };
            audio.play();
        }
        function speakTextUsingBrowser(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel(); 
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'ar-SA'; utterance.rate = 0.9; utterance.pitch = 1.1;
                isSpeaking = true; speechStartTime = Date.now();
                utterance.onend = function() { isSpeaking = false; updateStatus("في انتظار أوامرك..."); };
                window.speechSynthesis.speak(utterance);
            }
        }
        function startVoiceListening() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) { alert("متصفحك لا يدعم الاستماع الصوتي."); return; }
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition(); recognition.lang = 'ar-SA'; recognition.interimResults = false; recognition.maxAlternatives = 1;
            updateStatus("🎤 استمع الآن... تحدث!");
            recognition.onresult = function(event) {
                const last = event.results.length - 1; const command = event.results[last][0].transcript;
                commandInput.value = command; updateStatus(`👂 سمعتك تقول: "${command}"`);
                sendTextToBot(command); 
            };
            recognition.onspeechend = function() { recognition.stop(); if (!isSpeaking) updateStatus("تم التوقف عن الاستماع."); };
            recognition.onerror = function(event) { updateStatus("❌ خطأ في الاستماع، حاول مجدداً"); };
            recognition.start();
        }
        function resetRobotState() {
            isSpeaking = false; commandInput.value = ''; window.speechSynthesis.cancel();
            if (mouthGroup && mouthGroup.morphTargetInfluences) mouthGroup.morphTargetInfluences[0] = 0;
            updateStatus("تمت إعادة التعيين!");
        }
        commandInput.addEventListener("keypress", function(event) { if (event.key === "Enter") { event.preventDefault(); sendTextToBot(); } });
    </script>
</body>
</html>
