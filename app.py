"""
================================================================================
CROBOT AI X - النسخة المتوافقة مع Vercel (بدون WebSocket)
================================================================================
- ثلاثي الأبعاد: Three.js + WebGPU + GLTF/DRACO
- الصوت: Web Speech API (STT) + ElevenLabs (TTS)
- الذكاء: OpenAI GPT + RAG + Function Calling + تحليل المشاعر
- الرؤية: GPT‑4 Vision
- النشر: Vercel (Flask Serverless)
================================================================================
"""

import os
import json
import base64
import datetime
import random
import requests
from flask import Flask, render_template_string, request, jsonify

# ---------- المتغيرات البيئية ----------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "YOUR_ELEVENLABS_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "YOUR_WEATHER_KEY")

# ---------- تهيئة Flask ----------
app = Flask(__name__)

# ---------- حالة الروبوت وذاكرته (RAG) ----------
robot_state = {
    "status": "idle",
    "last_response": "",
    "chat_memory": [],          # سياق المحادثة
    "emotion": "neutral",
}

# ============================================================================
# 1. أدوات (Tool Calling)
# ============================================================================
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_weather(city="Algiers"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        return f"درجة الحرارة في {city}: {data['main']['temp']}°C، {data['weather'][0]['description']}"
    except:
        return "لم أتمكن من جلب الطقس حالياً."

def convert_currency(amount=100, from_cur="USD", to_cur="EUR"):
    return f"{amount} {from_cur} = {amount * 0.85} {to_cur} (مثال)"

def control_music(action="play"):
    return f"تم {action} الموسيقى"

TOOLS = {
    "الوقت": get_current_time,
    "الطقس": get_weather,
    "تحويل العملة": convert_currency,
    "تشغيل موسيقى": lambda: control_music("play"),
    "إيقاف موسيقى": lambda: control_music("stop")
}

def execute_tool_command(text):
    text_lower = text.lower()
    if "الوقت" in text_lower or "الساعة" in text_lower:
        return get_current_time()
    if "طقس" in text_lower:
        city = "Algiers"
        for word in text.split():
            if word in ["الجزائر", "القاهرة", "الرياض", "دبي"]:
                city = word
                break
        return get_weather(city)
    if "تحويل" in text_lower and "عملة" in text_lower:
        return convert_currency()
    if "موسيقى" in text_lower:
        if "شغل" in text_lower or "تشغيل" in text_lower:
            return control_music("play")
        elif "أوقف" in text_lower or "إيقاف" in text_lower:
            return control_music("stop")
    return None

# ============================================================================
# 2. تحليل المشاعر
# ============================================================================
def detect_emotion(text):
    positive = ["حب", "فرح", "سعيد", "جميل", "رائع"]
    negative = ["حزين", "غاضب", "سيء", "مزعج"]
    if any(w in text for w in positive):
        return "happy"
    if any(w in text for w in negative):
        return "sad"
    if "?" in text:
        return "curious"
    return "neutral"

# ============================================================================
# 3. الذكاء الاصطناعي (LLM + RAG + Function Calling)
# ============================================================================
def get_llm_response(user_text, chat_history):
    try:
        messages = [{"role": "system", "content": "أنت مساعد ذكي اسمه آريا، تتحدث العربية، لديك شخصية ودودة وتساعد المستخدم."}]
        for entry in chat_history[-10:]:
            messages.append(entry)
        messages.append({"role": "user", "content": user_text})

        tool_result = execute_tool_command(user_text)
        if tool_result:
            return tool_result

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 200
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "عذراً، واجهت صعوبة في التفكير. هل يمكنك إعادة السؤال؟"
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

# ============================================================================
# 4. توليد الصوت (TTS) باستخدام ElevenLabs
# ============================================================================
def generate_tts_audio(text):
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        return None
    except:
        return None

# ============================================================================
# 5. معالجة الصور (Computer Vision)
# ============================================================================
def analyze_image(image_bytes):
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "صف ما تراه في هذه الصورة بالعربية."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 200
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return "لم أستطع تحليل الصورة."
    except Exception as e:
        return f"خطأ في تحليل الصورة: {str(e)}"

# ============================================================================
# 6. نقاط النهاية (API Routes)
# ============================================================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/speak', methods=['POST'])
def api_speak():
    data = request.get_json()
    user_text = data.get('text', '')
    if not user_text:
        return jsonify({"error": "نص فارغ"}), 400

    robot_state["status"] = "thinking"
    emotion = detect_emotion(user_text)
    robot_state["emotion"] = emotion

    reply = get_llm_response(user_text, robot_state["chat_memory"])

    robot_state["chat_memory"].append({"role": "user", "content": user_text})
    robot_state["chat_memory"].append({"role": "assistant", "content": reply})
    if len(robot_state["chat_memory"]) > 20:
        robot_state["chat_memory"] = robot_state["chat_memory"][-20:]

    robot_state["last_response"] = reply
    robot_state["status"] = "speaking"

    audio_b64 = generate_tts_audio(reply)

    return jsonify({
        "status": "success",
        "reply_text": reply,
        "audio_data": audio_b64,
        "emotion": emotion
    })

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "لا يوجد ملف"}), 400
    audio_file = request.files['file']
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        files = {"file": (audio_file.filename, audio_file, audio_file.mimetype)}
        data = {"model": "whisper-1", "language": "ar"}
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=20)
        result = response.json()
        return jsonify({"text": result.get("text", "")})
    except Exception as e:
        return jsonify({"text": "", "error": str(e)})

