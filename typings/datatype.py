from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GlobalContext:
    vehicles: Dict[str, any] = None  # 车辆id访问对应的类
    event: any = None  # 通过访问Event里的成员属性例如:accident_position等来得到对应event的信息
    step: int = None  # 当前时间
    visibility: float = None  # 可视距离


@dataclass
class AccidentData:
    accident_id: str
    accident_road_id: str  # 车道id  e.g."A1A0"
    accident_position: List[float]  # 事故的经纬度位置
    time_to_trading_point: str
    distance_to_traing_point: str  # 事故距离当前交易点的直线距离
    accident_severity: str
    traffic_flow: Dict[str, List[int]]  # key: 道路ID  value: 历史观测到的车辆数


@dataclass
class PersonalData:
    road_id: str  # 车辆当前所在位置车道id  e.g."A1A0"
    position: List[float]  # 车辆的经纬度位置


@dataclass
class ControllerPersonalData:
    current_traffic_state: str = None  # 当前交通状态，主要用于 Controller
    predicted_income: float = None  # 预测收入，主要用于 Controller


@dataclass
class TradingData:
    current_token: float
    history_average_price: float
    trading_history: List[Dict[str, any]] = field(default_factory=list)  # 交易历史
    accident_info: Dict[str, any] = None  # 事故信息，主要用于 Vehicle


@dataclass
class TradingHistoryData:
    current_token: float
    history_average_price: float
    vehicle_id: str
    controller_id: str
    proposed_price: float
    is_success: bool
    trading_time: str
    accident_info: Dict[str, any] = None  # 事故信息，主要用于 Vehicle


@dataclass
class Preference:
    trading_purpose: str
    expected_price: float  # current_budget for controller
    cost: float  # 发起交易时, 车辆要花费的货币
    skepticism: bool = None  # 对数据保留怀疑态度，主要用于 Controller


Offer = [
    {
        "name": "propose_offers",
        "description": "propose data trading offer based on the information provided",
        "parameters": {
            "type": "object",
            "properties": {
                "data_description": {
                    "type": "string",
                    "description": "The description of data which would be traded",
                },
                "price": {
                    "type": "number",
                    "description": "the proposed price of the data",  # "12 dollars"
                },
                # "amount": {
                #     "type": "number",
                #     "description": "the amount of traded data",
                # },
                "reason": {
                    "type": "string",
                    "description": "the reason to convince controller to buy the data",
                },
            },
        },
        "required": ["content"],
    }
]


Decision = [
    {
        "name": "offer_dicision",
        "description": "decide whether to take the offer based on the proposed offer context and the information I have",
        "parameters": {
            "type": "object",
            "properties": {
                "decision": {
                    "type": "boolean",
                    "description": "The decision of say yes or no to the offer",
                },
                "reason": {
                    "type": "string",
                    "description": "the reason why make this offer decision",  # "12 dollars"
                },
            },
        },
        "required": ["content"],
    }
]
