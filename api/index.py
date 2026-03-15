#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel Serverless Function Entry Point
购房意向智能分析系统 - Vercel部署入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 简单的HTTP处理，只使用标准库
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>购房意向智能分析系统</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .status {
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            margin: 20px 0;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .feature {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .feature h3 {
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 购房意向智能分析系统</h1>
        <div class="status">
            <h2>✅ 系统已成功部署</h2>
            <p>Server is running successfully on Vercel</p>
        </div>
        <div class="features">
            <div class="feature">
                <h3>🎵 音频分析</h3>
                <p>支持MP3格式通话录音分析</p>
            </div>
            <div class="feature">
                <h3>🤖 AI智能分析</h3>
                <p>基于MiniMax API的智能文本分析</p>
            </div>
            <div class="feature">
                <h3>📊 数据可视化</h3>
                <p>历史记录统计与趋势分析</p>
            </div>
        </div>
        <p style="text-align: center; margin-top: 40px; opacity: 0.8;">
            部署时间：2026-03-15 | 版本：v1.0.0
        </p>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Server is running",
            "timestamp": str(__import__('datetime').datetime.now()),
            "environment": "vercel"
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
