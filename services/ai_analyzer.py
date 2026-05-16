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


class AIAnalyzer:
    """AI分析器类 - 使用DeepSeek API"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-5835f9a6bf63499fa077440fbb40fdd8')
        self.base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-flash')
    
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
        
        prompt = f"""你是一位专业的房产销售分析师，请分析以下购房咨询通话录音的文本内容，提供专业的购房电话分析报告。

对话内容：
{conversation}

请严格按照以下JSON格式返回分析结果，不要返回其他文本：
{{
    "通话概要": {{
        "通话时长估算": "根据对话内容估算的时长，如'约5分钟'",
        "有效沟通程度": "高/中/低",
        "客户响应积极性": "积极/一般/冷淡"
    }},
    "角色识别": {{
        "说话人1": "置业顾问",
        "说话人2": "客户"
    }},
    "购房意向": {{
        "面积需求": "如未提及则填'未提及'",
        "价格区间": "如未提及则填'未提及'",
        "区域偏好": "如未提及则填'未提及'",
        "户型需求": "如未提及则填'未提及'"
    }},
    "购房阶段": {{
        "当前阶段": "初步咨询/需求明确/决策阶段/犹豫观望",
        "阶段特征": "对当前阶段的简要描述"
    }},
    "客户核心关注点": {{
        "第一关注": {{
            "因素": "如学区、交通、价格等",
            "具体内容": "具体描述"
        }},
        "第二关注": {{
            "因素": "如学区、交通、价格等",
            "具体内容": "具体描述"
        }},
        "第三关注": {{
            "因素": "如学区、交通、价格等",
            "具体内容": "具体描述"
        }},
        "其他关注": ["关注点1", "关注点2"]
    }},
    "竞品对比": {{
        "提及竞品": ["竞品1", "竞品2"],
        "对比倾向": "倾向本项目/倾向竞品/中立对比",
        "本项目优势": ["优势1", "优势2"],
        "本项目劣势": ["劣势1", "劣势2"]
    }},
    "客户评级": {{
        "购房意向强度": "高/中/低",
        "购买力评估": "高/中/低",
        "决策周期": "短期（1个月内）/中期（1-3个月）/长期（3个月以上）",
        "综合等级": "A类/B类/C类",
        "等级说明": "对综合等级的简要说明"
    }},
    "情感与沟通": {{
        "客户态度": "积极/消极/中性",
        "置业顾问表现": "对置业顾问表现的评价",
        "沟通效果": "对整体沟通效果的评价"
    }},
    "关键信息提取": {{
        "联系方式": "如有则填，否则填'暂无'",
        "看房安排": "如有则填，否则填'暂无'",
        "特殊需求": "如有则填，否则填'暂无'"
    }},
    "跟进建议": {{
        "推荐话术要点": ["话术1", "话术2"],
        "差异化卖点强调": ["卖点1", "卖点2"],
        "异议处理建议": ["建议1", "建议2"],
        "下一步跟进计划": "具体的下一步行动建议"
    }},
    "总结": "本次通话的核心结论和跟进要点，100-200字"
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
                '跟进建议': {},
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
                        '关键信息提取': {},
                        '跟进建议': {}
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
        """格式化对话内容"""
        conversation = []
        
        if isinstance(speaker1_text, list):
            s1_text = ' '.join([item.get('text', '') if isinstance(item, dict) else str(item) 
                               for item in speaker1_text])
        else:
            s1_text = str(speaker1_text)
        
        if isinstance(speaker2_text, list):
            s2_text = ' '.join([item.get('text', '') if isinstance(item, dict) else str(item) 
                               for item in speaker2_text])
        else:
            s2_text = str(speaker2_text)
        
        conversation.append(f"【说话人1】：{s1_text}")
        conversation.append(f"【说话人2】：{s2_text}")
        
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
