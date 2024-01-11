import traci
import numpy as np
import sys
from typing import TypedDict, Dict, List
from dataclasses import dataclass, field
from typings.datatype import PersonalData, TradingData, AccidentData, GlobalContext
from DTM.env.gen_event import Event
from DTM.trading import Vehicle, Controller
from tests.trading_test import vehicle_preference


class DataTrade:
    def __init__(self, controller: Controller):
        self.controller = controller

    def start_trade(global_context: GlobalContext):
        vids = traci.vehicle.getIDList()
        for vid in vids:
            if traci.vehicle.getTypeID(vid) == "human":
                continue
            if traci.vehicle.getNextTLS(vid)[0][2] < global_context.visibility:
                vehicle = Vehicle(
                    vid,
                    global_context.vehicles[vid].get_personal_data(
                        global_context),
                    global_context.vehicles[vid].get_trading_data(
                        global_context),
                    vehicle_preference,
                )

            # TODO: 这里应该是一个发起交易 读取各方信息的函数
