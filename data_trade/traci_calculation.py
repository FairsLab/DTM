import traci
import numpy as np
from datatype import PersonalData, TradingData


def Update_Cars_info(global_context):
    vids = traci.vehicle.getIDList()
    # print(vids)
    for vid in vids:
        if vid not in global_context["vehicles"].keys():
            # print("create : "+str(vid))
            global_context["vehicles"][vid] = SumoVehicle(
                vid, 100, traci.vehicle.getTypeID(vid))

        if global_context["vehicles"][vid].vtype == "human":
            continue
        global_context["vehicles"][vid].update_info(global_context["step"])


def Calc_traffic_flow(global_context):
    vids = traci.vehicle.getIDList()
    # print(vids)

    for vid in vids:
        res = {}
        if global_context["vehicles"][vid].vtype == "human":
            continue
        pos = np.array(global_context["vehicles"][vid].position)
        for vid2 in vids:
            # print(global_context["cars"])
            dis = np.linalg.norm(pos-np.array(traci.vehicle.getPosition(vid2)))
            if dis < global_context["range"]:
                road = traci.vehicle.getRoadID(vid2)
                if road not in res.keys():
                    res[road] = 0
                res[road] += 1
        global_context["vehicles"][vid].traffic_flow = res  # simple version


def Calc_nearby_accident(global_context):
    vids = traci.vehicle.getIDList()
    for vid in vids:
        if global_context["vehicles"][vid].vtype == "human":
            continue
        for eid in global_context["event"].accident_object.keys():
            if eid in global_context["vehicles"][vid].accident.keys():
                continue
            a = np.array(global_context["vehicles"][vid].position)
            b = np.array(global_context["event"].accident_position[eid])
            if np.linalg.norm(a-b) < global_context["range"]:
                global_context["vehicles"][vid].accident[eid] = {
                    "Accident_Location": global_context["event"].accident_location,
                    "Accident_Position": b,
                    "accident_time": global_context["step"],  # detect time
                    "accident_vid": global_context["event"].accident_object[eid],
                    "traded": False
                }


def start_trade(global_context):
    vids = traci.vehicle.getIDList()
    for vid in vids:
        if traci.vehicle.getTypeID(vid) == "human":
            continue
        if traci.vehicle.getNextTLS(vid)[0][2] < global_context["range"]:
            pass  # start trade


class SumoVehicle:
    def __init__(self, car_id, init_currancy, vtype):
        self.vtype = vtype
        self.car_id = car_id
        self.history_trading_data = []
        self.currancy = init_currancy
        self.accident = {}

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

    def get_trading_data(self, global_context):
        if len(self.accident) == 0:
            return None
        accident_id = list(self.accident.keys())[0]

        accident_info = {"Accident_id": self.accident[accident_id],
                         "Accident_Location": self.accident[accident_id]["Accident_Location"],
                         "Time_To_Trading_Point": str((global_context["step"]-self.accident[accident_id]["accident_time"])/10)+"s",
                         "Distance_To_Trading_Point": str(np.linalg.norm(self.accident[accident_id]["Accident_Position"]-np.array(self.position)))+"m",
                         "Accident_Severity": "high",
                         "Traffic_Flow": self.traffic_flow,
                         }
        return TradingData(current_token=self.currancy,
                           history_average_price=None, trading_history=self.history_trading_data, accident_info=accident_info)

    def get_personal_data(self, global_context):
        return PersonalData(self.position)


class TLS:
    def __init__(self):
        pass
