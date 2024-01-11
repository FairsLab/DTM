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


class DataTrade:
    def __init__(self, controller: Controller):
        self.controller = controller

    def start_trade(self, global_context: GlobalContext):
        vids = traci.vehicle.getIDList()
        for vid in vids:
            if traci.vehicle.getTypeID(vid) == "human":
                continue
            print("*"*10, global_context.visibility)
            if traci.vehicle.getNextTLS(vid)[0][2] < global_context.visibility:
                vehicle = Vehicle(
                    vid,
                    global_context.vehicles[vid].get_personal_data(
                        global_context),
                    global_context.vehicles[vid].get_trading_data(
                        global_context),
                    vehicle_preference,
                )

            # 调用trading中的函数，发起交易
                openai_login(azure=True)

                self.offer_context = vehicle.propose_offer()
                self.decision_context = self.controller.decide_offer(
                    self.offer_context)
                print(self.offer_context)
                with open("./logs/offer_context.json", "a+") as f:
                    json.dump(self.offer_context, f)
                    f.write('\n')
                with open("./logs/decision_context.json", "a+") as f:
                    json.dump(self.decision_context, f)
                    f.write('\n')
