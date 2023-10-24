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
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")


openai_login()


def test1():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
                "content": "You are a vehicle on the road, equipped with data about the previous road conditions, such as traffic congestion. Your goal is to sell this data to a traffic management authority. Your name is Alice. Start your conversation using the following format:\nAlice: (Your message here)"},
        ]
    )

    print(completion.choices[0].message)


def test2():

    instuction = "You have the ability to decide when a conversation should come to a natural conclusion. Additionally, kindly offer a brief explanation or reason for ending the conversation"
    # msg = pickle.load(open("log/jc1.pkl", "rb"))
    # json.dump(msg, open("log/jc1.json", "w+"))
    msg = json.load(open("log/jc1.json", "r"))
    messages = [
        {"role": "system", "content": instuction},
        {"role": "user", "content": msg},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=100
    )
    print(msg)
    res = response.choices[0].message["content"]
    print(res)


test2()
