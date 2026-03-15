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

# 简单的Flask应用，只使用标准库
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>购房意向智能分析系统</title>
</head>
<body>
    <h1>购房意向智能分析系统</h1>
    <p>系统正在部署中，请稍后再试...</p>
    <p>Deployment in progress, please check back later...</p>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "ok", "message": "Server is running"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
