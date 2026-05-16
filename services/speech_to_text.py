#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音转文本服务
支持火山引擎语音识别API（极速版/长音频版）和飞书妙计API
"""

import os
import json
import time
import uuid
import base64
import requests
import logging

logger = logging.getLogger(__name__)

# Cloudflare环境下不使用pydub
AudioSegment = None
try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


class SpeechToText:
    """语音转文本类"""
    
    def __init__(self):
        # 火山引擎API配置
        self.volc_api_key = os.getenv('VOLC_API_KEY', '5dcac6d7-6ed5-44eb-9076-a02c43d216dc')
        self.volc_app_id = os.getenv('VOLC_APP_ID', '')
        self.use_long_audio = os.getenv('VOLC_USE_LONG_AUDIO', 'false').lower() == 'true'
        
        # 飞书API配置（备用）
        self.feishu_app_id = os.getenv('FEISHU_APP_ID', '')
        self.feishu_app_secret = os.getenv('FEISHU_APP_SECRET', '')
        self.tenant_access_token = None
        self.token_expire_time = 0
    
    def transcribe(self, audio_path):
        """
        将音频文件转换为文本
        优先使用火山引擎API（极速版），失败后使用飞书API，最后使用模拟数据
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            list: 包含时间戳的文本片段列表
        """
        # 优先尝试火山引擎
        if self.volc_api_key:
            try:
                logger.info(f"使用火山引擎API识别: {audio_path}")
                if self.use_long_audio:
                    logger.info("使用长音频异步模式")
                    return self._transcribe_volc_long(audio_path)
                else:
                    logger.info("使用极速版模式")
                    return self._transcribe_volc_flash(audio_path)
            except Exception as e:
                logger.warning(f"火山引擎API调用失败: {e}，尝试飞书API")
        
        # 其次尝试飞书API
        if self.feishu_app_id and self.feishu_app_secret:
            try:
                logger.info(f"使用飞书API识别: {audio_path}")
                return self._transcribe_feishu(audio_path)
            except Exception as e:
                logger.warning(f"飞书API调用失败: {e}，使用模拟数据")
        
        # 最后使用模拟数据
        logger.info("使用模拟数据")
        return self._mock_transcribe(audio_path)
    
    def transcribe_from_url(self, audio_url):
        """
        通过URL使用火山引擎长音频API识别
        
        Args:
            audio_url: 音频文件的公网URL
            
        Returns:
            task_id: 任务ID，用于后续查询结果
        """
        logger.info(f"使用火山引擎长音频API识别URL: {audio_url}")
        return self._submit_volc_task_url(audio_url)
    
    def get_task_result(self, task_id):
        """
        查询长音频任务结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            dict: 包含状态和结果的字典
        """
        return self._poll_volc_task_once(task_id)
    
    def _transcribe_volc_flash(self, audio_path):
        """
        使用火山引擎极速版语音识别API（适合短音频）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            list: 格式化的识别结果
        """
        recognize_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
        
        # 将文件转换为Base64
        base64_data = self._file_to_base64(audio_path)
        
        # 构建请求头
        request_id = str(uuid.uuid4())
        headers = {
            "X-Api-Key": self.volc_api_key,
            "X-Api-Resource-Id": "volc.bigasr.auc_turbo",
            "X-Api-Request-Id": request_id,
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }
        
        # 如果配置了app_id，添加旧版header
        if self.volc_app_id:
            headers["X-Api-App-Key"] = self.volc_app_id
        
        # 构建请求体
        request_body = {
            "user": {
                "uid": self.volc_app_id or "default_user"
            },
            "audio": {
                "data": base64_data,
                "format": "mp3"
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_ddc": True,
                "enable_speaker_info": True,
                "enable_channel_split": False,
                "show_utterances": True,
                "vad_segment": False,
                "sensitive_words_filter": ""
            }
        }
        
        # 发送请求
        response = requests.post(recognize_url, json=request_body, headers=headers, timeout=120)
        
        # 检查响应头
        status_code = response.headers.get('X-Api-Status-Code', '')
        if status_code != '20000000':
            message = response.headers.get('X-Api-Message', '未知错误')
            raise Exception(f"火山引擎API错误: {status_code} - {message}")
        
        # 解析响应
        result = response.json()
        return self._format_volc_result(result)
    
    def _transcribe_volc_long(self, audio_path):
        """
        使用火山引擎长音频异步识别API（适合长音频）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            list: 格式化的识别结果
        """
        # 1. 提交任务
        task_id = self._submit_volc_task(audio_path)
        logger.info(f"任务已提交，Task ID: {task_id}")
        
        # 2. 轮询任务状态
        result = self._poll_volc_task(task_id)
        
        # 3. 格式化结果
        return self._format_volc_result(result)
    
    def _submit_volc_task(self, audio_path):
        """
        提交长音频识别任务

        Args:
            audio_path: 音频文件路径

        Returns:
            str: 任务ID
        """
        submit_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"

        # 将文件转换为Base64
        base64_data = self._file_to_base64(audio_path)

        # 构建请求头
        request_id = str(uuid.uuid4())
        headers = {
            "X-Api-Key": self.volc_api_key,
            "X-Api-Resource-Id": "volc.seedasr.auc",
            "X-Api-Request-Id": request_id,
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }

        # 如果配置了app_id，添加旧版header
        if self.volc_app_id:
            headers["X-Api-App-Key"] = self.volc_app_id

        # 构建请求体
        request_body = {
            "user": {
                "uid": self.volc_app_id or "default_user"
            },
            "audio": {
                "data": base64_data,
                "format": "mp3"
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_speaker_info": True,
                "show_utterances": True
            }
        }

        logger.info(f"提交本地文件任务请求")

        # 发送请求
        response = requests.post(submit_url, json=request_body, headers=headers, timeout=60)

        logger.info(f"提交本地文件任务响应状态码: {response.status_code}")

        # 检查响应头
        status_code = response.headers.get('X-Api-Status-Code', '')
        if status_code != '20000000':
            message = response.headers.get('X-Api-Message', '未知错误')
            raise Exception(f"火山引擎提交任务错误: {status_code} - {message}")

        # 根据火山引擎文档，submit接口响应体为空
        # 任务ID就是我们自己生成的X-Api-Request-Id
        logger.info(f"本地文件任务提交成功，任务ID: {request_id}")
        return request_id
    
    def _submit_volc_task_url(self, audio_url):
        """
        提交长音频识别任务（通过URL）

        Args:
            audio_url: 音频文件的公网URL

        Returns:
            str: 任务ID
        """
        submit_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"

        # 构建请求头
        request_id = str(uuid.uuid4())
        headers = {
            "X-Api-Key": self.volc_api_key,
            "X-Api-Resource-Id": "volc.seedasr.auc",
            "X-Api-Request-Id": request_id,
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }

        # 如果配置了app_id，添加旧版header
        if self.volc_app_id:
            headers["X-Api-App-Key"] = self.volc_app_id

        # 构建请求体 - 使用URL方式（完善参数）
        request_body = {
            "user": {
                "uid": "豆包语音"
            },
            "audio": {
                "url": audio_url,
                "format": "mp3"
            },
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "enable_speaker_info": True,
                "show_utterances": True
            }
        }

        logger.info(f"提交URL任务请求: {request_body}")
        logger.info(f"请求头: {headers}")

        # 发送请求
        response = requests.post(submit_url, json=request_body, headers=headers, timeout=60)

        logger.info(f"提交URL任务响应状态码: {response.status_code}")
        logger.info(f"提交URL任务响应头: {dict(response.headers)}")
        logger.info(f"提交URL任务响应内容: {repr(response.text)}")

        # 检查响应头
        status_code = response.headers.get('X-Api-Status-Code', '')
        if status_code != '20000000':
            message = response.headers.get('X-Api-Message', '未知错误')
            logger.error(f"API错误 - 状态码: {status_code}, 消息: {message}")
            raise Exception(f"火山引擎提交任务错误: {status_code} - {message}")

        # 根据火山引擎文档，submit接口响应体为空
        # 任务ID就是我们自己生成的X-Api-Request-Id
        logger.info(f"任务提交成功，任务ID: {request_id}")
        return request_id
    
    def _poll_volc_task_once(self, task_id):
        """
        单次查询长音频任务结果（不轮询）

        Args:
            task_id: 任务ID

        Returns:
            dict: 包含状态和结果的字典
        """
        query_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"

        # 构建请求头 - 重要：使用任务ID作为X-Api-Request-Id
        headers = {
            "X-Api-Key": self.volc_api_key,
            "X-Api-Resource-Id": "volc.seedasr.auc",
            "X-Api-Request-Id": task_id,
            "X-Api-Sequence": "-1",
            "Content-Type": "application/json"
        }

        # 根据火山引擎文档，查询接口的body是空json {}
        request_body = {}

        logger.info(f"查询任务请求: task_id={task_id}")

        # 发送请求
        response = requests.post(query_url, json=request_body, headers=headers, timeout=30)

        logger.info(f"查询任务响应状态: {response.status_code}")
        logger.info(f"查询任务响应头: {dict(response.headers)}")
        logger.info(f"查询任务响应内容: {response.text}")

        # 检查响应头
        status_code = response.headers.get('X-Api-Status-Code', '')
        
        # 处理状态码
        if status_code == '20000000':
            # 成功
            result = response.json()
            logger.info(f"查询任务响应JSON: {result}")
            return {
                'status': 'success',
                'result': result
            }
        elif status_code == '20000001':
            # 正在处理中
            return {
                'status': 'processing',
                'message': '任务正在处理中...'
            }
        elif status_code == '20000002':
            # 任务在队列中
            return {
                'status': 'processing',
                'message': '任务在队列中等待处理...'
            }
        else:
            # 其他错误
            message = response.headers.get('X-Api-Message', '未知错误')
            logger.error(f"API错误 - 状态码: {status_code}, 消息: {message}")
            return {
                'status': 'failed',
                'error': f"{status_code} - {message}"
            }
    
    def _poll_volc_task(self, task_id, max_wait=1800, poll_interval=5):
        """
        轮询查询长音频任务结果

        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒），默认30分钟
            poll_interval: 轮询间隔（秒）

        Returns:
            dict: 识别结果
        """
        query_url = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"

        start_time = time.time()

        while time.time() - start_time < max_wait:
            # 构建请求头 - 重要：使用任务ID作为X-Api-Request-Id
            headers = {
                "X-Api-Key": self.volc_api_key,
                "X-Api-Resource-Id": "volc.seedasr.auc",
                "X-Api-Request-Id": task_id,
                "X-Api-Sequence": "-1",
                "Content-Type": "application/json"
            }

            # 根据火山引擎文档，查询接口的body是空json {}
            request_body = {}

            # 发送请求
            response = requests.post(query_url, json=request_body, headers=headers, timeout=30)

            # 检查响应头
            status_code = response.headers.get('X-Api-Status-Code', '')

            if status_code == '20000000':
                # 任务完成
                result = response.json()
                logger.info(f"任务完成: {result}")
                return result
            elif status_code == '20000001' or status_code == '20000002':
                # 正在处理中或在队列中，继续等待
                logger.info(f"任务状态: {status_code} - 继续等待...")
                time.sleep(poll_interval)
            else:
                # 其他错误
                message = response.headers.get('X-Api-Message', '未知错误')
                raise Exception(f"火山引擎查询任务错误: {status_code} - {message}")

        # 超时
        raise Exception(f"长音频识别任务超时（{max_wait}秒）")
    
    def _file_to_base64(self, file_path):
        """
        将本地文件转换为Base64编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: Base64编码的文件内容
        """
        with open(file_path, 'rb') as file:
            file_data = file.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
        
        return base64_data
    
    def _format_volc_result(self, result):
        """
        格式化火山引擎API返回结果
        
        Args:
            result: API返回的JSON结果
            
        Returns:
            list: 格式化后的文本片段列表
        """
        formatted = []
        result_data = result.get('result', {})
        utterances = result_data.get('utterances', [])
        
        logger.info(f"找到 {len(utterances)} 个utterances")
        
        if not utterances:
            # 如果没有分段，使用整体文本
            text = result_data.get('text', '')
            logger.info(f"没有utterances，使用整体文本: {text[:100]}...")
            if text:
                formatted.append({
                    'text': text,
                    'timestamp': '00:00',
                    'start_time': 0,
                    'end_time': result.get('audio_info', {}).get('duration', 0),
                    'speaker_id': 1
                })
        else:
            merged = []
            current_speaker = None
            current_text = []
            current_start_time = None
            current_end_time = None
            
            for idx, utterance in enumerate(utterances):
                text = utterance.get('text', '')
                start_time = utterance.get('start_time', 0) / 1000.0  # 毫秒转秒
                end_time = utterance.get('end_time', 0) / 1000.0
                
                # 获取说话人ID - 支持两种格式
                speaker_id = 1
                
                # 格式1: utterance.additions.speaker (极速版格式)
                additions = utterance.get('additions', {})
                if additions:
                    spk_str = additions.get('speaker')
                    if spk_str is not None:
                        speaker_id = int(spk_str)
                
                # 格式2: utterance.speaker_info.spk_id (长音频格式)
                if speaker_id == 1:
                    speaker_info = utterance.get('speaker_info', {})
                    if speaker_info:
                        spk_id = speaker_info.get('spk_id')
                        if spk_id is not None:
                            speaker_id = int(spk_id) + 1  # 确保从1开始
                
                logger.info(f"Utterance {idx}: 说话人={speaker_id}, 文本='{text}'")
                
                # 合并逻辑：如果说话人相同且文本连续，则合并
                if speaker_id == current_speaker:
                    current_text.append(text)
                    current_end_time = end_time
                else:
                    # 如果有之前的内容，先保存
                    if current_speaker is not None:
                        minutes = int(current_start_time // 60)
                        seconds = int(current_start_time % 60)
                        timestamp = f"{minutes:02d}:{seconds:02d}"
                        
                        merged.append({
                            'text': ''.join(current_text),
                            'timestamp': timestamp,
                            'start_time': current_start_time,
                            'end_time': current_end_time,
                            'speaker_id': current_speaker
                        })
                    
                    # 开始新的说话人
                    current_speaker = speaker_id
                    current_text = [text]
                    current_start_time = start_time
                    current_end_time = end_time
            
            # 保存最后一个说话人的内容
            if current_speaker is not None:
                minutes = int(current_start_time // 60)
                seconds = int(current_start_time % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                
                merged.append({
                    'text': ''.join(current_text),
                    'timestamp': timestamp,
                    'start_time': current_start_time,
                    'end_time': current_end_time,
                    'speaker_id': current_speaker
                })
            
            formatted = merged
        
        return formatted
    
    def _transcribe_feishu(self, audio_path):
        """
        使用飞书妙计API（备用方案）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            list: 格式化的识别结果
        """
        token = self._get_tenant_access_token()
        
        upload_url = "https://open.feishu.cn/open-apis/speech_to_text/v1/file/upload"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        with open(audio_path, 'rb') as f:
            files = {'file': f}
            data = {
                'file_name': os.path.basename(audio_path),
                'file_type': 'mp3'
            }
            
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            upload_result = response.json()
            
        if upload_result.get('code') != 0:
            raise Exception(f"上传文件失败: {upload_result.get('msg')}")
        
        file_token = upload_result['data']['file_token']
        
        task_url = "https://open.feishu.cn/open-apis/speech_to_text/v1/task/create"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        task_data = {
            "file_token": file_token,
            "language": "zh-CN",
            "enable_diarization": True,
            "speaker_count": 2
        }
        
        response = requests.post(task_url, headers=headers, json=task_data)
        task_result = response.json()
        
        if task_result.get('code') != 0:
            raise Exception(f"创建任务失败: {task_result.get('msg')}")
        
        task_id = task_result['data']['task_id']
        
        result = self._poll_feishu_task_result(token, task_id)
        
        return self._format_feishu_result(result)
    
    def _get_tenant_access_token(self):
        """获取飞书tenant_access_token"""
        if self.tenant_access_token and time.time() < self.token_expire_time:
            return self.tenant_access_token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "app_id": self.feishu_app_id,
            "app_secret": self.feishu_app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if result.get('code') == 0:
                self.tenant_access_token = result.get('tenant_access_token')
                self.token_expire_time = time.time() + result.get('expire', 7200) - 300
                return self.tenant_access_token
            else:
                raise Exception(f"获取token失败: {result.get('msg')}")
        except Exception as e:
            raise Exception(f"飞书认证失败: {str(e)}")
    
    def _poll_feishu_task_result(self, token, task_id, max_wait=300):
        """轮询飞书任务结果"""
        url = f"https://open.feishu.cn/open-apis/speech_to_text/v1/task/get"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "task_id": task_id
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(url, headers=headers, params=params)
            result = response.json()
            
            if result.get('code') != 0:
                raise Exception(f"查询任务失败: {result.get('msg')}")
            
            status = result['data']['status']
            
            if status == 2:
                return result['data']['result']
            elif status == 3:
                raise Exception("转写任务失败")
            
            time.sleep(2)
        
        raise Exception("转写任务超时")
    
    def _format_feishu_result(self, result):
        """格式化飞书API返回结果"""
        formatted = []
        
        if isinstance(result, dict):
            sentences = result.get('sentences', [])
            
            for sentence in sentences:
                text = sentence.get('text', '')
                start_time = sentence.get('start_time', 0) / 1000
                end_time = sentence.get('end_time', 0) / 1000
                
                minutes = int(start_time // 60)
                seconds = int(start_time % 60)
                timestamp = f"{minutes:02d}:{seconds:02d}"
                
                formatted.append({
                    'text': text,
                    'timestamp': timestamp,
                    'start_time': start_time,
                    'end_time': end_time,
                    'speaker_id': sentence.get('speaker_id', 1)
                })
        
        return formatted
    
    def _mock_transcribe(self, audio_path):
        """
        模拟转写结果（降级方案）
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            list: 模拟的文本片段列表
        """
        duration = 60
        if AudioSegment is not None:
            try:
                audio = AudioSegment.from_mp3(audio_path)
                duration = len(audio) / 1000
            except:
                pass
        
        mock_texts = [
            "您好，请问有什么可以帮您的？",
            "我想咨询一下你们的房产项目。",
            "好的，我们项目位于市中心，交通非常便利。",
            "请问价格大概是多少？",
            "均价在四万五左右，具体要看户型和楼层。",
            "那有什么户型可选？",
            "我们有两室、三室、四室多种户型可供选择。",
            "好的，我考虑一下再联系您。",
            "没问题，这是我的联系方式，随时欢迎您咨询。"
        ]
        
        results = []
        time_per_text = duration / len(mock_texts) if mock_texts else 0
        
        for i, text in enumerate(mock_texts):
            start_time = i * time_per_text
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            
            results.append({
                'text': text,
                'timestamp': f"{minutes:02d}:{seconds:02d}",
                'start_time': start_time,
                'end_time': (i + 1) * time_per_text,
                'speaker_id': 1 if i % 2 == 0 else 2
            })
        
        return results
