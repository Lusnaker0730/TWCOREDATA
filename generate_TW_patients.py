#!/usr/bin/env python3
"""
台灣 FHIR 病人資料完整生成器 - 修復版
修復了 Condition 和 Observation 上傳失敗的问题
"""

import json
import requests
import uuid
import random
from datetime import datetime, timedelta
from html import escape as html_escape
from pathlib import Path
import time
from config_loader import ConfigLoader

class TWFHIRGeneratorFixed:
    # 門診機率較高的就診類型權重列表
    ENCOUNTER_TYPE_WEIGHTS = ["outpatient", "outpatient", "outpatient", "emergency", "inpatient"]

    RESOURCE_LIST_FIELDS = {
        "conditions": ["code", "display", "category", "system"],
        "observations": ["code", "display", "category", "unit", "min_val", "max_val"],
        "medications": ["code", "display", "category", "dosage_form", "strength", "atc"],
        "allergies": ["code", "display", "category", "type", "criticality"],
    }

    def __init__(self):
        """
        初始化台灣 FHIR 資料生成器 - 修復版
        """
        # 載入配置檔案
        self.config_loader = ConfigLoader()
        self.resources = {
            "conditions": self.config_loader.get_items("conditions"),
            "observations": self.config_loader.get_items("observations"),
            "medications": self.config_loader.get_items("medications"),
            "allergies": self.config_loader.get_items("allergies"),
        }

        # 台灣常見姓氏和名字
        self.surnames = [
            "陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊",
            "許", "鄭", "謝", "洪", "郭", "邱", "曾", "廖", "賴", "徐",
            "周", "葉", "蘇", "莊", "盧", "梁", "游", "羅", "高", "蕭"
        ]
        
        self.male_names = [
            "志明", "建宏", "俊傑", "文華", "嘉明", "志偉", "建華", "俊宏",
            "文傑", "嘉偉", "志華", "建明", "俊偉", "文宏", "嘉華", "宗翰",
            "承恩", "宇軒", "子軒", "浩宇", "俊翰", "宇豪", "承翰", "浩翰"
        ]
        
        self.female_names = [
            "美玲", "淑芬", "怡君", "雅婷", "佳蓉", "淑娟", "美惠", "雅芳",
            "佳玲", "怡萱", "淑貞", "美珍", "雅慧", "佳芬", "怡蓉", "雅雯",
            "佳穎", "怡萍", "淑華", "美玉", "雅玲", "佳慧", "怡靜", "子涵"
        ]
        
        self.cities = [
            "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
            "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣",
            "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣"
        ]

    @property
    def conditions(self): return self.resources["conditions"]
    @property
    def observations(self): return self.resources["observations"]
    @property
    def medications(self): return self.resources["medications"]
    @property
    def allergies(self): return self.resources["allergies"]

    def generate_taiwan_id(self, gender="random"):
        """生成台灣身份证号"""
        area_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                     'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        
        first_char = random.choice(area_codes)
        
        if gender == "random":
            gender_code = random.choice([1, 2])
        elif gender == "male":
            gender_code = 1
        else:
            gender_code = 2
        
        numbers = [str(random.randint(0, 9)) for _ in range(7)]
        check_digit = random.randint(0, 9)
        
        return first_char + str(gender_code) + ''.join(numbers) + str(check_digit)

    def generate_phone_number(self, phone_type="mobile"):
        """生成台灣电话号碼"""
        if phone_type == "mobile":
            prefix = "09"
            middle = str(random.randint(10, 99))
            suffix = f"{random.randint(100, 999)}-{random.randint(100, 999)}"
            return f"{prefix}{middle}-{suffix}"
        else:
            area_codes = ["02", "03", "04", "05", "06", "07"]
            area = random.choice(area_codes)
            number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            return f"{area}-{number}"

    def generate_address(self):
        """生成台灣地址"""
        city = random.choice(self.cities)
        district = f"{random.choice(['中', '東', '西', '南', '北'])}區"
        street_names = ["中山路", "中正路", "民生路", "民權路", "忠孝路", "仁愛路", "信義路", "和平路"]
        street = random.choice(street_names)
        section = random.randint(1, 5)
        number = random.randint(1, 999)
        floor = random.randint(1, 20)
        
        full_address = f"{city}{district}{street}{section}段{number}號{floor}樓"
        postal_code = str(random.randint(100, 999))
        
        return {
            "city": city,
            "district": district,
            "postal_code": postal_code,
            "full_address": full_address
        }

    def generate_patient(self):
        """生成符合 TWCORE 规范的 Patient 資源"""
        gender = random.choice(["male", "female"])
        surname = random.choice(self.surnames)
        
        if gender == "male":
            given_name = random.choice(self.male_names)
        else:
            given_name = random.choice(self.female_names)
        
        full_name = surname + given_name
        taiwan_id = self.generate_taiwan_id(gender)
        
        # 生成出生日期（18-80岁）
        today = datetime.now()
        birth_date = today - timedelta(days=random.randint(18 * 365, 80 * 365))
        
        address_info = self.generate_address()
        mobile_phone = self.generate_phone_number("mobile")
        home_phone = self.generate_phone_number("home")
        
        patient_id = str(uuid.uuid4())
        
        # 创建 narrative 文本
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>病人信息</strong></p>
            <ul>
                <li>姓名: {full_name}</li>
                <li>性别: {'男性' if gender == 'male' else '女性'}</li>
                <li>出生日期: {birth_date.strftime('%Y-%m-%d')}</li>
                <li>身份证号: {taiwan_id}</li>
                <li>地址: {address_info['full_address']}</li>
            </ul>
        </div>
        """.strip()
        
        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "code": "NI",
                                "display": "National unique individual identifier"
                            }
                        ]
                    },
                    "system": "http://www.moi.gov.tw/",
                    "value": taiwan_id
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "family": surname,
                    "given": [given_name],
                    "text": full_name
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": mobile_phone,
                    "use": "mobile"
                },
                {
                    "system": "phone",
                    "value": home_phone,
                    "use": "home"
                },
                {
                    "system": "email",
                    "value": f"{given_name.lower()}.{surname.lower()}@example.tw"
                }
            ],
            "gender": gender,
            "birthDate": birth_date.strftime("%Y-%m-%d"),
            "address": [
                {
                    "use": "home",
                    "type": "both",
                    "text": address_info["full_address"],
                    "city": address_info["city"],
                    "district": address_info["district"],
                    "postalCode": address_info["postal_code"],
                    "country": "TW"
                }
            ],
            "maritalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": random.choice(["M", "S", "D", "W"]),
                        "display": random.choice(["Married", "Never Married", "Divorced", "Widowed"])
                    }
                ]
            },
            "communication": [
                {
                    "language": {
                        "coding": [
                            {
                                "system": "urn:ietf:bcp:47",
                                "code": "zh-TW",
                                "display": "Chinese Taiwan, Province of China"
                            }
                        ]
                    },
                    "preferred": True
                }
            ]
        }
        
        return patient

    @staticmethod
    def _random_date_in_range(date_from=None, date_to=None, default_days_back=180):
        """在指定日期範圍內生成隨機日期，若未指定則使用預設天數回推"""
        if date_from and date_to:
            delta = (date_to - date_from).days
            if delta <= 0:
                return date_from
            return date_from + timedelta(days=random.randint(0, delta))
        elif date_from:
            delta = (datetime.now() - date_from).days
            if delta <= 0:
                return date_from
            return date_from + timedelta(days=random.randint(0, delta))
        elif date_to:
            return date_to - timedelta(days=random.randint(0, default_days_back))
        else:
            return datetime.now() - timedelta(days=random.randint(1, default_days_back))

    def generate_encounter(self, patient_id, patient_name, encounter_type="outpatient", date_from=None, date_to=None):
        """
        生成就診記錄 (Encounter) 資源

        Args:
            patient_id: 病人ID
            patient_name: 病人姓名
            encounter_type: 就診類型 ('outpatient': 門診, 'inpatient': 住院, 'emergency': 急診)
            date_from: 就診日期範圍起始 (datetime, 可選)
            date_to: 就診日期範圍結束 (datetime, 可選)

        Returns:
            Encounter FHIR 資源
        """
        encounter_id = str(uuid.uuid4())

        # 定義就診類型的映射
        encounter_types = {
            "outpatient": {
                "code": "AMB",
                "display": "門診",
                "display_en": "Ambulatory"
            },
            "inpatient": {
                "code": "IMP",
                "display": "住院",
                "display_en": "Inpatient"
            },
            "emergency": {
                "code": "EMER",
                "display": "急診",
                "display_en": "Emergency"
            }
        }

        encounter_info = encounter_types.get(encounter_type, encounter_types["outpatient"])

        # 生成就診時間
        visit_date = self._random_date_in_range(date_from, date_to, default_days_back=180)
        
        # 根據就診類型設定就診時長
        if encounter_type == "outpatient":
            duration_minutes = random.randint(15, 60)  # 門診：15-60分鐘
        elif encounter_type == "emergency":
            duration_minutes = random.randint(60, 240)  # 急診：1-4小時
        else:  # inpatient
            duration_minutes = random.randint(1440, 10080)  # 住院：1-7天
        
        end_date = visit_date + timedelta(minutes=duration_minutes)
        
        # 台灣時區
        tz_offset = "+08:00"
        
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>就診資訊</strong></p>
            <ul>
                <li>病人: {patient_name}</li>
                <li>就診類型: {encounter_info['display']}</li>
                <li>就診日期: {visit_date.strftime('%Y-%m-%d %H:%M')}</li>
                <li>結束時間: {end_date.strftime('%Y-%m-%d %H:%M')}</li>
                <li>狀態: 已完成</li>
            </ul>
        </div>
        """.strip()
        
        encounter = {
            "resourceType": "Encounter",
            "id": encounter_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": encounter_info["code"],
                "display": encounter_info["display_en"]
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "185349003" if encounter_type == "outpatient" else "32485007",
                            "display": encounter_info["display"]
                        }
                    ],
                    "text": encounter_info["display"]
                }
            ],
            "subject": {
                "reference": f"Patient/{patient_id}",
                "display": patient_name
            },
            "period": {
                "start": visit_date.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}"),
                "end": end_date.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")
            },
            "reasonCode": [
                {
                    "text": "一般就診" if encounter_type == "outpatient" else "住院治療" if encounter_type == "inpatient" else "急診就醫"
                }
            ]
        }
        
        return encounter

    def generate_condition(self, patient_id, patient_name, date_from=None, date_to=None):
        """隨機選取疾病並生成 Condition 資源"""
        condition_info = random.choice(self.conditions)
        return self.generate_condition_with_info(patient_id, patient_name, condition_info, date_from, date_to)

    def generate_condition_with_info(self, patient_id, patient_name, condition_info, date_from=None, date_to=None):
        """使用指定的疾病資訊生成 Condition 資源"""
        condition_id = str(uuid.uuid4())

        # 生成發病日期
        onset_date = self._random_date_in_range(date_from, date_to, default_days_back=730)
        
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>疾病資訊</strong></p>
            <ul>
                <li>病人: {patient_name}</li>
                <li>疾病: {condition_info['display']}</li>
                <li>發病日期: {onset_date.strftime('%Y-%m-%d')}</li>
                <li>狀態: 活躍</li>
            </ul>
        </div>
        """.strip()
        
        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }
                ]
            },
            "code": {
                "coding": [
                    {
                        "system": condition_info["system"],
                        "code": condition_info["code"],
                        "display": condition_info["display"]
                    }
                ],
                "text": condition_info["display"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "onsetDateTime": onset_date.strftime("%Y-%m-%d"),
            "recordedDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        return condition

    def generate_observation(self, patient_id, patient_name, date_from=None, date_to=None):
        """隨機選取觀察項目並生成 Observation 資源"""
        obs_info = random.choice(self.observations)
        return self.generate_observation_with_info(patient_id, patient_name, obs_info, date_from, date_to)

    def generate_observation_with_info(self, patient_id, patient_name, obs_info, date_from=None, date_to=None):
        """使用指定的觀察信息生成 Observation 資源"""
        observation_id = str(uuid.uuid4())

        # 生成隨機值
        if isinstance(obs_info["min_val"], float) or isinstance(obs_info["max_val"], float):
            if obs_info["code"] == "8310-5":  # 體溫
                value = round(random.uniform(obs_info["min_val"], obs_info["max_val"]), 1)
            else:
                value = round(random.uniform(obs_info["min_val"], obs_info["max_val"]), 2)
        else:
            value = random.randint(obs_info["min_val"], obs_info["max_val"])

        # 生成觀察日期
        observation_date = self._random_date_in_range(date_from, date_to, default_days_back=30)
        
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>觀察記錄</strong></p>
            <ul>
                <li>病人: {patient_name}</li>
                <li>項目: {obs_info['display']}</li>
                <li>數值: {value} {obs_info['unit']}</li>
                <li>觀察日期: {observation_date.strftime('%Y-%m-%d')}</li>
            </ul>
        </div>
        """.strip()
        
        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "status": "final",
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": obs_info["code"],
                        "display": obs_info["display"]
                    }
                ],
                "text": obs_info["display"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": observation_date.strftime("%Y-%m-%d"),
            "valueQuantity": {
                "value": value,
                "unit": obs_info["unit"],
                "system": "http://unitsofmeasure.org",
                "code": obs_info["ucum_code"]  # 使用正确的 UCUM 代碼
            }
        }
        
        return observation

    def generate_medication(self, patient_id, patient_name):
        """隨機選取藥物並生成 Medication 資源"""
        med_info = random.choice(self.medications)
        return self.generate_medication_with_info(patient_id, patient_name, med_info)

    def generate_medication_with_info(self, patient_id, patient_name, med_info):
        """使用指定的藥物資訊生成 Medication 資源"""
        medication_id = str(uuid.uuid4())
        
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>藥物資訊</strong></p>
            <ul>
                <li>藥物名稱: {med_info['display']}</li>
                <li>類別: {med_info['category']}</li>
                <li>劑型: {med_info['dosage_form']}</li>
                <li>強度: {med_info['strength']}</li>
                <li>ATC代碼: {med_info['atc']}</li>
            </ul>
        </div>
        """.strip()
        
        medication = {
            "resourceType": "Medication",
            "id": medication_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "code": {
                "coding": [
                    {
                        "system": med_info["system"],
                        "code": med_info["code"],
                        "display": med_info["display"]
                    }
                ],
                "text": med_info["display"]
            },
            "status": "active",
            "form": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": self._get_dosage_form_code(med_info["dosage_form"]),
                        "display": self._get_dosage_form_display(med_info["dosage_form"])
                    }
                ],
                "text": self._get_dosage_form_display(med_info["dosage_form"])
            }
        }
        
        return medication

    def generate_medication_request(self, patient_id, patient_name, medication_id, medication_display):
        """生成 MedicationRequest 資源"""
        med_request_id = str(uuid.uuid4())
        
        # 隨機生成處方日期（過去30天內）
        authored_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # 隨機生成用藥指示
        dosage_instructions = [
            "每日一次，飯後服用",
            "每日兩次，早晚飯後服用",
            "每日三次，飯前服用",
            "每日四次，每6小時服用一次",
            "需要時服用，每日不超過4次",
            "睡前服用",
            "每週一次"
        ]
        
        frequency_codes = {
            "每日一次，飯後服用": {"frequency": 1, "period": 1, "periodUnit": "d"},
            "每日兩次，早晚飯後服用": {"frequency": 2, "period": 1, "periodUnit": "d"},
            "每日三次，飯前服用": {"frequency": 3, "period": 1, "periodUnit": "d"},
            "每日四次，每6小時服用一次": {"frequency": 4, "period": 1, "periodUnit": "d"},
            "需要時服用，每日不超過4次": {"frequency": 1, "period": 1, "periodUnit": "d"},
            "睡前服用": {"frequency": 1, "period": 1, "periodUnit": "d"},
            "每週一次": {"frequency": 1, "period": 1, "periodUnit": "wk"}
        }
        
        selected_instruction = random.choice(dosage_instructions)
        frequency_info = frequency_codes[selected_instruction]
        
        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>處方資訊</strong></p>
            <ul>
                <li>病人: {patient_name}</li>
                <li>藥物: {medication_display}</li>
                <li>用法: {selected_instruction}</li>
                <li>處方日期: {authored_date.strftime('%Y-%m-%d')}</li>
                <li>狀態: 有效</li>
            </ul>
        </div>
        """.strip()
        
        medication_request = {
            "resourceType": "MedicationRequest",
            "id": med_request_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "status": "active",
            "intent": "order",
            "medicationReference": {
                "reference": f"Medication/{medication_id}",
                "display": medication_display
            },
            "subject": {
                "reference": f"Patient/{patient_id}",
                "display": patient_name
            },
            "authoredOn": authored_date.strftime("%Y-%m-%d"),
            "dosageInstruction": [
                {
                    "text": selected_instruction,
                    "timing": {
                        "repeat": {
                            "frequency": frequency_info["frequency"],
                            "period": frequency_info["period"],
                            "periodUnit": frequency_info["periodUnit"]
                        }
                    }
                }
            ]
        }
        
        return medication_request

    def _get_dosage_form_code(self, dosage_form):
        """獲取劑型的 SNOMED CT 代碼"""
        form_codes = {
            "tablet": "385055001",
            "capsule": "385049006", 
            "cream": "385101003",
            "inhaler": "420317006",
            "eye_drops": "385023001"
        }
        return form_codes.get(dosage_form, "421026006")  # 預設為 oral dose form

    def _get_dosage_form_display(self, dosage_form):
        """獲取劑型的顯示名稱"""
        form_displays = {
            "tablet": "Tablet",
            "capsule": "Capsule", 
            "cream": "Cream",
            "inhaler": "Inhaler",
            "eye_drops": "Eye drops"
        }
        return form_displays.get(dosage_form, "Oral dose form")

    def _extract_strength_value(self, strength):
        """從強度字串中提取數值"""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', strength)
        return float(match.group(1)) if match else 1.0

    def _extract_strength_unit(self, strength):
        """從強度字串中提取單位"""
        import re
        # 移除數字，保留單位
        unit = re.sub(r'\d+(?:\.\d+)?', '', strength).strip()
        return unit if unit else "mg"

    def generate_allergy(self, patient_id, patient_name, date_from=None, date_to=None):
        """隨機選取過敏項目並生成 AllergyIntolerance 資源"""
        allergy_info = random.choice(self.allergies)
        return self.generate_allergy_with_info(patient_id, patient_name, allergy_info, date_from, date_to)

    def generate_allergy_with_info(self, patient_id, patient_name, allergy_info, date_from=None, date_to=None):
        """使用指定的過敏資訊生成 AllergyIntolerance 資源"""
        allergy_id = str(uuid.uuid4())

        # 生成記錄日期
        recorded_date = self._random_date_in_range(date_from, date_to, default_days_back=730)

        # 過敏類型映射
        allergy_type_map = {
            "medication": {"code": "medication", "display": "Medication"},
            "food": {"code": "food", "display": "Food"},
            "environment": {"code": "environment", "display": "Environment"},
        }
        allergy_type = allergy_type_map.get(allergy_info.get("type", "medication"), allergy_type_map["medication"])

        # 過敏反應類型
        reaction_manifestations = [
            {"code": "39579001", "display": "Anaphylaxis"},
            {"code": "271807003", "display": "Eruption of skin"},
            {"code": "267036007", "display": "Dyspnea"},
            {"code": "247472004", "display": "Urticaria"},
            {"code": "878820003", "display": "Rhinitis"},
            {"code": "422587007", "display": "Nausea"},
            {"code": "404640003", "display": "Dizziness"},
            {"code": "418290006", "display": "Itching"},
        ]
        manifestation = random.choice(reaction_manifestations)

        # 嚴重程度
        severity_options = ["mild", "moderate", "severe"]
        severity = random.choice(severity_options)

        narrative_text = f"""
        <div xmlns="http://www.w3.org/1999/xhtml">
            <p><strong>過敏資訊</strong></p>
            <ul>
                <li>病人: {html_escape(patient_name)}</li>
                <li>過敏原: {html_escape(allergy_info['display'])}</li>
                <li>類型: {html_escape(allergy_type['display'])}</li>
                <li>嚴重程度: {html_escape(severity)}</li>
                <li>記錄日期: {recorded_date.strftime('%Y-%m-%d')}</li>
            </ul>
        </div>
        """.strip()

        allergy = {
            "resourceType": "AllergyIntolerance",
            "id": allergy_id,
            "text": {
                "status": "generated",
                "div": narrative_text
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                        "display": "Active"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }
                ]
            },
            "type": "allergy",
            "category": [allergy_type["code"]],
            "criticality": allergy_info.get("criticality", "low"),
            "code": {
                "coding": [
                    {
                        "system": allergy_info["system"],
                        "code": allergy_info["code"],
                        "display": allergy_info["display"]
                    }
                ],
                "text": allergy_info["display"]
            },
            "patient": {
                "reference": f"Patient/{patient_id}"
            },
            "recordedDate": recorded_date.strftime("%Y-%m-%d"),
            "reaction": [
                {
                    "manifestation": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": manifestation["code"],
                                    "display": manifestation["display"]
                                }
                            ]
                        }
                    ],
                    "severity": severity
                }
            ]
        }

        return allergy

    def generate_complete_patient_data(self, num_conditions=2, num_observations=3, num_medications=2, num_allergies=1, num_encounters=1,
                                       encounter_date_from=None, encounter_date_to=None,
                                       condition_date_from=None, condition_date_to=None,
                                       observation_date_from=None, observation_date_to=None,
                                       allergy_date_from=None, allergy_date_to=None):
        """
        生成一個完整的病人資料（包含 Patient、Encounter、Condition、Observation、Medication、MedicationRequest、AllergyIntolerance）- 確保不重复

        可選時間綁定參數（datetime 或 None）：
            encounter_date_from / encounter_date_to: 就診記錄日期範圍
            condition_date_from / condition_date_to: 疾病發病日期範圍
            observation_date_from / observation_date_to: 觀察記錄日期範圍
            allergy_date_from / allergy_date_to: 過敏記錄日期範圍
        """
        # 生成 Patient
        patient = self.generate_patient()
        patient_id = patient["id"]
        patient_name = patient["name"][0]["text"]

        # 生成 Encounters (就診記錄)
        encounters = []
        if num_encounters > 0:
            encounter_types = self.ENCOUNTER_TYPE_WEIGHTS
            for _ in range(num_encounters):
                encounter_type = random.choice(encounter_types)
                encounter = self.generate_encounter(patient_id, patient_name, encounter_type,
                                                    date_from=encounter_date_from, date_to=encounter_date_to)
                encounters.append(encounter)

        # 生成不重複的 Conditions
        conditions = []
        if num_conditions > 0:
            if num_conditions > len(self.conditions):
                print(f"⚠️  警告：要求生成 {num_conditions} 個疾病，但只有 {len(self.conditions)} 種疾病類型，將生成全部")
                num_conditions = len(self.conditions)

            selected_conditions = random.sample(self.conditions, num_conditions)
            for condition_info in selected_conditions:
                condition = self.generate_condition_with_info(patient_id, patient_name, condition_info,
                                                             date_from=condition_date_from, date_to=condition_date_to)
                conditions.append(condition)

        # 生成不重複的 Observations
        observations = []
        if num_observations > 0:
            if num_observations > len(self.observations):
                print(f"⚠️  警告：要求生成 {num_observations} 個觀察，但只有 {len(self.observations)} 種觀察类型，將生成全部")
                num_observations = len(self.observations)

            selected_observations = random.sample(self.observations, num_observations)
            for obs_info in selected_observations:
                observation = self.generate_observation_with_info(patient_id, patient_name, obs_info,
                                                                 date_from=observation_date_from, date_to=observation_date_to)
                observations.append(observation)
        
        # 生成不重複的 Medications 和 MedicationRequests
        medications = []
        medication_requests = []
        if num_medications > 0:
            if num_medications > len(self.medications):
                print(f"⚠️  警告：要求生成 {num_medications} 個藥物，但只有 {len(self.medications)} 種藥物類型，將生成全部")
                num_medications = len(self.medications)
            
            # 隨機選擇不重複的藥物類型
            selected_medications = random.sample(self.medications, num_medications)
            for med_info in selected_medications:
                medication = self.generate_medication_with_info(patient_id, patient_name, med_info)
                medications.append(medication)
                
                # 為每個藥物生成對應的處方
                medication_request = self.generate_medication_request(
                    patient_id, patient_name, medication["id"], medication["code"]["text"]
                )
                medication_requests.append(medication_request)

        # 生成不重複的 Allergies
        allergies = []
        if num_allergies > 0:
            if num_allergies > len(self.allergies):
                print(f"⚠️  警告：要求生成 {num_allergies} 個過敏，但只有 {len(self.allergies)} 種過敏類型，將生成全部")
                num_allergies = len(self.allergies)

            selected_allergies = random.sample(self.allergies, num_allergies)
            for allergy_info in selected_allergies:
                allergy = self.generate_allergy_with_info(patient_id, patient_name, allergy_info,
                                                          date_from=allergy_date_from, date_to=allergy_date_to)
                allergies.append(allergy)

        return {
            "patient": patient,
            "encounters": encounters,
            "conditions": conditions,
            "observations": observations,
            "medications": medications,
            "medication_requests": medication_requests,
            "allergies": allergies
        }

    def generate_custom_patient_data(self, selected_conditions=None, selected_observations=None, selected_medications=None, selected_allergies=None, num_encounters=1,
                                      encounter_date_from=None, encounter_date_to=None,
                                      condition_date_from=None, condition_date_to=None,
                                      observation_date_from=None, observation_date_to=None,
                                      allergy_date_from=None, allergy_date_to=None):
        """
        生成自定義的單一病人資料

        Args:
            selected_conditions: 指定的疾病列表 (可以是索引或疾病代碼)
            selected_observations: 指定的觀察項目列表 (可以是索引或觀察代碼)
            selected_medications: 指定的藥物列表 (可以是索引或藥物代碼)
            selected_allergies: 指定的過敏項目列表 (可以是索引或過敏代碼)
            num_encounters: 要生成的就診記錄數量 (預設1)
            encounter_date_from / encounter_date_to: 就診記錄日期範圍 (datetime, 可選)
            condition_date_from / condition_date_to: 疾病發病日期範圍 (datetime, 可選)
            observation_date_from / observation_date_to: 觀察記錄日期範圍 (datetime, 可選)
            allergy_date_from / allergy_date_to: 過敏記錄日期範圍 (datetime, 可選)

        Returns:
            完整的病人資料字典
        """
        # 生成 Patient
        patient = self.generate_patient()
        patient_id = patient["id"]
        patient_name = patient["name"][0]["text"]
        
        # 生成 Encounters (就診記錄)
        encounters = []
        if num_encounters > 0:
            encounter_types = self.ENCOUNTER_TYPE_WEIGHTS  # 門診機率較高
            for _ in range(num_encounters):
                encounter_type = random.choice(encounter_types)
                encounter = self.generate_encounter(patient_id, patient_name, encounter_type,
                                                    date_from=encounter_date_from, date_to=encounter_date_to)
                encounters.append(encounter)

        # 處理指定的 Conditions
        conditions = []
        for condition_info in self._resolve_items(selected_conditions, "conditions"):
            conditions.append(self.generate_condition_with_info(patient_id, patient_name, condition_info,
                                                                date_from=condition_date_from, date_to=condition_date_to))

        # 處理指定的 Observations
        observations = []
        for obs_info in self._resolve_items(selected_observations, "observations"):
            observations.append(self.generate_observation_with_info(patient_id, patient_name, obs_info,
                                                                    date_from=observation_date_from, date_to=observation_date_to))

        # 處理指定的 Medications 和 MedicationRequests
        medications = []
        medication_requests = []
        for med_info in self._resolve_items(selected_medications, "medications"):
            medication = self.generate_medication_with_info(patient_id, patient_name, med_info)
            medications.append(medication)

            # 為每個藥物生成對應的處方
            medication_request = self.generate_medication_request(
                patient_id, patient_name, medication["id"], medication["code"]["text"]
            )
            medication_requests.append(medication_request)

        # 處理指定的 Allergies
        allergies = []
        for allergy_info in self._resolve_items(selected_allergies, "allergies"):
            allergies.append(self.generate_allergy_with_info(patient_id, patient_name, allergy_info,
                                                             date_from=allergy_date_from, date_to=allergy_date_to))

        return {
            "patient": patient,
            "encounters": encounters,
            "conditions": conditions,
            "observations": observations,
            "medications": medications,
            "medication_requests": medication_requests,
            "allergies": allergies
        }

    def _find_item_by_code(self, resource_type, code):
        """根據代碼查找項目"""
        for item in self.resources[resource_type]:
            if item.get("code") == code:
                return item
        return None

    def _find_condition_by_code(self, code): return self._find_item_by_code("conditions", code)
    def _find_observation_by_code(self, code): return self._find_item_by_code("observations", code)
    def _find_medication_by_code(self, code): return self._find_item_by_code("medications", code)
    def _find_allergy_by_code(self, code): return self._find_item_by_code("allergies", code)

    def _resolve_items(self, selected, resource_type):
        """將 int(索引)/str(代碼) 列表解析為配置項目列表"""
        resolved = []
        items_list = self.resources.get(resource_type, [])
        for item in (selected or []):
            info = None
            if isinstance(item, int):
                if 0 <= item < len(items_list):
                    info = items_list[item]
            elif isinstance(item, str):
                info = self._find_item_by_code(resource_type, item)
            if info:
                resolved.append(info)
        return resolved

    def list_available_items(self, resource_type, category=None, limit=None):
        """列出可用的項目"""
        items = self.resources.get(resource_type, [])
        if category:
            items = [item for item in items if item.get("category_key") == category or item.get("category") == category]
        if limit:
            items = items[:limit]
        fields = self.RESOURCE_LIST_FIELDS.get(resource_type, ["code", "display", "category"])
        return [
            {"index": i, **{f: item.get(f, None) for f in fields}}
            for i, item in enumerate(items)
        ]

    def list_available_conditions(self, **kw): return self.list_available_items("conditions", **kw)
    def list_available_observations(self, **kw): return self.list_available_items("observations", **kw)
    def list_available_medications(self, **kw): return self.list_available_items("medications", **kw)
    def list_available_allergies(self, **kw): return self.list_available_items("allergies", **kw)

    def get_categories(self):
        """獲取所有可用的類別"""
        return {
            rtype: sorted(set(item.get("category", "未分類") for item in items))
            for rtype, items in self.resources.items()
        }

    def search_items(self, query, item_type="all"):
        """
        搜尋項目

        Args:
            query: 搜尋關鍵字
            item_type: 項目類型 ("conditions", "observations", "medications", "allergies", "all")

        Returns:
            搜尋結果
        """
        query = query.lower()
        results = {}
        for rtype, items in self.resources.items():
            if item_type not in [rtype, "all"]:
                results[rtype] = []
                continue
            fields = self.RESOURCE_LIST_FIELDS.get(rtype, ["code", "display", "category"])
            results[rtype] = [
                {"index": i, **{f: item.get(f, None) for f in fields}}
                for i, item in enumerate(items)
                if (query in item.get("display", "").lower() or
                    query in item.get("code", "").lower() or
                    query in item.get("category", "").lower())
            ]
        return results

    def upload_resource_to_server(self, resource, server_url):
        """上傳单個資源到 FHIR 伺服器"""
        resource_type = resource["resourceType"]
        url = f"{server_url}/{resource_type}"
        
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        
        try:
            response = requests.post(url, json=resource, headers=headers, timeout=60)  # 增加超時時間到60秒
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                server_id = response_data.get('id', 'unknown')
                return True, server_id
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, str(e)

    def upload_patient_data_to_server(self, patient_data, server_url):
        """上傳完整的病人資料到伺服器"""
        results = {
            "patient": None,
            "encounters": [],
            "conditions": [],
            "observations": [],
            "medications": [],
            "medication_requests": [],
            "allergies": [],
            "errors": []
        }
        
        # 上傳 Patient
        print(f"📤 上傳 Patient: {patient_data['patient']['name'][0]['text']}")
        success, result = self.upload_resource_to_server(patient_data['patient'], server_url)
        
        if success:
            results["patient"] = result
            print(f"   ✅ Patient 上傳成功，ID: {result}")
            
            # 更新 Patient ID 引用
            new_patient_id = result

            UPLOAD_CONFIG = [
                {"key": "encounters", "ref_field": "subject", "display_path": lambda r: r['class']['display'], "label": "Encounter"},
                {"key": "conditions", "ref_field": "subject", "display_path": lambda r: r['code']['text'], "label": "Condition"},
                {"key": "allergies", "ref_field": "patient", "display_path": lambda r: r['code']['text'], "label": "AllergyIntolerance"},
                {"key": "observations", "ref_field": "subject", "display_path": lambda r: r['code']['text'], "label": "Observation"},
                {"key": "medications", "ref_field": None, "display_path": lambda r: r['code']['text'], "label": "Medication"},
            ]

            for config in UPLOAD_CONFIG:
                key = config["key"]
                if key not in patient_data:
                    continue
                for i, resource in enumerate(patient_data[key]):
                    if config["ref_field"]:
                        resource[config["ref_field"]]['reference'] = f"Patient/{new_patient_id}"
                    display = config["display_path"](resource)
                    print(f"📤 上傳 {config['label']} {i+1}: {display}")

                    success, result = self.upload_resource_to_server(resource, server_url)
                    if success:
                        results[key].append(result)
                        print(f"   ✅ {config['label']} 上傳成功，ID: {result}")
                    else:
                        results["errors"].append(f"{config['label']} {i+1}: {result}")
                        print(f"   ❌ {config['label']} 上傳失敗: {result}")
                    time.sleep(0.5)

            # 上傳 MedicationRequests (特殊處理：需要更新 Medication 引用)
            if 'medication_requests' in patient_data:
                for i, med_request in enumerate(patient_data['medication_requests']):
                    # 更新 Patient 和 Medication 的引用
                    med_request['subject']['reference'] = f"Patient/{new_patient_id}"
                    if i < len(results["medications"]):
                        med_request['medicationReference']['reference'] = f"Medication/{results['medications'][i]}"

                    print(f"📤 上傳 MedicationRequest {i+1}: {med_request['medicationReference']['display']}")

                    success, result = self.upload_resource_to_server(med_request, server_url)
                    if success:
                        results["medication_requests"].append(result)
                        print(f"   ✅ MedicationRequest 上傳成功，ID: {result}")
                    else:
                        results["errors"].append(f"MedicationRequest {i+1}: {result}")
                        print(f"   ❌ MedicationRequest 上傳失敗: {result}")

                time.sleep(0.5)
        else:
            results["errors"].append(f"Patient: {result}")
            print(f"   ❌ Patient 上傳失敗: {result}")
        
        return results

