from pathlib import Path
import sys

# 获取当前脚本所在目录的父目录（假设它是项目根目录）
root_dir = Path(__file__).parent.parent.resolve()

# 将项目根目录添加到 sys.path
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# 现在可以进行导入
from typings.datatype import PersonalData, TradingData, Preference, Offer, Decision

from DTM.trading import Vehicle, Controller

# 智能车的个人数据
vehicle_personal_data = PersonalData(
    location=[10, 20]
)

# 智能车的交易数据
vehicle_trading_data = TradingData(
    current_token=50.0,
    history_average_price=10.0,
    accident_info={
        "Accident_Location": "road A",
        "Distance_To_Trading_Point": "50m",
        "Time_To_Trading_Point": "20s",
        "Accident_Severity": "high",
        "Traffic_Flow": "500 veh/h"
    }
)

# 智能车的偏好设置
vehicle_preference = Preference(
    trading_purpose="获得最大化收益",
    expected_price=10.0,
    cost=1.0
)




# 信号控制器的个人数据
controller_personal_data = PersonalData(
    current_traffic_state="中",
    predicted_income=50.0
)

# 信号控制器的交易数据
controller_trading_data = TradingData(
    current_token=200.0,
    history_average_price=10.0,
    trading_history=[{
        "交易时间": "2023-11-09 11:00",
        "description": "事故数据",
        "price": 15.0,
        "交易对象": "veh2000",
        "content": {}
    }]
)

# 信号控制器的偏好设置
controller_preference = Preference(
    trading_purpose="提升交通效率",
    current_budget=15.0,
    skepticism=True
)


# 实例化智能车
vehicle = Vehicle(
    actor_id="Vehicle_2003",
    personal_data=vehicle_personal_data,
    trading_data=vehicle_trading_data,
    preference=vehicle_preference
)


# 实例化信号控制器
controller = Controller(
    actor_id="Controller_1",
    personal_data=controller_personal_data,
    trading_data=controller_trading_data,
    preference=controller_preference
)



