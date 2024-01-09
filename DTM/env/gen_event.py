"""
event class
"""
import pdb
from typing import Dict
import traci


class Event:
    def __init__(self, event: Dict):
        self.accident_var = event
        self.accident_object = {}
        self.accident_position = {}
        self.accident_location = {}

    def event_loger(self, step: int):
        self.__accident(step)

    def __accident(self, step: int):
        # list of start, end time, lane ID and position
        t_start = self.accident_var["start_time"]
        t_end = self.accident_var["end_time"]
        location = self.accident_var["lane"]
        position = self.accident_var["pos"]
        # find the nearest vehicle to put on hold.
        best_pos = 0
        accident_vehicle = None
        for step_start in t_start:
            if step == step_start:
                # pdb.set_trace()
                index_accident = t_start.index(step_start)
                edge = location[index_accident]
                pos = position[index_accident]
                loaded_vehicle_list = traci.lane.getLastStepVehicleIDs(edge)
                if loaded_vehicle_list:
                    for v_id in loaded_vehicle_list:
                        v_pos = traci.vehicle.getLanePosition(v_id)
                        if (
                            best_pos < v_pos <= pos
                            and traci.vehicle.getTypeID(v_id) == "human"
                        ):
                            accident_vehicle = v_id
                            best_pos = v_pos
                        if v_pos > pos:
                            if accident_vehicle:
                                self.accident_object[index_accident] = accident_vehicle
                                self.accident_position[
                                    index_accident
                                ] = traci.vehicle.getPosition(accident_vehicle)
                                self.accident_location[
                                    index_accident
                                ] = traci.vehicle.getRoadID(accident_vehicle)
                            else:
                                self.accident_object[index_accident] = v_id
                                self.accident_position[
                                    index_accident
                                ] = traci.vehicle.getPosition(v_id)

                                self.accident_location[
                                    index_accident
                                ] = traci.vehicle.getRoadID(v_id)
                            best_pos = 0
                            break
                else:
                    accident_index = t_start.index(step_start)
                    pdb.set_trace()
                    del t_start[accident_index]
                    del t_end[accident_index]
                    del location[accident_index]
                    del position[accident_index]
        # put accident vehicles on hold
        for v_id in self.accident_object.values():
            traci.vehicle.setType(v_id, "accident")
            traci.vehicle.setLaneChangeMode(v_id, 0)
            traci.vehicle.setSpeedMode(v_id, 0)
            traci.vehicle.setSpeed(v_id, 0)
        # accident over
        for step_end in t_end:
            if step == step_end:
                pdb.set_trace()
                index_accident = t_end.index(step_end)
                # pdb.set_trace()
                accident_vehicle = self.accident_object[index_accident]
                traci.vehicle.setType(accident_vehicle, "human")
                traci.vehicle.setLaneChangeMode(accident_vehicle, 1621)
                traci.vehicle.setSpeedMode(accident_vehicle, 31)
                traci.vehicle.setSpeed(accident_vehicle, -1)
                del self.accident_object[index_accident]
