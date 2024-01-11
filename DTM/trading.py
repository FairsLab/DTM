import sys
import openai
import os
import logging
import re
import json
from dotenv import load_dotenv
from typings.datatype import *


def openai_login(azure=False):
    load_dotenv()
    if azure is True:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = (
            "2023-07-01-preview"  # 使用function_calling 有特定version需求，且gpt需要部署为0613版本
        )
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


class MetaActor:
    personal_data: PersonalData
    trading_data: TradingData
    preference: Preference


class Vehicle(MetaActor):
    def __init__(self, actor_id, personal_data, trading_data, preference) -> None:
        self.actor_id = actor_id
        self.personal_data = personal_data
        self.trading_data = trading_data
        self.preference = preference

    def propose_offer(self):
        # 整合输入数据
        input_data = {
            "personal_data": self.personal_data,
            "trading_data": self.trading_data,
            "preference": self.preference,
        }
        # 转换input_data为适合openai.ChatCompletion.create()的格式
        prompt = format_input_for_openai(input_data)

        # 调用openai.ChatCompletion.create()来生成提议
        response = openai.ChatCompletion.create(
            engine="gpt35",  # 部署名
            messages=[{"role": "user", "content": prompt}],
            functions=Offer,
            function_call="auto",
            # max_tokens=1,
            # temperature=0.1,
        )

        # 从response中提取message
        message = response.choices[0].message

        # 返回message给controller
        return message


class Controller(MetaActor):
    def __init__(self, actor_id, personal_data: ControllerPersonalData, trading_data, preference) -> None:
        self.actor_id = actor_id
        self.personal_data = personal_data
        self.trading_data = trading_data
        self.preference = preference

    def decide_offer(self, offer_context):
        # 整合输入数据
        input_data = {
            "message": offer_context,
            "personal_data": self.personal_data,
            "trading_data": self.trading_data,
            "preference": self.preference,
        }
        # 转换input_data为适合openai.ChatCompletion.create()的格式
        prompt = format_input_for_openai(input_data)
        # 调用openai.ChatCompletion.create()来生成提议
        response = openai.ChatCompletion.create(
            engine="gpt35",  # 部署名
            messages=[{"role": "user", "content": prompt}],
            functions=Decision,
            function_call="auto",
            # max_tokens=1,
            # temperature=0.1,
        )

        # 从response中提取message
        message = response.choices[0].message
        # TODO 保存message为json？

        # 返回message给controller
        return message


def format_input_for_openai(input_data):
    # 格式化input_data为字符串，适用于openai.ChatCompletion.create()
    # 这里可以根据您的具体需求进行定制
    return str(input_data)


# def extract_first_number(text):
#     # 使用正则表达式匹配第一个数字及其后的文本
#     match = re.search(r"\d+", text)
#     if match:
#         # 提取第一个数字
#         first_number = match.group()
#         # 提取后面的文本，包括可能的换行符
#         remaining_text = text[match.end() :].strip()
#         return first_number, remaining_text
#     else:
#         # 如果没有找到数字，返回None
#         return None, text


# 提取response里面的内容用于保存
def extract_offer(offer_context):
    # 解析 JSON 字符串
    arguments_string = offer_context["function_call"]["arguments"]
    print("-"*20, arguments_string)
    arguments = json.loads(arguments_string)
    # 提取信息
    data_description = arguments.get("data_description", "")
    price = arguments.get("price", 0)
    offer_reason = arguments.get("reason", "")

    extracted_info = {
        "data_description": data_description,
        "price": price,
        "offer_reason": offer_reason
    }
    # TODO 保存数据

    return extracted_info


def extract_decision(decision_context):
    # 解析 JSON 字符串
    arguments_string = decision_context["function_call"]["arguments"]
    print("?"*20, arguments_string)
    arguments = json.loads(arguments_string)
    # 提取信息
    decision = arguments.get("decision", False)
    decision_reason = arguments.get("reason", "")

    extracted_info = {
        "decision": decision,
        "reason": decision_reason
    }
    return extracted_info


# TODO 在data_trade里面调用上述函数
# def _trade():
    # vehicle_1 实例化

    # controller 实例化

    # 判断空值
    # propose offer
    # decision offer