def custom_patient_generation():
    """自定義單一病人資料生成功能"""
    generator = TWFHIRGeneratorFixed()
    
    print("🎯 自定義單一病人資料生成")
    print("=" * 50)
    
    # 顯示選項
    print("請選擇生成方式:")
    print("1. 瀏覽並選擇特定項目")
    print("2. 搜尋並選擇項目")
    print("3. 使用代碼直接指定")
    print("4. 返回主選單")
    
    choice = input("\n請選擇 (1-4): ") or "4"
    
    if choice == "1":
        return browse_and_select(generator)
    elif choice == "2":
        return search_and_select(generator)
    elif choice == "3":
        return direct_code_input(generator)
    else:
        return None

def browse_and_select(generator):
    """瀏覽並選擇項目"""
    selected_conditions = []
    selected_observations = []
    selected_medications = []
    
    # 選擇疾病
    print("\n📋 選擇疾病 (可選多個，輸入索引號，用逗號分隔，直接按 Enter 跳過)")
    categories = generator.get_categories()
    
    print("可用疾病類別:")
    for i, category in enumerate(categories["conditions"]):
        print(f"  {i+1}. {category}")
    
    category_choice = input("選擇類別 (輸入數字，或直接按 Enter 查看全部): ")
    
    if category_choice.isdigit():
        category_idx = int(category_choice) - 1
        if 0 <= category_idx < len(categories["conditions"]):
            selected_category = categories["conditions"][category_idx]
            conditions = generator.list_available_conditions(category=selected_category, limit=20)
        else:
            conditions = generator.list_available_conditions(limit=20)
    else:
        conditions = generator.list_available_conditions(limit=20)
    
    print("\n可用疾病:")
    for condition in conditions:
        print(f"  {condition['index']}: {condition['display']} ({condition['category']})")
    
    condition_input = input("選擇疾病索引 (用逗號分隔): ").strip()
    if condition_input:
        try:
            selected_conditions = [int(x.strip()) for x in condition_input.split(",")]
        except ValueError:
            print("⚠️ 輸入格式錯誤，跳過疾病選擇")
    
    # 選擇觀察項目
    print("\n🔬 選擇觀察項目 (可選多個，輸入索引號，用逗號分隔，直接按 Enter 跳過)")
    
    print("可用觀察類別:")
    for i, category in enumerate(categories["observations"]):
        print(f"  {i+1}. {category}")
    
    category_choice = input("選擇類別 (輸入數字，或直接按 Enter 查看全部): ")
    
    if category_choice.isdigit():
        category_idx = int(category_choice) - 1
        if 0 <= category_idx < len(categories["observations"]):
            selected_category = categories["observations"][category_idx]
            observations = generator.list_available_observations(category=selected_category, limit=20)
        else:
            observations = generator.list_available_observations(limit=20)
    else:
        observations = generator.list_available_observations(limit=20)
    
    print("\n可用觀察項目:")
    for observation in observations:
        print(f"  {observation['index']}: {observation['display']} ({observation['unit']}) - {observation['category']}")
    
    observation_input = input("選擇觀察項目索引 (用逗號分隔): ").strip()
    if observation_input:
        try:
            selected_observations = [int(x.strip()) for x in observation_input.split(",")]
        except ValueError:
            print("⚠️ 輸入格式錯誤，跳過觀察項目選擇")
    
    # 選擇藥物
    print("\n💊 選擇藥物 (可選多個，輸入索引號，用逗號分隔，直接按 Enter 跳過)")
    
    print("可用藥物類別:")
    for i, category in enumerate(categories["medications"]):
        print(f"  {i+1}. {category}")
    
    category_choice = input("選擇類別 (輸入數字，或直接按 Enter 查看全部): ")
    
    if category_choice.isdigit():
        category_idx = int(category_choice) - 1
        if 0 <= category_idx < len(categories["medications"]):
            selected_category = categories["medications"][category_idx]
            medications = generator.list_available_medications(category=selected_category, limit=20)
        else:
            medications = generator.list_available_medications(limit=20)
    else:
        medications = generator.list_available_medications(limit=20)
    
    print("\n可用藥物:")
    for medication in medications:
        print(f"  {medication['index']}: {medication['display']} ({medication['strength']}) - {medication['category']}")
    
    medication_input = input("選擇藥物索引 (用逗號分隔): ").strip()
    if medication_input:
        try:
            selected_medications = [int(x.strip()) for x in medication_input.split(",")]
        except ValueError:
            print("⚠️ 輸入格式錯誤，跳過藥物選擇")
    
    return generator.generate_custom_patient_data(
        selected_conditions=selected_conditions,
        selected_observations=selected_observations,
        selected_medications=selected_medications
    )

