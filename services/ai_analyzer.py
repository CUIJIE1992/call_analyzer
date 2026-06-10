#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI文本分析服务
使用DeepSeek API分析对话内容
"""

import os
import json
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _load_env_fallback():
    """兜底加载 .env，避免因启动顺序或子进程导致环境变量缺失"""
    from dotenv import load_dotenv
    load_dotenv(override=True)


class AIAnalyzer:
    """AI分析器类 - 使用DeepSeek API"""

    def __init__(self):
        # 先尝试从环境变量读取，缺失时强制从 .env 兜底加载
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            _load_env_fallback()
            self.api_key = os.getenv('DEEPSEEK_API_KEY')

        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-flash')

        if not self.api_key:
            raise ValueError("缺少环境变量 DEEPSEEK_API_KEY，请在 .env 文件中配置")
    
    def analyze_conversation(self, speaker1_text, speaker2_text):
        """
        分析对话内容
        
        Args:
            speaker1_text: 说话人1的文本
            speaker2_text: 说话人2的文本
            
        Returns:
            dict: 分析结果
        """
        conversation = self._format_conversation(speaker1_text, speaker2_text)
        
        prompt = f"""你是一位资深的房产销售分析专家，拥有10年以上房地产销售与客户分析经验。请基于以下购房咨询通话录音的对话内容，进行深入、客观、精准的分析。

【分析原则】
1. 以对话原文为唯一事实依据，避免凭空臆测；未提及的内容必须明确标注为"未提及"
2. 区分"客户明确表达"与"顾问主动询问"，仅在客户主动表达时记录需求
3. 区分"客户主动留下"与"顾问主动报出"的联系方式，务必精确分类
4. 意向判断要综合客户行为（到访、留电、询问细节等）和语言表达，不能仅凭信息量
5. 所有判断需结合中文房产销售的实际语境，避免套用通用话术

【对话内容】
{conversation}

【输出要求】
请严格按照以下JSON格式返回分析结果，不要返回任何markdown标记、代码块或额外说明文字：

