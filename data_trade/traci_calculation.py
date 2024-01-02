import traci
import numpy as np
from datatype import PersonalData, TradingData, AccidentData
from typing import TypedDict
from env.gen_event import Event
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GlobalContext:
    vehicles: Dict[str, "SumoVehicle"] = None  # 车辆id访问对应的类
    event: Event = None  # 通过访问Event里的成员属性例如:accident_position等来得到对应event的信息
    step: int = None  # 当前时间
    visibility: float = None  # 可视距离


def Update_Cars_info(global_context: GlobalContext):
    vids = traci.vehicle.getIDList()
    # print(vids)
    for vid in vids:
        if vid not in global_context.vehicles.keys():
            # print("create : "+str(vid))
            global_context.vehicles[vid] = SumoVehicle(
                vid, 100, traci.vehicle.getTypeID(vid))

        if global_context.vehicles[vid].vtype == "human":
            continue
        global_context.vehicles[vid].update_info(global_context.step)
        # 更新车辆当前信息

# 对每辆车计算看到的车数量, 并直接更新到对应的车辆中


def Calc_traffic_flow(global_context: GlobalContext):
    vids = traci.vehicle.getIDList()

    for vid in vids:  # 这个地方还可以优化 但比较麻烦
        res = {}
        if global_context.vehicles[vid].vtype == "human":
            continue
        pos = np.array(global_context.vehicles[vid].position)
        for vid2 in vids:
            # print(global_context["cars"])
            dis = np.linalg.norm(pos-np.array(traci.vehicle.getPosition(vid2)))
            if dis < global_context.visibility:
                road = traci.vehicle.getRoadID(vid2)
                if road not in res.keys():
                    res[road] = 0
                res[road] += 1
        # simple version
        global_context.vehicles[vid].update_traffic_flow(res)


# 每辆车判断一下是否看到车祸信息
def Calc_nearby_accident(global_context: GlobalContext):
    vids = traci.vehicle.getIDList()
    for vid in vids:
        if global_context.vehicles[vid].vtype == "human":
            continue
        for eid in global_context.event.accident_object.keys():
            if eid in global_context.vehicles[vid].accident.keys():
                continue
            vehicle_position = np.array(
                global_context.vehicles[vid].position)
            event_position = np.array(
                global_context.event.accident_position[eid])
            if np.linalg.norm(event_position-vehicle_position) < global_context.visibility:
                global_context.vehicles[vid].accident[eid] = {
                    "Accident_Location": global_context.event.accident_location,
                    "Accident_Position": event_position,
                    "accident_time": global_context.step,  # detect time
                    "accident_vid": global_context.event.accident_object[eid],
                    "traded": False
                }

# 判断哪些车辆需要进入交易(距离下一个信号灯足够近)


def start_trade(global_context: GlobalContext):
    vids = traci.vehicle.getIDList()
    for vid in vids:
        if traci.vehicle.getTypeID(vid) == "human":
            continue
        if traci.vehicle.getNextTLS(vid)[0][2] < global_context.visibility:
            pass  # start trade
        # TODO: 这里应该是一个发起交易 读取各方信息的函数


class SumoVehicle:
    def __init__(self, car_id, init_currancy, vtype):
        self.vtype = vtype
        self.car_id = car_id
        self.accident = {}  # 目击到且尚未交易的事故
        self.history_trading_data = []  # 交易完成后把交易记录按顺序存储在里面
        self.currancy = init_currancy

    def update_info(self, step):
        self.update_step = step
        self.position = traci.vehicle.getPosition(self.car_id)
        self.speed = traci.vehicle.getSpeed(self.car_id)
        self.direction = traci.vehicle.getAngle(self.car_id)
        new_road = traci.vehicle.getRoadID(self.car_id)
        if not hasattr(self, "road") or not self.road == new_road:
            self.traffic_flow = {}  # recalculate traffic flow when entering a new road

    def update_traffic_flow(self, traffic_flow: dict):
        for key in traffic_flow.keys():
            if key not in self.traffic_flow.keys():
                self.traffic_flow[key] = {"visible_vehicle_count": []}
            self.traffic_flow[key]["visible_vehicle_count"].append(
                traffic_flow[key])

    def get_trading_data(self, global_context: GlobalContext):
        if len(self.accident) == 0:
            return None  # 如果没有可以交易的事故就返回None
        accident_id = list(self.accident.keys())[0]

        # 按照trading_test中的格式, 多了一个Accident_id方便以后要用
        accident_info = AccidentData(
            accident_id=self.accident[accident_id],
            accident_location=self.accident[accident_id]["Accident_Location"],
            time_to_trading_point=str(
                (global_context.step-self.accident[accident_id]["accident_time"])/10)+"s",
            distance_to_traing_point=str(np.linalg.norm(
                self.accident[accident_id]["Accident_Position"]-np.array(self.position)))+"m",
            accident_severity="high",
            traffic_flow=self.traffic_flow,
        )

        # {
        #     "Accident_Id": self.accident[accident_id],
        #     "Accident_Location": self.accident[accident_id]["Accident_Location"],
        #     "Time_To_Trading_Point": str((global_context.step-self.accident[accident_id]["accident_time"])/10)+"s",
        #     "Distance_To_Trading_Point": str(np.linalg.norm(self.accident[accident_id]["Accident_Position"]-np.array(self.position)))+"m",
        #     "Accident_Severity": "high",
        #     # 目前是一个字典, 键是道路ID ,值是一个list表示每个观测时刻看到的车辆数(每次进入新的道路刷新)
        #     "Traffic_Flow": self.traffic_flow,
        # }
        # 因为还没设定好交易完成后的数据格式, 这里历史平均价格本来应该从history_trading_data计算出来的
        # 还有就是如果当前是第一次交易那平均价格应该也是None才对
        return TradingData(current_token=self.currancy,
                           history_average_price=None, trading_history=self.history_trading_data, accident_info=accident_info)

    def get_personal_data(self, global_context: GlobalContext):
        return PersonalData(self.position)


class Controller:
    def __init__(self):
        pass
