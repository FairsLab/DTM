# 导入 openai 库
import openai
import os
from dotenv import load_dotenv
import logging
import copy
import pickle
import json
import re


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(process)d \n\t %(" "message)s",
    filename="log/trade2.log",
)


def openai_login(azure=False):
    load_dotenv()
    if azure is True:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_base = os.getenv("OPENAI_ENDPOINT")
        openai.api_type = "azure"
        openai.api_version = "2023-05-15"  # 请替换为您的 Azure OpenAI 服务的版本
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


openai_login()


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


class Agent:
    def __init__(self, role, name, personality=""):
        self.role = role
        self.name = name
        self.personality = personality

    def evaluate(self, data_description, history):
        instruction = ""
        if self.role == "car":
            # 简述角色信息和目标.
            instruction += "You are a car with information on the road conditions you have traveled on. Your name is {0}. You want to sell this information to the Traffic Light System and maximize your profits as much as possible.".format(
                self.name
            )
            # 加入性格特征的描写.
            instruction += self.personality

            instruction += (
                "\n Below is a description of the Data you'll be selling:\n"
                + data_description
                + "\n\n"
            )

        elif self.role == "center":
            instruction += "You are a Traffic Light System who wants to purchase traffic information from cars to optimize traffic. Your name is {0}. You want to buy this information from the car and maximize your profits as much as possible.".format(
                self.name
            )
            instruction += self.personality
            instruction += (
                "\n Below is a description of the data provided by the counterparty:\n"
                + data_description
                + "\n\n"
            )

        if history == []:
            instruction += (
                "Now you need to come up with a pricing and give reasons why.\n"
            )
        else:
            instruction += "Below is the pricing both parties used to generate during the negotiation process and the reasoning behind it:\n"
            for row in history:
                instruction += (
                    row["name"]
                    + "("
                    + row["role"]
                    + "):\nprice: "
                    + row["price"]
                    + "\nreason:"
                    + row["reason"]
                    + "\n\n"
                )
            instruction += "You rejected the other side's latest pricing, now you need to come up with a new pricing and explain the reason to your counterparty.\n"

        instruction += """
        \nIn order to keep the conversation concise, the reasons you give should be no more than 100 characters.
        The output should be formatted as follows:\n[first line](your pricing)\n[second line](your reason)
        """

        messages = [{"role": "system", "content": instruction}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0.4
        )
        txt = response.choices[0].message.content
        # logging.debug(response)
        price, reason = extract_first_number(txt)
        logging.info(txt)
        res = dict()
        res["role"] = self.name
        ret = {
            "usage": response["usage"].total_tokens,
            "name": self.name,
            "role": self.role,
            "price": price,
            "reason": reason,
        }

        logging.info(ret)
        return ret

    def decision(self, data_description, history):
        instruction = ""
        if self.role == "car":
            # 简述角色信息和目标.
            instruction += "You are a car with information on the road conditions you have traveled on. Your name is {0}. You want to sell this information to the Traffic Light System and maximize your profits as much as possible.".format(
                self.name
            )
            # 加入性格特征的描写.
            instruction += self.personality

            instruction += (
                "\n Below is a description of the Data you'll be selling:\n"
                + data_description
                + "\n\n"
            )

        elif self.role == "center":
            instruction += "You are a Traffic Light System who wants to purchase traffic information from cars to optimize traffic. Your name is {0}. You want to buy this information from the car and maximize your profits as much as possible.".format(
                self.name
            )
            instruction += self.personality
            instruction += (
                "\n Below is a description of the data provided by the counterparty:\n"
                + data_description
                + "\n\n"
            )

        instruction += "Below is the pricing both parties used to generate during the negotiation process and the reasoning behind it:\n"
        for row in history:
            instruction += (
                row["name"]
                + "("
                + row["role"]
                + "):\nprice: "
                + row["price"]
                + "\nreason:"
                + row["reason"]
                + "\n\n"
            )

        instruction += "You now need to decide whether to accept the last pricing and justification offered by the other party? Output 1 means yes, Output 2 means no and re-propose a price you can accept, Output 3 means no and withdraw from the negotiation. Please only output the corresponding number."

        messages = [{"role": "system", "content": instruction}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0.4
        )
        txt = response.choices[0].message.content
        if txt == "1":
            return 1
        elif txt == "3":
            return 3
        else:
            return 2