{{
    "通话概要": {{
        "通话时长估算": "根据对话轮次和内容密度估算，格式如'约3分钟'/'约8分钟'",
        "有效沟通程度": "高/中/低（高=双方多轮深入交流；中=有问有答但话题不深；低=客户敷衍或单方陈述）",
        "客户响应积极性": "积极（主动提问、主动留电、主动到访）/一般（被动回答但配合）/冷淡（敷衍、推脱、拒绝）"
    }},
    "角色识别": {{
        "说话人1": "置业顾问",
        "说话人2": "客户"
    }},
    "购房意向": {{
        "面积需求": "客户主动提出的面积偏好，如未提及则填'未提及'",
        "价格区间": "客户主动提出的预算或总价/单价范围，如未提及则填'未提及'",
        "区域偏好": "客户主动提出的地段/片区/商圈偏好，如未提及则填'未提及'",
        "户型需求": "客户主动提出的户型/朝向/楼层等需求，如未提及则填'未提及'"
    }},
    "购房阶段": {{
        "当前阶段": "从'初步咨询/需求探明/方案对比/决策阶段/犹豫观望'中精确选择",
        "阶段特征": "用一句话说明判断依据，需引用对话中的具体行为或表达"
    }},
    "客户核心关注点": {{
        "第一关注": {{
            "因素": "从客户对话中提取的最核心关注因素，如价格、学区、交通、配套、户型、品质等",
            "具体内容": "客户在该因素上的具体表述或要求，需贴近原话"
        }},
        "第二关注": {{
            "因素": "第二核心关注因素",
            "具体内容": "具体表述或要求"
        }},
        "第三关注": {{
            "因素": "第三核心关注因素",
            "具体内容": "具体表述或要求"
        }},
        "其他关注": ["次要关注点1", "次要关注点2"]
    }},
    "竞品对比": {{
        "提及竞品": ["客户提到的其他楼盘或项目名称，无则填空数组"],
        "对比倾向": "倾向本项目/倾向竞品/中立对比/未做对比",
        "本项目优势": ["客户认可的本项目卖点"],
        "本项目劣势": ["客户提出的本项目不足或顾虑"]
    }},
    "客户评级": {{
        "购房意向强度": "高/中/低。判定标准：①客户主动留电话/加微信/预约到访/已到访→高；②客户主动询问房源细节、贷款政策、交付时间等→中偏高；③客户提出明确预算和需求但未承诺下一步→中；④客户敷衍、推脱、反复比较无明确偏好→低",
        "购买力评估": "高/中/低。根据客户职业、家庭结构、提及的预算区间、付款方式偏好综合判断",
        "决策周期": "短期（1个月内）/中期（1-3个月）/长期（3个月以上）/暂无明确计划",
        "综合等级": "A类（高意向+高/中购买力，1-3个月内可能成交）/B类（中意向或中购买力，需持续培育）/C类（低意向或低购买力，长期跟进）",
        "等级说明": "用1-2句话说明评级依据，需具体引用客户行为或表达"
    }},
    "情感与沟通": {{
        "客户态度": "积极/消极/中性/抵触。结合客户语气词、回应速度、提问主动性判断",
        "置业顾问表现": "从专业度、需求挖掘能力、异议处理、节奏控制等维度评价",
        "沟通效果": "总结本次沟通是否达成预期目标（明确需求/预约到访/留下联系方式等）"
    }},
    "关键信息提取": {{
        "客户联系方式": "严格区分：仅记录客户主动说出或确认的手机号/微信号。置业顾问主动报出的自己的联系方式不算。如无客户留下联系方式则填'暂无'",
        "顾问联系方式": "仅记录置业顾问在通话中主动报出的自己的手机号或微信号，如无则填'暂无'",
        "到访意向": "从'已到访/预约到访（明确日期或时间）/有意向到访（未明确时间）/暂无到访意向'中精确选择",
        "看房安排": "客户与顾问约定的具体看房时间/地点/方式，无则填'暂无'",
        "特殊需求": "客户的特殊购房需求，如置换、公积金贷款、首付比例、税费、落户、就学、老人同住等，无则填'暂无'"
    }},
    "总结": "用150-250字客观总结本次通话的核心发现：客户是谁、想要什么、顾虑什么、意向如何、关键跟进点是什么。需具体、有信息量，避免空话套话"
}}
"""
        
        try:
            result = self._call_deepseek_api(prompt)
            return result
        except Exception as e:
            logger.error(f'Analysis failed: {str(e)}')
            return {
                'error': f'分析失败: {str(e)}',
                '通话概要': {},
                '角色识别': {},
                '购房意向': {},
                '购房阶段': {},
                '客户核心关注点': {},
                '竞品对比': {},
                '客户评级': {},
                '情感与沟通': {},
                '关键信息提取': {},
                '总结': ''
            }
    
    def _call_deepseek_api(self, prompt):
        """调用DeepSeek API"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的房产销售分析师，擅长分析购房咨询通话录音。请严格按照JSON格式返回结果，不要返回任何markdown标记或额外说明。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        logger.debug(f"Calling DeepSeek API with model: {self.model}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"API error: {response.text}")
                raise Exception(f"API请求失败: {response.status_code}")
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logger.debug(f"API返回内容长度: {len(content)}")
                
                try:
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0]
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0]
                    
                    parsed = json.loads(content.strip())
                    return parsed
                except json.JSONDecodeError as je:
                    logger.error(f"JSON解析错误: {str(je)}")
                    logger.error(f"尝试解析的内容: {content[:500]}")
                    return {
                        '原始分析': content,
                        '总结': '请查看原始分析',
                        '通话概要': {},
                        '角色识别': {},
                        '购房意向': {},
                        '购房阶段': {},
                        '客户核心关注点': {},
                        '竞品对比': {},
                        '客户评级': {},
                        '情感与沟通': {},
                        '关键信息提取': {}
                    }
            else:
                error_msg = result.get('error', {}).get('message', '未知错误')
                logger.error(f"API返回格式错误: {error_msg}")
                raise Exception(f"API返回错误: {error_msg}")
                
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            raise Exception("API请求超时，请检查网络连接或稍后重试")
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"网络连接错误: {str(ce)}")
            raise Exception(f"网络连接失败: {str(ce)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
            raise Exception(f"API请求失败: {str(e)}")
    
    def _format_conversation(self, speaker1_text, speaker2_text):
        """格式化对话内容，按时间排序"""
        # 合并所有对话并按时间排序
        all_messages = []

        if isinstance(speaker1_text, list):
            for item in speaker1_text:
                if isinstance(item, dict):
                    all_messages.append({
                        'speaker': '说话人1',
                        'text': item.get('text', ''),
                        'start_time': item.get('start_time', 0)
                    })
                else:
                    all_messages.append({
                        'speaker': '说话人1',
                        'text': str(item),
                        'start_time': 0
                    })

        if isinstance(speaker2_text, list):
            for item in speaker2_text:
                if isinstance(item, dict):
                    all_messages.append({
                        'speaker': '说话人2',
                        'text': item.get('text', ''),
                        'start_time': item.get('start_time', 0)
                    })
                else:
                    all_messages.append({
                        'speaker': '说话人2',
                        'text': str(item),
                        'start_time': 0
                    })

        # 按时间排序
        all_messages.sort(key=lambda x: x['start_time'])

        # 格式化输出
        conversation = []
        for msg in all_messages:
            conversation.append(f"【{msg['speaker']}】：{msg['text']}")

        return '\n\n'.join(conversation)
    
    def extract_keywords(self, text):
        """提取关键词"""
        prompt = f"请从以下文本中提取5-10个关键词，用顿号分隔：\n\n{text}"
        
        try:
            result = self._call_deepseek_api(prompt)
            keywords_str = result.get('总结', '') or result.get('关键词', '')
            if '、' in keywords_str:
                return keywords_str.split('、')
            elif ',' in keywords_str:
                return keywords_str.split(',')
            else:
                return [keywords_str] if keywords_str else []
        except Exception as e:
            return []
    
    def summarize(self, text):
        """生成摘要"""
        prompt = f"请为以下文本生成一个简洁的摘要（100字以内）：\n\n{text}"
        
        try:
            result = self._call_deepseek_api(prompt)
            return result.get('总结', '摘要生成失败')
        except Exception as e:
            return f"摘要生成失败: {str(e)}"
    
    def generate_customer_tags(self, analysis):
        """
        根据分析结果自动生成客户标签
        
        Args:
            analysis: AI分析结果字典
            
        Returns:
            list: 标签列表
        """
        tags = []
        
        if not analysis:
            return tags
        
        rating = analysis.get('客户评级', {})
        stage = analysis.get('购房阶段', {})
        concerns = analysis.get('客户核心关注点', {})
        key_info = analysis.get('关键信息提取') or analysis.get('关键信息') or {}
        
        intention = rating.get('购房意向强度', '')
        if intention == '高':
            tags.append('高意向客户')
        elif intention == '中':
            tags.append('中意向客户')
        elif intention == '低':
            tags.append('低意向客户')
        
        grade = rating.get('综合等级', '')
        if grade and ('A' in grade or 'a' in grade):
            tags.append('A类优质客户')
        
        visit_intent = key_info.get('到访意向', '')
        if visit_intent == '已到访':
            tags.append('已到访客户')
            if '高意向客户' not in tags:
                tags.append('高意向客户')
                if '低意向客户' in tags:
                    tags.remove('低意向客户')
        elif visit_intent == '预约到访':
            tags.append('预约到访')
            if '高意向客户' not in tags and '中意向客户' not in tags:
                tags.append('高意向客户')
                if '低意向客户' in tags:
                    tags.remove('低意向客户')
        elif visit_intent == '有意向到访':
            tags.append('有意向到访')
            if '低意向客户' in tags and '高意向客户' not in tags and '中意向客户' not in tags:
                tags.append('中意向客户')
                tags.remove('低意向客户')
        
        contact = key_info.get('客户联系方式', '') or key_info.get('联系方式', '')
        if contact and contact != '暂无' and '无意向' not in visit_intent:
            tags.append('已留联系方式')
            if '低意向客户' in tags and '高意向客户' not in tags and '中意向客户' not in tags:
                tags.append('中意向客户')
                tags.remove('低意向客户')
        
        first_concern = concerns.get('第一关注', {})
        second_concern = concerns.get('第二关注', {})
        third_concern = concerns.get('第三关注', {})
        other_concerns = concerns.get('其他关注', [])
        
        all_concerns = []
        if first_concern.get('因素'):
            all_concerns.append(first_concern['因素'])
        if second_concern.get('因素'):
            all_concerns.append(second_concern['因素'])
        if third_concern.get('因素'):
            all_concerns.append(third_concern['因素'])
        all_concerns.extend(other_concerns)
        
        all_concerns_text = ' '.join(all_concerns)
        if '学区' in all_concerns_text or '教育' in all_concerns_text:
            tags.append('学区关注')
        if '交通' in all_concerns_text:
            tags.append('交通关注')
        
        current_stage = stage.get('当前阶段', '')
        if '改善' in current_stage:
            tags.append('改善型需求')
        elif '刚需' in current_stage or '首次' in current_stage:
            tags.append('刚需客户')
        elif '决策' in current_stage:
            tags.append('决策期客户')
        
        return tags
