# 用于测试函数
from datatype import *
import openai
import logging
import re
import json
from trading import Vehicle

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


# 智能车的个人数据
vehicle_personal_data = PersonalData(
    location=[10, 20]
)

# 智能车的交易数据
vehicle_trading_data = TradingData(
    current_token=50.0,
    history_average_price=10.0,
    accident_info={
        "Accident_Location": "road A",
        "Distance_To_Trading_Point": "50m",
        "Time_To_Trading_Point": "20s",
        "Accident_Severity": "high",
        "Traffic_Flow": "500 veh/h"
    }
)

# 智能车的偏好设置
vehicle_preference = Preference(
    trading_purpose="获得最大化收益",
    expected_price=10.0,
    cost=1.0
)

vehicle_1 = Vehicle(vehicle_personal_data, vehicle_trading_data, vehicle_preference)

print(vehicle_1.propose_offer)

        