class Player:
    def __init__(self, role, name):
        self.name = name
        if role == "car":
            # self.system_message = """You are a vehicle on the road, equipped with data about the previous road conditions, such as traffic congestion.
            # Your goal is to sell this data to a traffic management authority. You are {0}. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Time is limited, try to end the conversation once the transaction ends. Start your conversation using the following format:\n{0}: (Your message here)""".format(self.name)
            self.system_message = "You are a professional data trader, specializing in selling road condition data to traffic management authorities. Your primary goal is to efficiently close deals. You are {0}. Keep the conversation concise and strictly focused on trade-related information. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Start your conversation using the following format:\n{0}: (Your trade proposal here).".format(
                self.name
            )
        elif role == "center":
            self.system_message = "You are a professional data trader representing a traffic management authority, specializing in purchasing road condition data to optimize traffic control. Your main focus is to efficiently close deals. You are {0}. Keep the conversation concise and strictly focused on trade-related information. Try to conclude the conversation promptly once the transaction is complete. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Start your conversation using the following format:\n{0}: (Your trade inquiry or offer here).".format(
                self.name
            )

    def generate(self, history):
        messages = [
            {"role": "system", "content": self.system_message},
        ]
        for row_o in history:
            row = copy.copy(row_o)
            if row["role"] != self.name:
                row["role"] = "user"
            else:
                row["role"] = "assistant"
            messages.append(row)
        print("message:", messages, "\nend QAQ\n")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, temperature=0.5
        )
        res = dict(response.choices[0].message)
        res["role"] = self.name
        return res, response["usage"].total_tokens


class Judge:
    @classmethod
    def is_conversation_end(self, history):
        # instuction = "You have the ability to decide when a conversation could come to a natural conclusion. Please provide a label of 0 if you believe the conversation cannot end, and a label of 1 if you think it's ok to end the conversation. Your output should only be 0 or 1."
        instuction = "You have the ability to decide when a conversation could come to a natural conclusion. Please provide a label of 0 if you believe the conversation cannot end, and a label of 1 if you think it's time to end the conversation. Your output should only be 0 or 1."
        msg = """Below is a chat history among a few people:\n\n """
        for row_o in history:
            msg += row_o["content"] + "\n\n"

        msg += """Your task is to determine whether the ongoing conversation should end. 
        return 0 if the conversation should continue. return 1 if the conversation should end. """
        messages = [
            {"role": "system", "content": instuction},
            {"role": "user", "content": msg},
        ]
        json.dump(msg, open("log/jc1.json", "w+"))

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages, max_tokens=1, temperature=0.1
        )
        res = response.choices[0].message["content"]
        print(res)
        assert res == "0" or res == "1"
        return res == "1"

    @classmethod
    def is_trade_made(self, history):
        pass

    @classmethod
    def get_trade_detail(self, history):
        pass


def _converse_demo():
    A = Player("car", "alice")
    B = Player("center", "bob")
    history = []
    total_use = 0
    for i in range(16):
        print("*" * 10, "\n", "round:{}\n".format(i))
        if i % 2 == 0:
            res, x = A.generate(history)
        else:
            res, x = B.generate(history)
        print("res:", res)
        history.append(res)
        total_use += x
        if Judge.is_conversation_end(history):
            break

    print("result:")
    for row in history:
        print(row)
    print(total_use)


def _demo():
    logging.info("start demo")
    A = Agent(
        "car",
        "alice",
        personality="You have enough time to negotiate, and you are very eager to maximize the benefits.",
    )
    A = Agent("car", "alice", personality="You've been running out of money lately.")
    B = Agent(
        "center",
        "Bob",
        "You have enough time to negotiate, and you are very eager to maximize the benefits.",
    )

    cnt = 0
    data_description = "A road condition information about section 'A01' five minutes ago The cost of collecting this information is approximately 137."
    history = []
    f = 0
    while True:
        tmp = A.evaluate(data_description=data_description, history=history)
        logging.info(tmp)
        history.append(tmp)

        d = B.decision(data_description=data_description, history=history)
        logging.info(d)
        if d == 1:
            return {"result": "deal"}
        elif d == 3:
            return {"result": "no deal"}

        A, B = B, A  # swap

        f = 1 - f

        cnt += 1
        if cnt == 6:
            break
    return {"result": "no deal"}


# _converse_demo()
if __name__ == "__main__":

    _demo()
