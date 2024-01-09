# 用于测试函数
import openai
import logging
import re
import json
import sys
import os
from dotenv import load_dotenv
import pickle
from pathlib import Path
# 获取当前脚本所在目录的父目录（假设它是项目根目录），将项目根目录添加到 sys.path，导入项目模块
root_dir = Path(__file__).parent.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from DTM.trading import Vehicle
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


openai_login(azure=True)

actor_id = 'vehicle_001'

# 智能车的个人数据
vehicle_personal_data = PersonalData(location=[10, 20])

# 智能车的交易数据
vehicle_trading_data = TradingData(
    current_token=50.0,
    history_average_price=10.0,
    accident_info={
        "Accident_Location": "road A",
        "Distance_To_Trading_Point": "50m",
        "Time_To_Trading_Point": "20s",
        "Accident_Severity": "high",
        "Traffic_Flow": "500 veh/h",
    },
)

# 智能车的偏好设置
vehicle_preference = Preference(
    trading_purpose="获得最大化收益", expected_price=10.0, cost=1.0
)

vehicle_1 = Vehicle(actor_id, vehicle_personal_data, vehicle_trading_data, vehicle_preference)

print(vehicle_1.propose_offer())
