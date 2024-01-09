from pathlib import Path
import os
import DTM.global_var
from DTM.start_sim import SimTraci


def main():
    gen_dir = Path(__file__).parent
    network_dir = gen_dir / 'data'
    folder = os.path.exists(network_dir)
    if not folder:
        os.mkdir(network_dir)
    #  simulation start
    sim_start = SimTraci(network=network_dir,  # network path
                         option=DTM.global_var.simulation_option,  # simulation option
                         event=DTM.global_var.v_accident,  # accident generate option
                         network_setting=DTM.global_var.network_settings,  # generate network settings
                         simulation_setting=DTM.global_var.simulation_settings,
                         visibility=DTM.global_var.vehicle_visibility,
                         )  # simulation settings
    sim_start.sim_run()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
