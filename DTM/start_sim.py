from __future__ import absolute_import
from __future__ import print_function

import pdb
from typing import Dict
import os

# import pdb
import sys
from tests.trading_test import controller_1

try:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    import sumolib
except ImportError:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
import traci
import csv


from DTM.env.generate_sumo import GenSumo
from DTM.env.gen_event import Event
from DTM.control.signal_control import SignalControl
from DTM.data_trade.data_trade import DataTrade
from DTM.data_trade.traci_calculation import (
    Update_Cars_info,
    Calc_nearby_accident,
    Calc_traffic_flow,
    GlobalContext,
    _get_total_delay,
)
from typings.datatype import *
from DTM.plot_delay import RealTimePlot


class SimTraci:
    # class CAV:
    #     def __init__(self, id, token, credit):
    #         self.id = id
    #         self.token = token
    #         self.credit = credit

    def __init__(self, **kwargs):
        # simulation option
        self.anime_variable = kwargs["option"]["gui"]
        self.generate_net = kwargs["option"]["generate_net"]
        self.control_option = kwargs["option"]["control_option"]
        self.graph_plot = kwargs["option"]["graph"]
        # network data path
        self.gen_path = kwargs["network"]
        # event data
        self.event = kwargs["event"]
        self.global_context = GlobalContext()
        self.global_context.vehicles = {}
        self.global_context.visibility = kwargs["visibility"]
        # trading option
        self.global_context.trading_option['azure']= kwargs["option"]["azure"]
        self.global_context.trading_option['openai_model'] = kwargs["option"]["openai_model"]
        self.data_trade = kwargs["option"]["trading"]
        # network settings for a random network
        self.network_setting = kwargs["network_setting"]
        # simulation settings
        self.simulation_setting = kwargs["simulation_setting"]
        # sim step initial
        self.sim_step = 0

 
    def __sumo_run(self, **kwargs):
        event = kwargs.get("event", None)
        self.global_context.event = event
        trade_register = kwargs.get("trade", None)
        controlled_signal = kwargs.get("control", None)  # TODO 其他control strategy的开关？是否和trading_option重复了？
        datatrade = DataTrade(controller_1)
        plot = RealTimePlot()  # TODO 增加plot
        file_path = f'./logs/peakend_{self.simulation_setting["peak_end"]}_peakflow_{self.simulation_setting["flow_peak"]}_opflow{self.simulation_setting["flow_off"]}_trade_{self.data_trade}/'
        file_name = f'DelayOverTime_trade'
        is_strategy_changed = False
        
        with open(file_path + file_name + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time', 'Qlength', 'Delay'])

        if not os.path.exists(file_path):
            os.makedirs(file_path)  # 创建目录
        
        while self.sim_step / 10 <= traci.simulation.getEndTime():
        # traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # pdb.set_trace()
            
            self.global_context.step = self.sim_step
            if self.sim_step % 10 == 0:
                print(self.sim_step/10, "s")
                if self.graph_plot:
                    # print(traci.lane.getEdgeID(A0A1_1))
                    q_length = traci.edge.getLastStepHaltingNumber('A0A1') + traci.edge.getLastStepHaltingNumber('B1A1') + traci.edge.getLastStepHaltingNumber('top0A1') + traci.edge.getLastStepHaltingNumber('left1A1')
                    total_delay = _get_total_delay()
                    time = self.sim_step//10
                    # 将变量转换为字符串
                    q_length_str = str(q_length)
                    total_delay_str = str(total_delay)
                    time_str = str(time)
                    variables = [time_str, q_length_str, total_delay_str]

                    plot.update_plot(time, q_length)
                    # 使用 csv 模块写入 CSV 文件
                    with open(file_path + file_name + '.csv', 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(variables)
                if self.data_trade is False:
                    traffic_light_id = 'A1'
                    if (self.sim_step // 10 > 500) & (is_strategy_changed==False) & (self.sim_step // 10 < 600):
                        print('switch signal strategy!!!!!!')
                        SignalControl.original_control(controller_id=traffic_light_id)
                        is_strategy_changed = True          
                    if (self.sim_step // 10 > 600) & (is_strategy_changed==True):                               
                        print('switch back signal strategy!!!!!!')
                        SignalControl.original_control(controller_id=traffic_light_id)
                        is_strategy_changed = False
                
            if (self.data_trade):
                traci_fetch_itv = 100
            # else:
            #     traci_fetch_itv = 500
                if self.sim_step % traci_fetch_itv == 0:  # TODO 这个traci_fetch_itv也可以写到var里面
                    Update_Cars_info(self.global_context)
                    if self.sim_step % traci_fetch_itv == 0:
                        Calc_nearby_accident(self.global_context)
                        Calc_traffic_flow(self.global_context)
                        trade_cnt = datatrade.controller.trade_count
                        traffic_light_id = 'A1'
                        # current_phase = traci.trafficlight.getPhase(traffic_light_id)
                        # # 获取交通灯逻辑的详细信息
                        # phases = traci.trafficlight.getCompleteRedYellowGreenDefinition(traffic_light_id)[0].phases
                        # # 计算总相位数
                        # total_phases = len(phases)
                        #if 交易3次 【无需判断phase】SUMO允许在任何时刻进行切换，但实际的逻辑变更会在当前相位结束后生效。】
                        if trade_cnt > 3:
                            if (self.sim_step // 10 > 500) & (is_strategy_changed==False) & (self.sim_step // 10 < 600):
                                print('switch signal strategy!!!!!!')
                                SignalControl.data_driven_control(controller_id=traffic_light_id)
                                is_strategy_changed = True          
                            if (self.sim_step // 10 > 600) & (is_strategy_changed==True):                               
                                print('switch back signal strategy!!!!!!')
                                SignalControl.original_control(controller_id=traffic_light_id)
                                is_strategy_changed = False
                            # SignalControl.data_driven_control(controller_id=traffic_light_id)
                        else:
                            datatrade.start_trade(self.global_context,file_path)
                        # TODO change_rate: float32 = rate(accident: increase the rate of using p2, non_accident: p1)
                    # signal_control(change_rate)
                        # if (self.sim_step // 10 > 700) & (self.sim_step // 10 < 800):                               
                        #     print('switch back signal strategy!!!!!!')
                        #     SignalControl.original_control(controller_id=traffic_light_id)


                



            # pdb.set_trace()
            if event:
                event.event_loger(self.sim_step)
            if trade_register:
                pass
            
            self.sim_step += 1
        traci.close()
        
        plot.save_plot(file_path=file_path, file_name=file_name)
        sys.stdout.flush()


    # start sumo simulation
    def __sumo_start(self):
        if self.anime_variable:
            sumo_binary = sumolib.checkBinary("sumo-gui")  # animation
        else:
            sumo_binary = sumolib.checkBinary("sumo")  # no animation
        sim_path = (self.gen_path / "example.sumocfg").absolute()
        try:
            traci.start([sumo_binary, "-c", sim_path, "--step-length", "0.1"])
        except UserWarning:
            sys.exit("No simulation data")

    def __sumo_initialize(self) -> Dict:
        obj_dict = dict()
        # pdb.set_trace()
        if self.event:
            event = Event(self.event)
            obj_dict["event"] = event
        # if self.data_trade:
        #     trade = DataTrade()
        #     signal = SignalControl()
        #     obj_dict["trade"] = trade
        #     obj_dict["control"] = signal
        return obj_dict

    # generate sumo configuration files
    def __sumo_generate(self):
        # generate net or not
        if self.generate_net:
            gen_data = GenSumo(
                self.gen_path, self.network_setting, self.simulation_setting
            )
            gen_data.generate_sumo()
        else:
            pass
        # actuated traffic signal on or off
        net_dir = self.gen_path / "network.net.xml"
        if self.control_option:
            os.popen(
                "netconvert "
                '-s "%s" '
                '--o "%s" '
                "--tls.rebuild "
                "--tls.default-type actuated" % (net_dir, net_dir)
            )
        else:
            os.popen(
                "netconvert "
                '-s "%s" '
                '--o "%s" '
                "--tls.rebuild "
                "--tls.default-type static" % (net_dir, net_dir)
            )

    def sim_run(self):
        self.__sumo_generate()
        obj_dict = self.__sumo_initialize()
        # pdb.set_trace()
        self.__sumo_start()
        self.__sumo_run(**obj_dict)
