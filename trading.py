from datatype import *
import openai
import logging
import re
import json
from datatype_test import *

class MetaActor:
    personal_data: PersonalData
    trading_data: TradingData
    preference: Preference
    
def get_offer_info(input_data:str):
    offer_info =  {"description": "交通事故信息数据",
    "price": "12 dollars",
    "amount": "1 bit",
    "reason": "可以为你带来更高的交通效率和安全，提高交通流畅度，从而减少事故发生的可能性，并且对城市的交通管理有积极的影响。",
            }
    return json.dumps(offer_info)

def generate_offer(input_data):
    return {
        "description": "交通事故信息数据",
        "price": "12 dollars",
        "amount": "1 bit",
        "reason": "可以为你带来更高的交通效率和安全，提高交通流畅度，从而减少事故发生的可能性，并且对城市的交通管理有积极的影响。"
    }


class Vehicle(MetaActor):
    def __init__(self, personal_data, trading_data, preference) -> None:
        self.personal_data = personal_data
        self.trading_data = trading_data
        self.preference = preference
        
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

        

class Controller(MetaActor):
    def decide_offer(self, message):
        # 整合输入数据
        input_data = {
            'message': message,
            'personal_data': self.personal_data,
            'trading_data': self.trading_data,
            'preference': self.preference
        }

        # 转换input_data为适合openai.ChatCompletion.create()的格式
        prompt = format_input_for_openai(input_data)

        # 调用openai.ChatCompletion.create()来生成决策
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= [{"role": "system", "content": prompt}] ,
            max_tokens=1, 
            temperature=0.1,
            # 其他适当的参数
        )
        # 从response中提取新的message
        new_message = response.choices[0].message

        # 返回新的message给vehicle
        return new_message


def format_input_for_openai(input_data):
    # 格式化input_data为字符串，适用于openai.ChatCompletion.create()
    # 这里可以根据您的具体需求进行定制
    return str(input_data)

def extract_first_number(text):
    # 使用正则表达式匹配第一个数字及其后的文本
    match = re.search(r'\d+', text)
    if match:
        # 提取第一个数字
        first_number = match.group()
        # 提取后面的文本，包括可能的换行符
        remaining_text = text[match.end():].strip()
        return first_number, remaining_text
    else:
        # 如果没有找到数字，返回None
        return None, text


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
        "usage_tokens": response.usage.total_tokens
    }

    logging.info(result)
    return result

def extract_and_format(response):
    txt = response.choices[0].message.content
    price, reason = extract_first_number(txt)
    return {
        "response_text": txt,
        "price": price,
        "reason": reason,
        "usage_tokens": response.usage.total_tokens
    }

# class Vehicle(MetaActor):
#     def propose_offer(self):
#         # 调用openai.ChatCompletion.create()，同时使用 Function Calling
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             prompt=format_input_for_openai(self),
#             functions=[extract_and_format]
#         )
#         return response



def generate_offer_request(vehicle):
    # 构建请求的函数体
    function_call = {
        "function": "generate_offer",
        "inputs": {
            "description": "交通事故信息数据",
            "personal_data": vehicle.personal_data,
            "trading_data": vehicle.trading_data,
            "preference": vehicle.preference
        }
    }
    
    # 这里的prompt可以根据您的具体需求进行调整
    prompt = f"Generate an offer based on the following data: {function_call}"

    return prompt







class Controller(MetaActor):
    def decide_offer(self, message):
        # 类似地调用openai.ChatCompletion.create()，使用 Function Calling
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            prompt=format_input_for_openai(self, message),
            functions=[extract_and_format]
        )
        return response



def _demo():
    # 实例化 Vehicle 和 Controller
    vehicle = Vehicle(
        personal_data=vehicle_personal_data,
        trading_data=vehicle_trading_data,
        preference=vehicle_preference
    )

    controller = Controller(
        personal_data=controller_personal_data,
        trading_data=controller_trading_data,
        preference=controller_preference
    )

    history = []
    for i in range(1):  # 假设最多进行1轮交互
        print(f"Round {i + 1}")

        # Vehicle 提出提议
        proposal_message = vehicle.propose_offer()
        print("Vehicle Proposal:", proposal_message)

        # Controller 做出决策
        decision_message = controller.decide_offer(proposal_message)
        print("Controller Decision:", decision_message)

        # 记录历史
        history.append({
            'round': i + 1,
            'vehicle_proposal': proposal_message,
            'controller_decision': decision_message
        })

        # 决策逻辑，例如是否接受提议
        if judge(decision_message):
            break  # 如果决策已经做出，则结束循环

    # 打印交互历史
    print("Interaction History:")
    for entry in history:
        print(entry)

def judge(decision_message):
    # 根据 decision_message 决定是否结束交易
    # 这里可以根据您的需求来编写具体的逻辑
    # 例如，可以检查决策消息是否包含某些关键字或条件
    return "deal" in decision_message.lower() or "no deal" in decision_message.lower()

# 运行演示
if __name__ == "__main__":

    pass