def search_and_select(generator):
    """搜尋並選擇項目"""
    print("\n🔍 搜尋項目")
    query = input("請輸入搜尋關鍵字: ").strip()
    
    if not query:
        print("⚠️ 未輸入搜尋關鍵字")
        return None
    
    results = generator.search_items(query)
    
    selected_conditions = []
    selected_observations = []
    selected_medications = []
    
    # 顯示疾病搜尋結果
    if results["conditions"]:
        print(f"\n📋 找到 {len(results['conditions'])} 個相關疾病:")
        for condition in results["conditions"]:
            print(f"  {condition['index']}: {condition['display']} ({condition['category']})")
        
        condition_input = input("選擇疾病索引 (用逗號分隔，或按 Enter 跳過): ").strip()
        if condition_input:
            try:
                selected_conditions = [int(x.strip()) for x in condition_input.split(",")]
            except ValueError:
                print("⚠️ 輸入格式錯誤")
    
    # 顯示觀察項目搜尋結果
    if results["observations"]:
        print(f"\n🔬 找到 {len(results['observations'])} 個相關觀察項目:")
        for observation in results["observations"]:
            print(f"  {observation['index']}: {observation['display']} ({observation['unit']}) - {observation['category']}")
        
        observation_input = input("選擇觀察項目索引 (用逗號分隔，或按 Enter 跳過): ").strip()
        if observation_input:
            try:
                selected_observations = [int(x.strip()) for x in observation_input.split(",")]
            except ValueError:
                print("⚠️ 輸入格式錯誤")
    
    # 顯示藥物搜尋結果
    if results["medications"]:
        print(f"\n💊 找到 {len(results['medications'])} 個相關藥物:")
        for medication in results["medications"]:
            print(f"  {medication['index']}: {medication['display']} ({medication['strength']}) - {medication['category']}")
        
        medication_input = input("選擇藥物索引 (用逗號分隔，或按 Enter 跳過): ").strip()
        if medication_input:
            try:
                selected_medications = [int(x.strip()) for x in medication_input.split(",")]
            except ValueError:
                print("⚠️ 輸入格式錯誤")
    
    if not (selected_conditions or selected_observations or selected_medications):
        print("⚠️ 未選擇任何項目")
        return None
    
    return generator.generate_custom_patient_data(
        selected_conditions=selected_conditions,
        selected_observations=selected_observations,
        selected_medications=selected_medications
    )

