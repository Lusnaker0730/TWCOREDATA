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
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置載入器
        
        Args:
            config_dir: 配置檔案目錄路徑
        """
        self.config_dir = Path(config_dir)
        self.conditions = []
        self.observations = []
        self.medications = []
        
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
    
    def load_conditions_config(self) -> List[Dict[str, Any]]:
        """
        載入疾病診斷配置
        
        Returns:
            疾病列表
        """
        config = self.load_json_config("conditions.json")
        conditions = []
        
        for category_key, category_data in config["categories"].items():
            for condition in category_data["conditions"]:
                # 添加類別資訊
                condition_with_category = condition.copy()
                condition_with_category["category"] = category_data["name"]
                condition_with_category["category_key"] = category_key
                conditions.append(condition_with_category)
        
        return conditions
    
    def load_observations_config(self) -> List[Dict[str, Any]]:
        """
        載入觀察項目配置
        
        Returns:
            觀察項目列表
        """
        config = self.load_json_config("observations.json")
        observations = []
        
        for category_key, category_data in config["categories"].items():
            for observation in category_data["observations"]:
                # 添加類別資訊
                observation_with_category = observation.copy()
                observation_with_category["category"] = category_data["name"]
                observation_with_category["category_key"] = category_key
                observations.append(observation_with_category)
        
        return observations
    
    def load_medications_config(self) -> List[Dict[str, Any]]:
        """
        載入藥物配置
        
        Returns:
            藥物列表
        """
        config = self.load_json_config("medications.json")
        medications = []
        
        for category_key, category_data in config["categories"].items():
            for medication in category_data["medications"]:
                # 添加類別資訊
                medication_with_category = medication.copy()
                medication_with_category["category_key"] = category_key
                medications.append(medication_with_category)
        
        return medications
    
    def load_all_configs(self):
        """載入所有配置檔案"""
        try:
            print("📋 載入配置檔案...")
            
            # 載入疾病配置
            self.conditions = self.load_conditions_config()
            print(f"   ✅ 載入 {len(self.conditions)} 種疾病診斷")
            
            # 載入觀察項目配置
            self.observations = self.load_observations_config()
            print(f"   ✅ 載入 {len(self.observations)} 種觀察項目")
            
            # 載入藥物配置
            self.medications = self.load_medications_config()
            print(f"   ✅ 載入 {len(self.medications)} 種藥物")
            
            print("📋 配置檔案載入完成")
            
        except Exception as e:
            print(f"❌ 載入配置檔案失敗: {e}")
            raise
    
    def get_conditions(self) -> List[Dict[str, Any]]:
        """獲取疾病列表"""
        return self.conditions
    
    def get_observations(self) -> List[Dict[str, Any]]:
        """獲取觀察項目列表"""
        return self.observations
    
    def get_medications(self) -> List[Dict[str, Any]]:
        """獲取藥物列表"""
        return self.medications
    
    def get_conditions_by_category(self, category_key: str) -> List[Dict[str, Any]]:
        """
        根據類別獲取疾病列表
        
        Args:
            category_key: 類別鍵值
            
        Returns:
            該類別的疾病列表
        """
        return [c for c in self.conditions if c.get("category_key") == category_key]
    
    def get_observations_by_category(self, category_key: str) -> List[Dict[str, Any]]:
        """
        根據類別獲取觀察項目列表
        
        Args:
            category_key: 類別鍵值
            
        Returns:
            該類別的觀察項目列表
        """
        return [o for o in self.observations if o.get("category_key") == category_key]
    
    def get_medications_by_category(self, category_key: str) -> List[Dict[str, Any]]:
        """
        根據類別獲取藥物列表
        
        Args:
            category_key: 類別鍵值
            
        Returns:
            該類別的藥物列表
        """
        return [m for m in self.medications if m.get("category_key") == category_key]
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        獲取配置資訊摘要
        
        Returns:
            配置資訊字典
        """
        return {
            "conditions_count": len(self.conditions),
            "observations_count": len(self.observations),
            "medications_count": len(self.medications),
            "config_directory": str(self.config_dir),
            "available_condition_categories": list(set(c.get("category_key") for c in self.conditions)),
            "available_observation_categories": list(set(o.get("category_key") for o in self.observations)),
            "available_medication_categories": list(set(m.get("category_key") for m in self.medications))
        }
    
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
        cardiovascular_conditions = loader.get_conditions_by_category("cardiovascular")
        print(f"   心血管疾病: {len(cardiovascular_conditions)} 種")
        
        vital_signs = loader.get_observations_by_category("vital_signs")
        print(f"   基本生理指標: {len(vital_signs)} 種")
        
        cardiovascular_meds = loader.get_medications_by_category("cardiovascular")
        print(f"   心血管藥物: {len(cardiovascular_meds)} 種")
        
        print("\n✅ 配置載入器測試完成")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    test_config_loader()
