import os
import signal
import sys
from flask import Flask, render_template_string, jsonify, request

# إنهاء أي خادم قديم يعمل بنفس البيئة
try:
    if os.name != 'nt':
        os.system("pkill -f 'python.*app.py'")
except Exception:
    pass

app = Flask(__name__)

# تصميم الواجهة المستقبلية لتطبيق AI ROBOT X
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI ROBOT X</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: #030308;
            color: #ffffff;
            overflow: hidden;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        #canvas-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }
        /* HUD Code Overlay */
        .hud-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            pointer-events: none;
            background: linear-gradient(180deg, rgba(255,0,85,0.05) 0%, rgba(0,240,255,0.05) 100%);
            display: flex;
            justify-content: space-between;
            padding: 20px;
            font-family: monospace;
            font-size: 11px;
            color: var(--neon-color, #ff0055);
            text-shadow: 0 0 5px var(--neon-color, #ff0055);
            transition: color 0.5s ease;
        }
        .hud-column {
            width: 200px;
            opacity: 0.7;
            overflow: hidden;
            white-space: pre-wrap;
        }
        /* Main UI Card Glassmorphism */
        .ui-panel {
            position: absolute;
            bottom: 40px;
            z-index: 3;
            width: 90%;
            max-width: 450px;
            background: rgba(10, 10, 20, 0.55);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8), 0 0 15px var(--shadow-color, rgba(255, 0, 85, 0.3));
            transition: box-shadow 0.5s ease;
            text-align: center;
        }
        .brand-title {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 15px;
            color: #ffffff;
            text-shadow: 0 0 10px var(--neon-color, #ff0055);
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--neon-color, #ff0055);
            color: var(--neon-color, #ff0055);
            margin-bottom: 15px;
            transition: all 0.5s ease;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 12px 15px;
            color: #fff;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: var(--neon-color, #ff0055);
        }
        button {
            background: var(--neon-color, #ff0055);
            border: none;
            border-radius: 10px;
            padding: 12px 20px;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 0 10px var(--neon-color, #ff0055);
            transition: all 0.3s ease;
        }
        button:hover {
            opacity: 0.9;
            transform: scale(1.02);
        }
    </style>
</head>
<body>

    <div id="canvas-container"></div>

    <div class="hud-overlay" id="hud">
        <div class="hud-column" id="hud-left">
            [SYS_INIT_AI_ROBOT_X]<br>
            > LOADING CORE MODULES...<br>
            > CYBERNETIC AVATAR: ONLINE<br>
            > NEURAL MESH: ACTIVE<br>
            > NEON MATRIX: STABLE
        </div>
        <div class="hud-column" id="hud-right">
            0x4F9A2B10<br>
            0x00FF00FA<br>
            SYSTEM_STATUS: OK<br>
            FPS: 60<br>
            LATENCY: 12ms
        </div>
    </div>

    <div class="ui-panel" id="ui-panel">
        <div class="brand-title">AI ROBOT X</div>
        <div class="status-badge" id="status-badge">حالة المعالجة: جاري التفكير (Cyber Pink)</div>
        <div class="input-group">
            <input type="text" id="user-input" placeholder="اكتب أمرك للروبوت..." onkeypress="if(event.key==='Enter') processInput()">
            <button onclick="processInput()">إرسال</button>
        </div>
    </div>

    <script>
        // إعداد متغيرات الألوان المستقبلية (الأحمر/الوردي عند التفكير - الأزرق النيون عند التحدث)
        const PINK_STATE = { hex: 0xff0055, css: '#ff0055', text: 'حالة المعالجة: جاري التفكير (Cyber Pink)' };
        const BLUE_STATE = { hex: 0x00f0ff, css: '#00f0ff', text: 'حالة الاستجابة: متصل بالذكاء (Neon Blue)' };

        let currentState = PINK_STATE;

        // إعداد Three.js
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // إنشاء هيكل الروبوت السايبراني (3D Head Model Placeholder)
        const robotGroup = new THREE.Group();
        
        // الرأس
        const headGeo = new THREE.SphereGeometry(1.2, 32, 32);
        headGeo.scale(1, 1.2, 1);
        const headMat = new THREE.MeshStandardMaterial({
            color: 0x111122,
            metalness: 0.9,
            roughness: 0.2,
            wireframe: false
        });
        const head = new THREE.Mesh(headGeo, headMat);
        robotGroup.add(head);

        // العيون النيون
        const eyeGeo = new THREE.SphereGeometry(0.2, 16, 16);
        const eyeMat = new THREE.MeshBasicMaterial({ color: currentState.hex });
        
        const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
        leftEye.position.set(-0.4, 0.2, 1);
        robotGroup.add(leftEye);

        const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
        rightEye.position.set(0.4, 0.2, 1);
        robotGroup.add(rightEye);

        // خوذة نيون شفافة
        const visorGeo = new THREE.CylinderGeometry(1.25, 1.25, 0.6, 32);
        const visorMat = new THREE.MeshPhysicalMaterial({
            color: currentState.hex,
            transparent: true,
            opacity: 0.3,
            transmission: 0.8,
            roughness: 0.1
        });
        const visor = new THREE.Mesh(visorGeo, visorMat);
        visor.position.set(0, 0.2, 0.2);
        visor.rotation.x = 0.2;
        robotGroup.add(visor);

        scene.add(robotGroup);

        // الإضاءة
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(currentState.hex, 2, 50);
        pointLight.position.set(2, 3, 4);
        scene.add(pointLight);

        camera.position.z = 4.5;

        // تحريك الروبوت والماتريكس
        function animate() {
            requestAnimationFrame(animate);
            
            // حركة دوران بطيئة للرأس
            robotGroup.rotation.y = Math.sin(Date.now() * 0.001) * 0.15;
            robotGroup.rotation.x = Math.cos(Date.now() * 0.0015) * 0.08;

            renderer.render(scene, camera);
        }
        animate();

        // تحديث الحالات والألوان
        function updateState(newState) {
            currentState = newState;
            document.documentElement.style.setProperty('--neon-color', newState.css);
            document.documentElement.style.setProperty('--shadow-color', newState.css);
            
            document.getElementById('status-badge').innerText = newState.text;
            
            eyeMat.color.setHex(newState.hex);
            visorMat.color.setHex(newState.hex);
            pointLight.color.setHex(newState.hex);
        }

        // تفاعل المدخلات
        function processInput() {
            const input = document.getElementById('user-input');
            if(!input.value.trim()) return;

            // تحويل للون الأزرق عند الرد
            updateState(BLUE_STATE);
            
            setTimeout(() => {
                alert("AI ROBOT X: تم استقبال الأمر وتنفيذه بنجاح.");
                input.value = "";
                // العودة للون الأحمر النيون بعد التفكير
                updateState(PINK_STATE);
            }, 1000);
        }

        // إشعار تغيير الحجم
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "app": "AI ROBOT X",
        "status": "online",
        "port": 7000
    })

if __name__ == '__main__':
    # التشغيل محلياً على المنفذ 7000
    app.run(host='0.0.0.0', port=7000, debug=True)
