import traci
import numpy as np
import sys
from typing import TypedDict, Dict, List
from dataclasses import dataclass, field
from typings.datatype import PersonalData, TradingData, AccidentData, GlobalContext
from DTM.env.gen_event import Event
from DTM.trading import *
from tests.trading_test import vehicle_preference
import json
import datetime

def create_and_append_json(file, data):
    """向JSON文件追加数据"""
    json.dump(data, file)
    file.write('\n')

def ensure_log_directories_exist():
    """确保日志目录存在"""
    os.makedirs('./logs', exist_ok=True)

class DataTrade:
    def __init__(self, controller: Controller):
        self.controller = controller

    def start_trade(self, global_context: GlobalContext):
        vids = traci.vehicle.getIDList()
        for vid in vids:
            if traci.vehicle.getTypeID(vid) == "human":
                continue
            if traci.vehicle.getNextTLS(vid)[0][2] < global_context.visibility:
                vehicle = Vehicle(
                    vid,
                    global_context.vehicles[vid].get_personal_data(global_context),
                    global_context.vehicles[vid].get_trading_data(global_context),
                    vehicle_preference,
                )
                # 获取当前日期
                current_date = datetime.datetime.now().strftime("%Y%m%d")
                # 确保路径有效
                ensure_log_directories_exist()
                # 日志保存路径
                offer_raw_file = f"./logs/offer_raw_{current_date}.json"
                decision_raw_file = f"./logs/decision_raw_{current_date}.json"
                offers_file = f"./logs/offers_{current_date}.json"
                decisions_file = f"./logs/decisions_{current_date}.json"

            # 调用trading中的函数，发起交易
                azure = False
                openai_login(azure=azure)
                with open(offer_raw_file, "a+") as offer_raw_file, \
                    open(decision_raw_file, "a+") as decision_raw_file, \
                    open(offers_file, "a+") as offers_file, \
                    open(decisions_file, "a+") as decisions_file:

                    for retry in range(3):
                        try:
                            self.offer_context = vehicle.propose_offer(azure=azure)
                            self.decision_context = self.controller.decide_offer(azure=azure, offer_context=self.offer_context)
                            self.extracted_decision = extract_decision(self.decision_context)
                            self.extracted_offer = extract_offer(self.offer_context)
                            # 保存文件
                            create_and_append_json(offer_raw_file, self.offer_context)
                            create_and_append_json(decision_raw_file, self.decision_context)
                            create_and_append_json(offers_file, self.extracted_offer)
                            create_and_append_json(decisions_file, self.extracted_decision)
                            break
                        except Exception as e:
                            print(f"Attempt {retry + 1} failed: {e}")
                            print("!"*30)
                            continue
