# 导入 openai 库
import openai
import os
from dotenv import load_dotenv
import copy
import pickle
import json


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


class Player:

    def __init__(self, role, name):
        self.name = name
        if role == 'car':
            # self.system_message = """You are a vehicle on the road, equipped with data about the previous road conditions, such as traffic congestion.
            # Your goal is to sell this data to a traffic management authority. You are {0}. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Time is limited, try to end the conversation once the transaction ends. Start your conversation using the following format:\n{0}: (Your message here)""".format(self.name)
            self.system_message = "You are a professional data trader, specializing in selling road condition data to traffic management authorities. Your primary goal is to efficiently close deals. You are {0}. Keep the conversation concise and strictly focused on trade-related information. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Start your conversation using the following format:\n{0}: (Your trade proposal here).".format(
                self.name)
        elif role == "center":
            self.system_message = "You are a professional data trader representing a traffic management authority, specializing in purchasing road condition data to optimize traffic control. Your main focus is to efficiently close deals. You are {0}. Keep the conversation concise and strictly focused on trade-related information. Try to conclude the conversation promptly once the transaction is complete. For efficiency, keep the conversation concise, response should be brief and within 200 characters. Start your conversation using the following format:\n{0}: (Your trade inquiry or offer here).".format(
                self.name)

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
            model="gpt-3.5-turbo",
            messages=messages,

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
            msg += row_o["content"]+'\n\n'

        msg += """Your task is to determine whether the ongoing conversation should end. 
        return 0 if the conversation should continue. return 1 if the conversation should end. """
        messages = [
            {"role": "system", "content": instuction},
            {"role": "user", "content": msg},
        ]
        print("d")
        json.dump(msg, open("log/jc1.json", "w+"))
        print("dd")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1,
            temperature=0.1
        )
        print("ddd")
        res = response.choices[0].message["content"]
        print(res)
        assert res == "0" or res == "1"
        return res == "1"


def _converse_demo():
    A = Player("car", "alice")
    B = Player("center", "bob")
    history = []
    total_use = 0
    for i in range(16):
        print("*"*10, '\n', "round:{}\n".format(i))
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


_converse_demo()
