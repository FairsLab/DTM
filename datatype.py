from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PersonalData:
    location: List[int] = field(default_factory=list)  # 位置，主要用于 Vehicle
    current_traffic_state: str = None  # 当前交通状态，主要用于 Controller
    predicted_income: float = None  # 预测收入，主要用于 Controller

@dataclass
class TradingData:
    current_token: float
    history_average_price: float
    trading_history: List[Dict[str, any]] = field(default_factory=list)  # 交易历史
    accident_info: Dict[str, any] = None  # 事故信息，主要用于 Vehicle


@dataclass
class Preference:
    trading_purpose: str
    expected_price: float
    cost: float
    skepticism: bool = None  # 对数据保留怀疑态度，主要用于 Controller


@dataclass
class Offer:
    vehicle_id: str
    description: str
    price: float
    amount: int
    reason: str

@dataclass
class Decision:
    controller_id: str
    decision: str  # 例如 'accept' 或 'reject'
    reason: str