def direct_code_input(generator):
    """直接輸入代碼"""
    print("\n📝 直接輸入代碼")
    print("請輸入代碼，用逗號分隔 (或按 Enter 跳過)")
    
    condition_codes = input("疾病代碼 (SNOMED CT): ").strip()
    observation_codes = input("觀察項目代碼 (LOINC): ").strip()
    medication_codes = input("藥物代碼 (RxNorm): ").strip()
    
    selected_conditions = []
    selected_observations = []
    selected_medications = []
    
    if condition_codes:
        selected_conditions = [code.strip() for code in condition_codes.split(",")]
    
    if observation_codes:
        selected_observations = [code.strip() for code in observation_codes.split(",")]
    
    if medication_codes:
        selected_medications = [code.strip() for code in medication_codes.split(",")]
    
    if not (selected_conditions or selected_observations or selected_medications):
        print("⚠️ 未輸入任何代碼")
        return None
    
    return generator.generate_custom_patient_data(
        selected_conditions=selected_conditions,
        selected_observations=selected_observations,
        selected_medications=selected_medications
    )

def main():
    """
    主函數 - 修復版的台灣 FHIR 資料生成和上傳
    """
    generator = TWFHIRGeneratorFixed()
    
    print("🏥 台灣 FHIR 病人資料完整生成器 - 修復版")
    print("=" * 60)
    print("✅ 修復了 Condition 和 Observation 上傳失敗的問題")
    print("✅ 使用 SNOMED CT 代碼替代有問題的 ICD-10 代碼")
    print("✅ 修正了 UCUM 單位代碼映射")
    print("✅ 確保同一病人不會生成重複的疾病和觀察項目")
    print("✅ 支援自定義單一病人資料生成")
    print()
    print(f"📋 可用的疾病類型: {len(generator.conditions)} 種")
    print(f"📋 可用的觀察項目: {len(generator.observations)} 種")
    print(f"📋 可用的藥物類型: {len(generator.medications)} 種")
    print()
    
    # 選擇生成模式
    print("請選擇生成模式:")
    print("1. 批量生成 (原有功能)")
    print("2. 自定義單一病人生成 (新功能)")
    
    mode_choice = input("請選擇模式 (1-2): ") or "1"
    
    if mode_choice == "2":
        # 自定義單一病人生成
        patient_data = custom_patient_generation()
        if not patient_data:
            print("❌ 未生成任何資料")
            return
        
        # 顯示生成結果
        patient_name = patient_data['patient']['name'][0]['text']
        print(f"\n✅ 成功生成病人資料: {patient_name}")
        print(f"   疾病: {len(patient_data['conditions'])} 個")
        print(f"   觀察: {len(patient_data['observations'])} 個")
        print(f"   藥物: {len(patient_data['medications'])} 個")
        print(f"   處方: {len(patient_data['medication_requests'])} 個")
        
        # 儲存檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output/custom_patients")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"custom_patient_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 資料已儲存到: {filepath}")
        
        # 詢問是否上傳
        upload_choice = input("\n是否要上傳到 FHIR 伺服器？(y/N): ").lower()
        if upload_choice == 'y':
            print("\n🚀 選擇上傳目標:")
            print("1. 台灣 TWCORE 伺服器")
            print("2. 國際 HAPI 伺服器")
            print("3. 自訂伺服器")
            
            server_choice = input("請選擇 (1-3): ") or "1"
            
            if server_choice == "1":
                server_url = "https://twcore.hapi.fhir.tw/fhir"
            elif server_choice == "2":
                server_url = "http://hapi.fhir.org/baseR4"
            elif server_choice == "3":
                server_url = input("請輸入 FHIR 伺服器地址: ")
            else:
                print("❌ 無效選擇")
                return
            
            print(f"\n📤 開始上傳到: {server_url}")
            result = generator.upload_patient_data_to_server(patient_data, server_url)
            
            # 顯示上傳結果
            if result["patient"]:
                print(f"✅ 病人上傳成功，ID: {result['patient']}")
                print(f"✅ 疾病上傳成功: {len(result['conditions'])} 個")
                print(f"✅ 觀察上傳成功: {len(result['observations'])} 個")
                print(f"✅ 藥物上傳成功: {len(result['medications'])} 個")
                print(f"✅ 處方上傳成功: {len(result['medication_requests'])} 個")
                if result["errors"]:
                    print(f"⚠️ 錯誤: {len(result['errors'])} 個")
            else:
                print("❌ 上傳失敗")
        
        return
    
    # 原有的批量生成功能
    print()
    
    # 獲取用戶輸入
    try:
        num_patients = int(input("請輸入要生成的病人數量 (X): ") or "2")
        num_conditions = int(input("請輸入每個病人的疾病數量 (Y，可設為0): ") or "2")
        num_observations = int(input("請輸入每個病人的觀察記錄數量 (Z，可設為0): ") or "3")
        num_medications = int(input("請輸入每個病人的藥物數量 (M，可設為0): ") or "2")
        
        print(f"\n📋 將生成 {num_patients} 個病人，每人有 {num_conditions} 個疾病、{num_observations} 個觀察記錄和 {num_medications} 個藥物")
        print(f"📊 總計資源: {num_patients} Patient + {num_patients * num_conditions} Condition + {num_patients * num_observations} Observation + {num_patients * num_medications} Medication + {num_patients * num_medications} MedicationRequest")
        
        # 生成資料
        print(f"\n🎲 开始生成資料...")
        all_patient_data = []
        
        for i in range(num_patients):
            print(f"👤 生成第 {i+1} 個病人...")
            patient_data = generator.generate_complete_patient_data(num_conditions, num_observations, num_medications)
            all_patient_data.append(patient_data)
            
            patient_name = patient_data['patient']['name'][0]['text']
            print(f"   姓名: {patient_name}")
            print(f"   疾病: {len(patient_data['conditions'])} 個")
            print(f"   觀察: {len(patient_data['observations'])} 個")
            print(f"   藥物: {len(patient_data['medications'])} 個")
            print(f"   處方: {len(patient_data['medication_requests'])} 個")
        
        # 儲存到檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output/complete_patients_fixed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"tw_complete_patients_fixed_{timestamp}.json"
        filepath = output_dir / filename
        
        # 转换为可儲存的格式
        save_data = []
        for data in all_patient_data:
            save_data.append({
                "patient": data["patient"],
                "conditions": data["conditions"],
                "observations": data["observations"],
                "medications": data["medications"],
                "medication_requests": data["medication_requests"]
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 資料已儲存到: {filepath}")
        
        # 询问是否上傳
        print(f"\n🚀 是否要上傳到 FHIR 伺服器？")
        print("1. 上傳到台灣 TWCORE 伺服器 (https://twcore.hapi.fhir.tw/fhir)")
        print("2. 上傳到國際 HAPI 伺服器 (http://hapi.fhir.org/baseR4)")
        print("3. 自訂伺服器地址")
        print("4. 不上傳，僅生成本機檔案")
        
        choice = input("\n請選擇 (1-4): ") or "4"
        
        if choice == "1":
            server_url = "https://twcore.hapi.fhir.tw/fhir"
        elif choice == "2":
            server_url = "http://hapi.fhir.org/baseR4"
        elif choice == "3":
            server_url = input("請輸入 FHIR 伺服器地址: ")
        else:
            print("✅ 資料生成完成，未上傳到伺服器")
            return
        
        print(f"\n🌐 目標伺服器: {server_url}")
        print("⚠️  警告：這將上傳真實資料到 FHIR 伺服器")
        
        confirm = input("確認上傳？(y/N): ").lower()
        if confirm != 'y':
            print("❌ 用戶取消上傳")
            return
        
        # 開始上傳
        print(f"\n📤 開始上傳修復版資料到伺服器...")
        upload_results = []
        
        for i, patient_data in enumerate(all_patient_data):
            print(f"\n👤 上傳第 {i+1}/{num_patients} 個病人...")
            result = generator.upload_patient_data_to_server(patient_data, server_url)
            upload_results.append(result)
        
        # 统计上傳结果
        successful_patients = sum(1 for r in upload_results if r["patient"])
        total_conditions = sum(len(r["conditions"]) for r in upload_results)
        total_observations = sum(len(r["observations"]) for r in upload_results)
        total_medications = sum(len(r["medications"]) for r in upload_results)
        total_medication_requests = sum(len(r["medication_requests"]) for r in upload_results)
        total_errors = sum(len(r["errors"]) for r in upload_results)
        
        print(f"\n📊 修復版上傳完成統計:")
        print(f"   成功上傳病人: {successful_patients}/{num_patients}")
        print(f"   成功上傳疾病: {total_conditions}")
        print(f"   成功上傳觀察: {total_observations}")
        print(f"   成功上傳藥物: {total_medications}")
        print(f"   成功上傳處方: {total_medication_requests}")
        print(f"   錯誤數量: {total_errors}")
        
        # 儲存上傳結果
        upload_result_file = f"upload_results_fixed_{timestamp}.json"
        with open(upload_result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "upload_time": datetime.now().isoformat(),
                "server_url": server_url,
                "version": "fixed",
                "statistics": {
                    "patients": successful_patients,
                    "conditions": total_conditions,
                    "observations": total_observations,
                    "medications": total_medications,
                    "medication_requests": total_medication_requests,
                    "errors": total_errors
                },
                "results": upload_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📁 上傳結果已儲存: {upload_result_file}")
        
        if successful_patients > 0:
            print(f"\n🎉 修復版上傳成功！您可以訪問:")
            print(f"   {server_url}/Patient (查看所有病人)")
            print(f"   {server_url}/Condition (查看所有疾病)")
            print(f"   {server_url}/Observation (查看所有觀察)")
            print(f"   {server_url}/Medication (查看所有藥物)")
            print(f"   {server_url}/MedicationRequest (查看所有處方)")
        
    except KeyboardInterrupt:
        print("\n❌ 用戶中斷操作")
    except Exception as e:
        print(f"\n❌ 程式執行出錯: {e}")

if __name__ == "__main__":
    main()
