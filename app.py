
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template_string, jsonify, redirect, url_for
import json
import os
import base64
import re
import yt_dlp
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

app = Flask(__name__)

BLOCK_PAGE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>অ্যাক্সেস ব্লকড! - AKIL op</title>
    <style>
        body { background: #0d0b1d; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin:0; text-align:center; }
        .card { background: rgba(255, 59, 48, 0.1); border: 1px solid #ff3b30; border-radius: 20px; padding: 40px; max-width: 400px; }
        h1 { color: #ff453a; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚫 iOS ডিভাইস ব্লক!</h1>
        <p>নিরাপত্তা ও নীতিগত কারণে এই অ্যাপটি শুধুমাত্র Android ও Desktop ব্রাউজারে চলবে।</p>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AKIL op Control Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            font-family: 'Hind Siliguri', sans-serif;
            background: #090a0f;
            background-image: radial-gradient(at 10% 10%, rgba(247, 151, 30, 0.12) 0px, transparent 50%), radial-gradient(at 90% 90%, rgba(108, 92, 231, 0.15) 0px, transparent 50%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px 15px;
            color: #f1f2f6;
        }
        .app-container {
            background: rgba(18, 22, 36, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 30px;
            max-width: 550px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
        }
        .header { text-align: center; margin-bottom: 25px; }
        .brand { font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #f7971e, #ffd200); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .sub-title { font-size: 13px; color: #8a94a6; margin-top: 4px; }
        .nav-tabs { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; }
        .tab-btn { flex: 1; padding: 12px 10px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #a0a8c0; border-radius: 12px; cursor: pointer; font-weight: 600; font-size: 13px; white-space: nowrap; }
        .tab-btn.active { background: rgba(247, 151, 30, 0.2); border-color: #f7971e; color: #ffd200; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #cbd5e1; }
        input[type="text"], textarea { width: 100%; padding: 14px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.04); color: #fff; font-size: 14px; outline: none; }
        input:focus, textarea:focus { border-color: #f7971e; }
        .btn-submit { width: 100%; padding: 14px; border: none; border-radius: 12px; background: linear-gradient(135deg, #f7971e, #ffd200); color: #0d0b1d; font-size: 15px; font-weight: 700; cursor: pointer; margin-top: 10px; }
        .output-box { background: rgba(0, 0, 0, 0.4); border-radius: 12px; padding: 15px; margin-top: 18px; border-left: 4px solid #f7971e; word-break: break-all; font-size: 14px; color: #e2e8f0; min-height: 50px; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="header">
            <div class="brand">AKIL op Control Center</div>
            <div class="sub-title">Universal Multi-Tool Dashboard</div>
        </div>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('linkTab', this)">🔗 লিংক শার্ট</button>
            <button class="tab-btn" onclick="switchTab('videoTab', this)">🎬 ডাউনলোডার</button>
            <button class="tab-btn" onclick="switchTab('phoneTab', this)">📞 লুকআপ</button>
            <button class="tab-btn" onclick="switchTab('codeTab', this)">🛡️ অডিটর</button>
        </div>

        <!-- ১. লিংক শার্ট -->
        <div id="linkTab" class="tab-content active">
            <div class="form-group">
                <label>আপনার লিংক এখানে দিন:</label>
                <input type="text" id="linkInput" placeholder="https://youtube.com/...">
            </div>
            <button class="btn-submit" onclick="processLink()">কাস্টমাইজ করুন</button>
            <div class="output-box" id="linkOutput">ফলাফল এখানে আসবে...</div>
        </div>

        <!-- ২. ডাউনলোডার -->
        <div id="videoTab" class="tab-content">
            <div class="form-group">
                <label>ভিডিও লিংক (YouTube, FB, Insta, TikTok):</label>
                <input type="text" id="videoUrlInput" placeholder="https://...">
            </div>
            <button class="btn-submit" onclick="processVideo()">ডাউনলোড লিঙ্ক তৈরি করুন</button>
            <div class="output-box" id="videoOutput">ফলাফল এখানে আসবে...</div>
        </div>

        <!-- ৩. ফোন লুকআপ -->
        <div id="phoneTab" class="tab-content">
            <div class="form-group">
                <label>ফোন নাম্বার (কান্ট্রি কোড সহ):</label>
                <input type="text" id="phoneInput" placeholder="+8801700000000">
            </div>
            <button class="btn-submit" onclick="processPhone()">তথ্য খুঁজুন</button>
            <div class="output-box" id="phoneOutput">ফলাফল এখানে আসবে...</div>
        </div>

        <!-- ৪. কোড অডিটর -->
        <div id="codeTab" class="tab-content">
            <div class="form-group">
                <label>সোর্স কোড পেস্ট করুন:</label>
                <textarea id="codeInput" rows="4" placeholder="কোড পেস্ট করুন..."></textarea>
            </div>
            <button class="btn-submit" onclick="processCode()">সিকিউরিটি চেক করুন</button>
            <div class="output-box" id="codeOutput">ফলাফল এখানে আসবে...</div>
        </div>
    </div>

    <script>
        function switchTab(tabId, btn) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
        }

        function processLink() {
            const link = document.getElementById('linkInput').value.trim();
            if(!link) return alert('লিংক দিন!');
            fetch('/api/customize-link', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({link: link})
            }).then(r => r.json()).then(d => {
                document.getElementById('linkOutput').innerHTML = '✅ তৈরি হওয়া লিংক:<br><a href="'+d.result+'" target="_blank" style="color:#ffd200;">'+d.result+'</a>';
            });
        }

        function processVideo() {
            const url = document.getElementById('videoUrlInput').value.trim();
            document.getElementById('videoOutput').innerText = '⏳ প্রসেস করা হচ্ছে...';
            fetch('/api/download-video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            }).then(r => r.json()).then(d => {
                if(d.success) {
                    document.getElementById('videoOutput').innerHTML = '📌 <b>' + d.title + '</b><br><br><a href="'+d.download_url+'" target="_blank" style="color:#2ed573; font-weight:bold;">⬇️ সরাসরি ডাউনলোড করুন</a>';
                } else {
                    document.getElementById('videoOutput').innerText = '❌ এরর: ' + d.error;
                }
            });
        }

        function processPhone() {
            const phone = document.getElementById('phoneInput').value.trim();
            fetch('/api/lookup-phone', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone: phone})
            }).then(r => r.json()).then(d => {
                if(d.status === 'Success') {
                    document.getElementById('phoneOutput').innerHTML = `<b>দেশ:</b> ${d.country}<br><b>অপারেটর:</b> ${d.carrier}<br><b>হোয়াটসঅ্যাপ:</b> <a href="${d.links.WhatsApp}" target="_blank" style="color:#25D366;">চ্যাট লিংক</a>`;
                } else {
                    document.getElementById('phoneOutput').innerText = '❌ ' + d.message;
                }
            });
        }

        function processCode() {
            const code = document.getElementById('codeInput').value;
            fetch('/api/audit-code', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code})
            }).then(r => r.json()).then(d => {
                document.getElementById('codeOutput').innerHTML = `<b>অবস্থা:</b> ${d.status}<br><b>রিস্ক স্কোর:</b> ${d.score}<br><b>পরামর্শ:</b> ${d.recommendation}`;
            });
        }
    </script>
</body>
</html>
"""

@app.before_request
def block_ios():
    user_agent = request.headers.get('User-Agent', '')
    if any(dev in user_agent for dev in ['iPhone', 'iPad', 'iPod']):
        if not request.path.startswith('/static'):
            return render_template_string(BLOCK_PAGE)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/customize-link', methods=['POST'])
def api_customize_link():
    data = request.json or {}
    link = data.get('link', '')
    encoded = base64.urlsafe_b64encode(link.encode()).decode()
    redirect_url = url_for('redirect_link', path=encoded, _external=True)
    return jsonify({"result": redirect_url})

@app.route('/r/<path>')
def redirect_link(path):
    try:
        decoded = base64.urlsafe_b64decode(path.encode()).decode()
        return redirect(decoded)
    except Exception:
        return "Invalid Link", 400

@app.route('/api/download-video', methods=['POST'])
def api_download_video():
    url = request.json.get('url', '')
    ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'success': True,
                'title': info.get('title', 'Video'),
                'download_url': info.get('url', url)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/lookup-phone', methods=['POST'])
def api_lookup_phone():
    raw_num = request.json.get('phone', '')
    clean_num = raw_num.strip().replace(" ", "").replace("-", "")
    if not clean_num.startswith("+"):
        clean_num = "+88" + clean_num if clean_num.startswith("01") else "+" + clean_num
    try:
        parsed = phonenumbers.parse(clean_num, None)
        if not phonenumbers.is_valid_number(parsed):
            return jsonify({"status": "Error", "message": "অবৈধ ফোন নাম্বার!"})
        return jsonify({
            "status": "Success",
            "country": geocoder.country_name_for_number(parsed, "en") or "Unknown",
            "carrier": carrier.name_for_number(parsed, "en") or "N/A",
            "links": {"WhatsApp": f"https://wa.me/{parsed.country_code}{parsed.national_number}"}
        })
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

@app.route('/api/audit-code', methods=['POST'])
def api_audit_code():
    code = request.json.get('code', '')
    score = 0
    patterns = {r'eval\(': 5, r'exec\(': 5, r'os\.system\(': 4, r'rm -rf': 5}
    for pattern, p_score in patterns.items():
        if re.search(pattern, code):
            score += p_score
    status = "🟢 নিরাপদ" if score == 0 else ("🟡 মাঝারি ঝুঁকি" if score <= 5 else "🔴 উচ্চ ঝুঁকি")
    rec = "কোডে ক্ষতিকারক কিছু পাওয়া যায়নি।" if score == 0 else "বিপজ্জনক ফাংশন সনাক্ত হয়েছে।"
    return jsonify({"score": score, "status": status, "recommendation": rec})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
