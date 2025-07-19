#!/usr/bin/env python3
"""
星云Agent平台接口服务
提供与星云Agent平台的API交互功能
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

from typing import Dict, List, Optional
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XingyunService:
    """星云Agent平台服务类"""

    def __init__(self, api_key: str, base_url: str = "https://www.xingyunlink.com/api"):
        """
        初始化星云服务

        Args:
            api_key (str): API密钥
            base_url (str): 基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict:
        """
        发送HTTP请求

        Args:
            method (str): HTTP方法
            endpoint (str): 接口端点
            data (Optional[Dict]): 请求数据

        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            raise Exception(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            raise Exception(f"响应解析失败: {str(e)}")

    def chat_completion(
        self,
        messages: List[Dict],
        chat_id: Optional[str] = None,
        stream: bool = False,
        detail: bool = False,
        response_chat_item_id: Optional[str] = None,
        variables: Optional[Dict] = None,
        custom_uid: Optional[str] = None,
    ) -> Dict:
        """
        发起对话请求

        Args:
            messages (List[Dict]): 消息列表
            chat_id (Optional[str]): 对话ID
            stream (bool): 是否流式响应
            detail (bool): 是否返回详细信息
            response_chat_item_id (Optional[str]): 响应消息ID
            variables (Optional[Dict]): 变量
            custom_uid (Optional[str]): 自定义用户ID

        Returns:
            Dict: 响应数据
        """
        endpoint = "v1/chat/completions"

        data = {"messages": messages, "stream": stream, "detail": detail}

        # 可选参数
        if chat_id is not None:
            data["chatId"] = chat_id
        if response_chat_item_id is not None:
            data["responseChatItemId"] = response_chat_item_id
        if variables is not None:
            data["variables"] = variables
        if custom_uid is not None:
            data["customUid"] = custom_uid

        logger.info(f"发送对话请求: chat_id={chat_id}, stream={stream}")
        return self._make_request("POST", endpoint, data)

    def chat_with_text(
        self, text: str, chat_id: Optional[str] = None, **kwargs
    ) -> Dict:
        """
        发送文本消息

        Args:
            text (str): 文本内容
            chat_id (Optional[str]): 对话ID
            **kwargs: 其他参数

        Returns:
            Dict: 响应数据
        """
        messages = [{"role": "user", "content": text}]

        return self.chat_completion(messages, chat_id, **kwargs)

    def chat_with_image(
        self, text: str, image_url: str, chat_id: Optional[str] = None, **kwargs
    ) -> Dict:
        """
        发送包含图片的消息

        Args:
            text (str): 文本内容
            image_url (str): 图片URL
            chat_id (Optional[str]): 对话ID
            **kwargs: 其他参数

        Returns:
            Dict: 响应数据
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        return self.chat_completion(messages, chat_id, **kwargs)

    def get_chat_history(self, chat_id: str) -> Dict:
        """
        获取对话历史（如果平台支持）

        Args:
            chat_id (str): 对话ID

        Returns:
            Dict: 对话历史
        """
        # 注意：这个接口需要根据星云平台的实际API文档来实现
        # 当前文档中没有提供获取历史记录的接口
        logger.warning("获取对话历史功能需要根据实际API文档实现")
        return {"message": "此功能需要根据实际API文档实现"}


class XingyunExcelAnalyzer:
    """星云Excel分析器"""

    def __init__(self, api_key: str):
        """
        初始化分析器

        Args:
            api_key (str): 星云平台API密钥
        """
        self.xingyun_service = XingyunService(api_key)

    def analyze_excel_file(
        self, excel_file_path: str, custom_prompt: Optional[str] = None
    ) -> Dict:
        """
        分析Excel文件

        Args:
            excel_file_path (str): Excel文件路径
            custom_prompt (Optional[str]): 自定义提示词

        Returns:
            Dict: 分析结果
        """
        if custom_prompt is None:
            custom_prompt = """
            请分析这个Excel文件的数据内容，并提供以下分析：
            
            1. 数据概览：识别主要的变量、指标和数据维度
            2. 数据特征：分析数据的分布特征、异常值等
            3. 可视化建议：推荐2-4种最适合的图表类型，并说明理由
            4. 业务洞察：基于数据提供业务建议和发现
            5. HTML报告：生成一个包含图表和分析的HTML报告
            
            请确保分析结果专业、准确，HTML报告美观易读。
            """

        try:
            # 生成唯一的chat_id
            chat_id = f"excel_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 调用星云Agent进行分析
            result = self.xingyun_service.analyze_excel_with_xingyun(
                excel_file_path=excel_file_path, prompt=custom_prompt, chat_id=chat_id
            )

            logger.info(f"Excel分析完成: {excel_file_path}")
            return result

        except Exception as e:
            logger.error(f"Excel分析失败: {str(e)}")
            raise Exception(f"分析失败: {str(e)}")


# 使用示例
def main():
    """使用示例"""
    # 配置API密钥
    api_key = os.getenv("XINGYUN_API_KEY")

    # 创建服务实例
    xingyun_service = XingyunService(api_key)

    # 示例1：发送文本消息
    try:
        result = xingyun_service.chat_with_text(
            text="你好，请介绍一下你的功能", chat_id="test_chat_001"
        )
        print("文本对话结果:", json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"文本对话失败: {str(e)}")


if __name__ == "__main__":
    main()
