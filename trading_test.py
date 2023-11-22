# 用于测试函数
from .datatype import *
import openai
import logging
import re
import json
from .datatype_test import *

# 导入 openai 库
import openai
import os
from dotenv import load_dotenv
import pickle
import json



def openai_login(azure=False):
    load_dotenv()
    if azure is True:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # 请替换为您的 Azure OpenAI 服务的版本
        openai.deployment_id = os.getenv("DEPLOYMENT")  # 请替换为您的 Azure OpenAI 服务的版本
        print(openai.deployment_id)
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


openai_login(azure=True)

class MetaActor:
    personal_data: PersonalData
    trading_data: TradingData
    preference: Preference
    

class Vehicle(MetaActor):
    def propose_offer(self):
        # 整合输入数据
        input_data = {
            'personal_data': self.personal_data,
            'trading_data': self.trading_data,
            'preference': self.preference
        }
        function_call = {
            'function_name' : "generate_offer"
        }
        # 转换input_data为适合openai.ChatCompletion.create()的格式
        prompt = format_input_for_openai(input_data)

        # 调用openai.ChatCompletion.create()来生成提议
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= [{"role": "system", "content": prompt}] ,
            function = Offer,
            function_call = "auto",
            max_tokens=1, 
            temperature=0.1,
            # 其他适当的参数
        )
        # 从response中提取message
        message = response.choices[0].message
        print(message)

        # 返回message给controller
        return message


def format_input_for_openai(input_data):
    # 格式化input_data为字符串，适用于openai.ChatCompletion.create()
    # 这里可以根据您的具体需求进行定制
    return str(input_data)
       
        