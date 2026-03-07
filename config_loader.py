#!/usr/bin/env python3
"""
配置檔案載入器模組
負責載入和管理診斷、觀察、藥物的配置資料
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

class ConfigLoader:
    """配置檔案載入器"""

    RESOURCE_TYPES = {
        "conditions": {"filename": "conditions.json", "items_key": "conditions", "label": "疾病診斷"},
        "observations": {"filename": "observations.json", "items_key": "observations", "label": "觀察項目"},
        "medications": {"filename": "medications.json", "items_key": "medications", "label": "藥物"},
        "allergies": {"filename": "allergies.json", "items_key": "allergies", "label": "過敏項目"},
    }

    def __init__(self, config_dir: str = "config"):
        """
        初始化配置載入器

        Args:
            config_dir: 配置檔案目錄路徑
        """
        self.config_dir = Path(config_dir)
        self.resources = {}

        # 載入所有配置檔案
        self.load_all_configs()

    def load_json_config(self, filename: str) -> Dict[str, Any]:
        """
        載入 JSON 配置檔案

        Args:
            filename: 檔案名稱

        Returns:
            配置資料字典
        """
        filepath = self.config_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"配置檔案不存在: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"配置檔案格式錯誤 {filepath}: {e}")
        except Exception as e:
            raise RuntimeError(f"載入配置檔案失敗 {filepath}: {e}")

    def _load_resource_config(self, filename: str, items_key: str) -> List[Dict[str, Any]]:
        """
        載入資源配置（通用方法）

        Args:
            filename: 配置檔案名稱
            items_key: 項目在類別資料中的鍵名

        Returns:
            項目列表
        """
        config = self.load_json_config(filename)
        items = []
        for category_key, category_data in config["categories"].items():
            for item in category_data[items_key]:
                item_copy = item.copy()
                item_copy["category"] = category_data["name"]
                item_copy["category_key"] = category_key
                items.append(item_copy)
        return items

    def load_all_configs(self):
        """載入所有配置檔案"""
        try:
            print("📋 載入配置檔案...")
            for rtype, rconfig in self.RESOURCE_TYPES.items():
                self.resources[rtype] = self._load_resource_config(rconfig["filename"], rconfig["items_key"])
                print(f"   ✅ 載入 {len(self.resources[rtype])} 種{rconfig['label']}")
            print("📋 配置檔案載入完成")
        except Exception as e:
            print(f"❌ 載入配置檔案失敗: {e}")
            raise

    def get_items(self, resource_type: str) -> List[Dict[str, Any]]:
        """
        獲取指定資源類型的項目列表

        Args:
            resource_type: 資源類型鍵名（如 "conditions", "observations" 等）

        Returns:
            項目列表
        """
        return self.resources.get(resource_type, [])

    def get_items_by_category(self, resource_type: str, category_key: str) -> List[Dict[str, Any]]:
        """
        根據類別獲取指定資源類型的項目列表

        Args:
            resource_type: 資源類型鍵名
            category_key: 類別鍵值

        Returns:
            該類別的項目列表
        """
        return [item for item in self.get_items(resource_type) if item.get("category_key") == category_key]

    # Backward-compatible accessors
    def get_conditions(self): return self.get_items("conditions")
    def get_observations(self): return self.get_items("observations")
    def get_medications(self): return self.get_items("medications")
    def get_allergies(self): return self.get_items("allergies")
    def get_conditions_by_category(self, ck): return self.get_items_by_category("conditions", ck)
    def get_observations_by_category(self, ck): return self.get_items_by_category("observations", ck)
    def get_medications_by_category(self, ck): return self.get_items_by_category("medications", ck)
    def get_allergies_by_category(self, ck): return self.get_items_by_category("allergies", ck)

    def get_config_info(self) -> Dict[str, Any]:
        """
        獲取配置資訊摘要

        Returns:
            配置資訊字典
        """
        info = {"config_directory": str(self.config_dir)}
        for rtype in self.RESOURCE_TYPES:
            info[f"{rtype}_count"] = len(self.get_items(rtype))
            info[f"available_{rtype}_categories"] = list(set(
                item.get("category_key") for item in self.get_items(rtype)
            ))
        return info

    def reload_configs(self):
        """重新載入所有配置檔案"""
        print("🔄 重新載入配置檔案...")
        self.load_all_configs()

def test_config_loader():
    """測試配置載入器"""
    try:
        loader = ConfigLoader()

        print("\n📊 配置資訊摘要:")
        info = loader.get_config_info()
        for key, value in info.items():
            print(f"   {key}: {value}")

        print("\n🧪 測試類別篩選:")
        test_cases = [
            ("conditions", "cardiovascular", "心血管疾病"),
            ("observations", "vital_signs", "基本生理指標"),
            ("medications", "cardiovascular", "心血管藥物"),
            ("allergies", "drug_allergy", "藥物過敏"),
        ]
        for rtype, category, label in test_cases:
            items = loader.get_items_by_category(rtype, category)
            print(f"   {label}: {len(items)} 種")

        print("\n✅ 配置載入器測試完成")

    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_config_loader()
