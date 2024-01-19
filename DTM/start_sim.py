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
        controlled_signal = kwargs.get("control", None)
        datatrade = DataTrade(controller_1)
        plot = RealTimePlot()  # TODO 增加plot
        
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            # pdb.set_trace()
            self.global_context.step = self.sim_step
            if self.sim_step % 10 == 0:
                print(self.sim_step/10, "s")
            if self.sim_step % 300 == 0:
                Update_Cars_info(self.global_context)
                if self.sim_step % 300 == 0:
                    Calc_nearby_accident(self.global_context)
                    Calc_traffic_flow(self.global_context)
                    
                    # TODO if 交易3次 $ 处于最后phase
                    trade_cnt = datatrade.controller.trade_count
                    if trade_cnt > 3:
                        print('condition meet!!!!!! switch signal strategy')
                        SignalControl.data_driven_control(controller_id='A1')
                    else:
                        datatrade.start_trade(self.global_context)

                    # traci.trafficlight.getPhase(traffic_light_id)
                    # TODO change_rate: float32 = rate(accident: increase the rate of using p2, non_accident: p1)
                    # signal_control(change_rate)
                    # Apply control strategy after data trading and traffic data calculations
                    # if condition_for_data_driven_strategy:  # Define your condition based on the latest data
                    #     data_driven_strategy.apply_strategy()
                    # else:
                    #     basic_strategy.apply_strategy()
                
                    
                    if self.sim_step % 300 == 0:
                        for vid in self.global_context.vehicles.keys():

                            x = self.global_context.vehicles[vid].get_trading_data(
                                self.global_context
                            )
                            if x is not None:
                                print(x)

            # print(self.sim_step)
            # pdb.set_trace()
            if event:
                event.event_loger(self.sim_step)
            if trade_register:
                pass
            if self.graph_plot:
                total_delay = _get_total_delay()
                time_step = self.sim_step
                plot.update_plot(time_step, total_delay)
                # if self.simstep % 200 == 0:
                #     GraphPresent.draw_physic()
                #     self.draw_control()
            self.sim_step += 1
        traci.close()
        plot.save_plot(filename='test')
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
        if self.data_trade:
            trade = DataTrade()
            signal = SignalControl()
            obj_dict["trade"] = trade
            obj_dict["control"] = signal
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
