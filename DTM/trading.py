import sys
import openai
import logging
import re
import json
from typings.datatype import PersonalData, TradingData, Preference, Offer, Decision


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
        # function_call = {"function_name": "generate_offer"}
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
            # 其他适当的参数
        )

        # 从response中提取message
        message = response.choices[0].message
        # TODO 保存message为json？

        # 返回message给controller
        return message


class Controller(MetaActor):
    def __init__(self, actor_id, personal_data, trading_data, preference) -> None:
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
        # function_call = {"function_name": "decide_offer"}
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
            # 其他适当的参数
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


def extract_first_number(text):
    # 使用正则表达式匹配第一个数字及其后的文本
    match = re.search(r"\d+", text)
    if match:
        # 提取第一个数字
        first_number = match.group()
        # 提取后面的文本，包括可能的换行符
        remaining_text = text[match.end() :].strip()
        return first_number, remaining_text
    else:
        # 如果没有找到数字，返回None
        return None, text


# TODO 待修改：提取response里面的内容用于保存
def process_response(response, actor):
    # 提取文本内容
    txt = response.choices[0].message.content
    logging.debug(response)

    # 提取价格和理由
    price, reason = extract_first_number(txt)
    logging.info(txt)

    # 构建结果字典
    result = {
        "actor_name": actor.name,
        "actor_role": actor.role,
        "response_text": txt,
        "price": price,
        "reason": reason,
        "usage_tokens": response.usage.total_tokens,
    }

    logging.info(result)
    return result


# TODO 根据 decision_message 决定是否结束交易
def judge(decision_message):
    # 这里可以根据您的需求来编写具体的逻辑
    # 例如，可以检查决策消息是否包含某些关键字或条件
    return "deal" in decision_message.lower() or "no deal" in decision_message.lower()


# TODO
def _trade():
    # vehicle_1 实例化
    
    # controller 实例化
    
    if trading_history.empty:
        pass
    else:
        pass
    
    # propose offer
    # decision offer
    
    