@app.route('/api/analyze-image', methods=['POST'])
def api_analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "لا توجد صورة"}), 400
    file = request.files['image']
    try:
        image_bytes = file.read()
        description = analyze_image(image_bytes)
        return jsonify({"description": description})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify(robot_state)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    robot_state["chat_memory"] = []
    robot_state["emotion"] = "neutral"
    robot_state["status"] = "idle"
    return jsonify({"status": "reset"})

# ============================================================================
# 7. واجهة المستخدم (HTML + Three.js + WebGPU) – بدون WebSocket
# ============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CROBOT AI X - المتطور</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0f1a; overflow: hidden; font-family: 'Segoe UI', sans-serif; color: #eee; }
        #canvas-container { width: 100vw; height: 100vh; display: block; }
        #ui-container {
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 750px;
            background: rgba(10, 15, 26, 0.8); backdrop-filter: blur(14px);
            border-radius: 28px; padding: 18px 22px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 60px rgba(0,0,0,0.9);
            z-index: 20;
        }
        .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        .row input {
            flex: 1; padding: 14px 20px; border: none; border-radius: 40px;
            background: rgba(255,255,255,0.07); color: #fff; font-size: 16px;
            outline: none; transition: 0.3s;
        }
        .row input:focus { background: rgba(255,255,255,0.14); box-shadow: 0 0 20px rgba(59,130,246,0.2); }
        .row input::placeholder { color: #64748b; }
        .btn {
            padding: 12px 22px; border: none; border-radius: 40px;
            background: #3b82f6; color: #fff; font-weight: bold;
            cursor: pointer; transition: 0.2s; display: inline-flex; align-items: center; gap: 6px;
            box-shadow: 0 4px 20px rgba(59,130,246,0.3);
        }
        .btn:hover { transform: scale(1.03); }
        .btn-secondary { background: #1e293b; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .btn-group { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; justify-content: center; }
        .btn-group .btn { flex: 1; min-width: 100px; justify-content: center; }
        #status { margin-top: 12px; font-size: 14px; color: #94a3b8; text-align: center; word-break: break-word; }
        .emotion-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-left: 6px; }
        .emotion-happy { background: #fbbf24; }
        .emotion-sad { background: #60a5fa; }
        .emotion-curious { background: #a78bfa; }
        .emotion-neutral { background: #94a3b8; }
        @media (max-width: 600px) {
            .row { flex-direction: column; }
            .btn-group { flex-direction: column; }
            .btn { width: 100%; justify-content: center; }
        }
        #loading-screen {
            position: fixed; inset: 0; background: #0a0f1a; display: flex;
            flex-direction: column; align-items: center; justify-content: center;
            z-index: 100; transition: opacity 0.8s;
        }
        #loading-screen.hidden { opacity: 0; pointer-events: none; }
        .spinner { width: 50px; height: 50px; border: 5px solid rgba(255,255,255,0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div id="loading-screen">
    <div class="spinner"></div>
    <p style="margin-top: 20px; font-size: 18px; color: #94a3b8;">جارٍ تحميل الروبوت المتطور...</p>
</div>

<div id="canvas-container"></div>

<div id="ui-container">
    <div class="row">
        <input type="text" id="commandInput" placeholder="اكتب أمراً للروبوت آريا..." />
        <button class="btn" onclick="sendText()">🗣️ تكلم</button>
    </div>
    <div class="btn-group">
        <button class="btn btn-secondary" onclick="startVoice()">🎤 استمع</button>
        <button class="btn btn-secondary" onclick="uploadImage()">🖼️ تحليل صورة</button>
        <button class="btn btn-secondary" onclick="resetChat()">🔄 إعادة</button>
    </div>
    <div id="status">
        <span id="statusText">مرحباً! أنا آريا، كيف يمكنني مساعدتك؟</span>
        <span class="emotion-indicator emotion-neutral" id="emotionDot"></span>
    </div>
</div>

<!-- Three.js مع WebGPU -->
<script type="importmap">
{
    "imports": {
        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
    }
}
</script>

<script type="module">
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
    import { WebGPURenderer } from 'three/addons/renderers/WebGPURenderer.js';

    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1a);

    const camera = new THREE.PerspectiveCamera(30, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 1.6, 4.5);
    camera.lookAt(0, 1.2, 0);

    let renderer;
    if (navigator.gpu) {
        try {
            renderer = new WebGPURenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            console.log('✅ WebGPU Renderer');
        } catch(e) {
            renderer = new THREE.WebGLRenderer({ antialias: true });
            console.log('⚠️ WebGPU غير مدعوم، نستخدم WebGL');
        }
    } else {
        renderer = new THREE.WebGLRenderer({ antialias: true });
        console.log('⚠️ WebGPU غير متاح، WebGL');
    }
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // إضاءة متطورة
    const ambient = new THREE.AmbientLight(0x404060, 0.5);
    scene.add(ambient);
    const main = new THREE.DirectionalLight(0xffeedd, 2.5);
    main.position.set(4, 6, 5);
    main.castShadow = true;
    scene.add(main);
    const fill = new THREE.DirectionalLight(0x88bbff, 0.8);
    fill.position.set(-3, 2, 3);
    scene.add(fill);
    const rim = new THREE.DirectionalLight(0x4488ff, 1.2);
    rim.position.set(-2, 1, -5);
    scene.add(rim);
    const back = new THREE.DirectionalLight(0x2255aa, 0.6);
    back.position.set(0, 2, -6);
    scene.add(back);

    // أرضية
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x0a0f1a, roughness: 0.7, metalness: 0.1 });
    const floor = new THREE.Mesh(new THREE.CircleGeometry(2.5, 32), floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.05;
    floor.receiveShadow = true;
    scene.add(floor);

    // تحميل النموذج
    const loader = new GLTFLoader();
    const draco = new DRACOLoader();
    draco.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.4.1/');
    loader.setDRACOLoader(draco);

    let robot, head, leftEye, rightEye, jaw, mouthMorphs = [];
    let eyeTarget = new THREE.Vector3(0, 0, 0);
    let isSpeaking = false;
    let speechStart = 0;

    loader.load(
        'https://threejs.org/examples/models/gltf/RobotExpressive/RobotExpressive.glb',
        (gltf) => {
            robot = gltf.scene;
            robot.scale.set(0.3, 0.3, 0.3);
            robot.position.set(0, 0.4, 0);
            robot.traverse((child) => {
                if (child.isMesh) {
                    child.material = new THREE.MeshPhysicalMaterial({
                        color: 0xf0f4ff,
                        roughness: 0.3,
                        metalness: 0.7,
                        clearcoat: 0.1,
                    });
                    if (child.name.includes('Head')) head = child;
                    if (child.name.includes('EyeLeft')) leftEye = child;
                    if (child.name.includes('EyeRight')) rightEye = child;
                    if (child.name.includes('Jaw')) jaw = child;
                    if (child.name.includes('Mouth')) mouthMorphs.push(child);
                }
            });
            scene.add(robot);
            document.getElementById('loading-screen').classList.add('hidden');
        },
        undefined,
        (err) => {
            console.error(err);
            document.getElementById('loading-screen').innerHTML = '<p style="color:red;">فشل تحميل النموذج</p>';
        }
    );

    // تتبع العينين
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth) * 2 - 1;
        const y = -(e.clientY / window.innerHeight) * 2 + 1;
        eyeTarget.set(x * 0.3, y * 0.2 + 0.1, 0.5);
    });

    let blinkTimer = 0;
    let isBlinking = false;

    function updateLipSync(time) {
        if (!jaw) return;
        if (isSpeaking) {
            const elapsed = (Date.now() - speechStart) / 1000;
            const val = 0.4 + 0.4 * Math.sin(elapsed * 18) * Math.sin(elapsed * 7 + 1);
            jaw.position.y = -0.08 + val * 0.06;
            mouthMorphs.forEach(m => {
                if (m.morphTargetInfluences) {
                    m.morphTargetInfluences[0] = val * 0.8;
                }
            });
        } else {
            jaw.position.y = -0.08;
            mouthMorphs.forEach(m => {
                if (m.morphTargetInfluences) m.morphTargetInfluences[0] = 0;
            });
        }
    }

    function animate(time) {
        requestAnimationFrame(animate);
        if (leftEye && rightEye) {
            const lookTarget = eyeTarget.clone();
            leftEye.lookAt(lookTarget);
            rightEye.lookAt(lookTarget);
        }
        blinkTimer += 0.02;
        if (blinkTimer > 1.5 + Math.random() * 3) {
            isBlinking = true;
            blinkTimer = 0;
        }
        if (isBlinking) {
            blinkTimer += 0.1;
            const scale = Math.max(0, 1 - blinkTimer * 2);
            if (leftEye) leftEye.scale.y = scale;
            if (rightEye) rightEye.scale.y = scale;
            if (blinkTimer >= 1) {
                isBlinking = false;
                blinkTimer = 0;
                if (leftEye) leftEye.scale.y = 1;
                if (rightEye) rightEye.scale.y = 1;
            }
        }
        if (head) {
            const timeSec = time / 1000;
            head.rotation.z = 0.02 * Math.sin(timeSec * 0.5);
            head.rotation.x = 0.01 * Math.sin(timeSec * 0.3 + 1);
        }
        updateLipSync(time);
        renderer.render(scene, camera);
    }
    animate(0);

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    window.startSpeaking = () => { isSpeaking = true; speechStart = Date.now(); };
    window.stopSpeaking = () => { isSpeaking = false; };
    window.setEmotion = (emotion) => {
        const colorMap = { happy: 0xffdd44, sad: 0x4488ff, curious: 0xaa88ff, neutral: 0xffffff };
        const c = colorMap[emotion] || 0xffffff;
        main.color.setHex(c);
    };
    console.log('✅ Three.js + WebGPU جاهز');
</script>

<script>
    // ---------- عناصر الواجهة ----------
    const input = document.getElementById('commandInput');
    const statusText = document.getElementById('statusText');
    const emotionDot = document.getElementById('emotionDot');

    function updateStatus(msg, emotion = 'neutral') {
        statusText.textContent = msg;
        emotionDot.className = 'emotion-indicator emotion-' + emotion;
        window.setEmotion && window.setEmotion(emotion);
    }

    // ---------- إرسال النص عبر REST API ----------
    async function sendText() {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        updateStatus('🤔 يفكر...', 'neutral');
        try {
            const res = await fetch('/api/speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            if (data.reply_text) {
                displayReply(data.reply_text, data.emotion);
                if (data.audio_data) playAudioBase64(data.audio_data);
                else speakText(data.reply_text);
            } else {
                updateStatus('⚠️ لم أستجب', 'neutral');
            }
        } catch(e) {
            updateStatus('⚠️ خطأ في الاتصال', 'neutral');
        }
    }

    function displayReply(text, emotion = 'neutral') {
        updateStatus('🤖 ' + text, emotion);
        window.startSpeaking && window.startSpeaking();
        // سيتم إيقاف حركة الشفاه عند انتهاء الصوت عبر onended
    }

    // ---------- تشغيل الصوت ----------
    function playAudioBase64(b64) {
        const audio = new Audio('data:audio/mp3;base64,' + b64);
        audio.onplay = () => { window.startSpeaking && window.startSpeaking(); };
        audio.onended = () => { window.stopSpeaking && window.stopSpeaking(); updateStatus('في انتظارك...', 'neutral'); };
        audio.play().catch(() => speakText(''));
    }

    function speakText(text) {
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ar-SA';
        utterance.rate = 0.9;
        utterance.pitch = 1.1;
        utterance.onstart = () => { window.startSpeaking && window.startSpeaking(); };
        utterance.onend = () => { window.stopSpeaking && window.stopSpeaking(); updateStatus('في انتظارك...', 'neutral'); };
        window.speechSynthesis.speak(utterance);
    }

    // ---------- الاستماع الصوتي (Web Speech API) ----------
    function startVoice() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('متصفحك لا يدعم الاستماع');
            return;
        }
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new Recognition();
        rec.lang = 'ar-SA';
        rec.interimResults = false;
        rec.maxAlternatives = 1;
        updateStatus('🎤 استمع... تحدث الآن', 'curious');
        rec.onresult = (e) => {
            const last = e.results.length - 1;
            const transcript = e.results[last][0].transcript;
            input.value = transcript;
            updateStatus('👂 سمعت: "' + transcript + '"', 'neutral');
            sendText();
        };
        rec.onspeechend = () => rec.stop();
        rec.onerror = () => updateStatus('❌ لم أستمع، حاول مجدداً', 'neutral');
        rec.start();
    }

    // ---------- تحميل صورة وتحليلها ----------
    function uploadImage() {
        const inputFile = document.createElement('input');
        inputFile.type = 'file';
        inputFile.accept = 'image/*';
        inputFile.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const formData = new FormData();
            formData.append('image', file);
            updateStatus('📸 جارٍ تحليل الصورة...', 'curious');
            try {
                const res = await fetch('/api/analyze-image', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.description) {
                    displayReply(data.description, 'neutral');
                    speakText(data.description);
                } else {
                    updateStatus('⚠️ لم أستطع تحليل الصورة', 'neutral');
                }
            } catch(err) {
                updateStatus('⚠️ خطأ في الاتصال', 'neutral');
            }
        };
        inputFile.click();
    }

    // ---------- إعادة ضبط ----------
    function resetChat() {
        fetch('/api/reset', { method: 'POST' });
        window.speechSynthesis && window.speechSynthesis.cancel();
        window.stopSpeaking && window.stopSpeaking();
        input.value = '';
        updateStatus('🔄 تمت إعادة التعيين', 'neutral');
    }

    // ربط الوظائف بالـ window
    window.sendText = sendText;
    window.startVoice = startVoice;
    window.uploadImage = uploadImage;
    window.resetChat = resetChat;

    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendText(); });
    console.log('✅ واجهة المستخدم جاهزة');
</script>

</body>
</html>
"""

# ============================================================================
# 8. تشغيل التطبيق (محلياً على المنفذ 7000)
# ============================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
