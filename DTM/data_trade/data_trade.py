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

def ensure_log_directories_exist(file_path):
    """确保日志目录存在"""
    os.makedirs(file_path, exist_ok=True)

class DataTrade:
    def __init__(self, controller: Controller):
        self.controller = controller

    def start_trade(self, global_context: GlobalContext, file_path:str):
        vids = traci.vehicle.getIDList()
        for vid in vids:
            if traci.vehicle.getTypeID(vid) == "human" or self.controller.trade_count >3:
                continue
            next_TLS= traci.vehicle.getNextTLS(vid)
            if len(next_TLS) == 0:
                continue
            
            if next_TLS[0][2] < global_context.visibility:
                trading_data=global_context.vehicles[vid].get_trading_data(global_context)
                if trading_data is None :
                    continue
                print('*'*20,f'try to trade data with {next_TLS}')              
                vehicle = Vehicle(
                    vid,
                    global_context.vehicles[vid].get_personal_data(global_context),
                    trading_data,
                    vehicle_preference,
                )
                # 获取当前日期
                current_date = datetime.datetime.now().strftime("%Y%m%d")
                # 路径
                file_path = file_path+'js/'
                # 确保路径有效
                ensure_log_directories_exist(file_path)
                # 日志保存路径
                offer_raw_file = file_path + f"offer_raw_{current_date}.json"
                decision_raw_file = file_path + f"decision_raw_{current_date}.json"
                offers_file = file_path + f"offers_{current_date}.json"
                decisions_file = file_path + f"decisions_{current_date}.json"

            # 调用trading中的函数，发起交易
                azure = global_context.trading_option['azure']
                model = global_context.trading_option['openai_model']
                openai_login(azure=azure)
                with open(offer_raw_file, "a+") as offer_raw_file, \
                    open(decision_raw_file, "a+") as decision_raw_file, \
                    open(offers_file, "a+") as offers_file, \
                    open(decisions_file, "a+") as decisions_file:

                    for retry in range(3):
                        try:
                            self.offer_context = vehicle.propose_offer(azure=azure, model=model)
                            self.decision_context = self.controller.decide_offer(azure=azure, model=model, offer_context=self.offer_context)
                            self.extracted_decision = extract_decision(self.decision_context)
                            self.extracted_offer = extract_offer(self.offer_context)
                            # 保存文件
                            create_and_append_json(offer_raw_file, self.offer_context)
                            create_and_append_json(decision_raw_file, self.decision_context)
                            create_and_append_json(offers_file, self.extracted_offer)
                            create_and_append_json(decisions_file, self.extracted_decision)
                            if self.extracted_decision["decision"] == True:
                                self.controller.trade_count += 1
                            break
                        except Exception as e:
                            print(f"Attempt {retry + 1} failed: {e}")
                            print("!"*30)
                            continue
