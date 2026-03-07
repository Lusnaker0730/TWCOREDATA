#!/usr/bin/env python3
"""
資料模型定義
定義生成配置、日期範圍等資料結構
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any


@dataclass
class DateRangeConfig:
    """各資源類型的日期範圍設定"""
    encounter_date_from: Optional[datetime] = None
    encounter_date_to: Optional[datetime] = None
    condition_date_from: Optional[datetime] = None
    condition_date_to: Optional[datetime] = None
    observation_date_from: Optional[datetime] = None
    observation_date_to: Optional[datetime] = None
    allergy_date_from: Optional[datetime] = None
    allergy_date_to: Optional[datetime] = None

    def get_range(self, resource_type: str):
        """取得指定資源類型的日期範圍 (date_from, date_to)"""
        return (
            getattr(self, f"{resource_type}_date_from", None),
            getattr(self, f"{resource_type}_date_to", None),
        )


@dataclass
class BatchGenerationConfig:
    """批量生成設定"""
    num_patients: int = 2
    num_conditions: int = 2
    num_observations: int = 3
    num_medications: int = 2
    num_encounters: int = 1
    num_allergies: int = 1
    server_choice: str = "none"
    custom_server: str = ""
    dates: DateRangeConfig = field(default_factory=DateRangeConfig)

    def get_count(self, resource_type: str) -> int:
        """取得指定資源類型的生成數量"""
        mapping = {
            "conditions": self.num_conditions,
            "observations": self.num_observations,
            "medications": self.num_medications,
            "encounters": self.num_encounters,
            "allergies": self.num_allergies,
        }
        return mapping.get(resource_type, 0)


@dataclass
class CustomGenerationConfig:
    """自訂生成設定"""
    selected_conditions: List[Any] = field(default_factory=list)
    selected_observations: List[Any] = field(default_factory=list)
    selected_medications: List[Any] = field(default_factory=list)
    selected_allergies: List[Any] = field(default_factory=list)
    num_encounters: int = 1
    server_choice: str = "none"
    custom_server: str = ""
    upload: bool = False
    dates: DateRangeConfig = field(default_factory=DateRangeConfig)

    def get_selected(self, resource_type: str) -> List[Any]:
        """取得指定資源類型的已選項目"""
        attr = f"selected_{resource_type}"
        return getattr(self, attr, [])
