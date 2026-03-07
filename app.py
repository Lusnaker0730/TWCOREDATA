#!/usr/bin/env python3
"""
台灣 FHIR 病人資料生成器 - Web UI 版本
提供簡潔美觀的網頁介面來生成和上傳 FHIR 資料
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from datetime import datetime
from pathlib import Path
import threading
import time
from generate_TW_patients import TWFHIRGeneratorFixed
from models import DateRangeConfig, BatchGenerationConfig, CustomGenerationConfig

app = Flask(__name__)

# 共用 Generator 實例，避免每次 API 請求重新讀取配置檔案
_generator = TWFHIRGeneratorFixed()


def _parse_date(value):
    """將字串日期 (YYYY-MM-DD) 轉為 datetime，無效或空值回傳 None"""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        return None


def _parse_date_params(getter):
    """從 form/dict getter 解析時間範圍參數"""
    return DateRangeConfig(
        encounter_date_from=_parse_date(getter('encounter_date_from')),
        encounter_date_to=_parse_date(getter('encounter_date_to')),
        condition_date_from=_parse_date(getter('condition_date_from')),
        condition_date_to=_parse_date(getter('condition_date_to')),
        observation_date_from=_parse_date(getter('observation_date_from')),
        observation_date_to=_parse_date(getter('observation_date_to')),
        allergy_date_from=_parse_date(getter('allergy_date_from')),
        allergy_date_to=_parse_date(getter('allergy_date_to')),
    )

# 全域變數來追蹤生成狀態
generation_status = {
    'is_running': False,
    'progress': 0,
    'current_step': '',
    'results': None,
    'error': None
}

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/custom')
def custom():
    """自定義病人生成頁面"""
    return render_template('custom.html')

@app.route('/dashboard')
def dashboard():
    """資料統計儀表板頁面"""
    return render_template('dashboard.html')

@app.route('/api/scenarios')
def get_scenarios():
    """獲取情境預設列表"""
    try:
        scenarios_file = Path('config/scenarios.json')
        if scenarios_file.exists():
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        else:
            return jsonify({'scenarios': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _accumulate_stats(stats, patient_data):
    """累加病人資料統計"""
    for key in ['encounters', 'allergies', 'conditions', 'observations', 'medications', 'medication_requests']:
        stats[f'total_{key}'] += len(patient_data.get(key, []))

@app.route('/api/statistics')
def get_statistics():
    """獲取資料統計信息"""
    try:
        stats = {
            'total_files': 0,
            'total_patients': 0,
            'total_encounters': 0,
            'total_allergies': 0,
            'total_conditions': 0,
            'total_observations': 0,
            'total_medications': 0,
            'total_medication_requests': 0,
            'recent_generations': [],
            'file_sizes': []
        }

        # 讀取 complete_patients_fixed 目錄
        output_dir = Path('output/complete_patients_fixed')
        if output_dir.exists():
            json_files = sorted(output_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True)
            stats['total_files'] = len(json_files)

            for json_file in json_files[:10]:  # 只讀取最近10個檔案
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # 統計各類資源
                        for patient_data in data:
                            stats['total_patients'] += 1
                            _accumulate_stats(stats, patient_data)

                        # 記錄最近的生成
                        file_stat = json_file.stat()
                        stats['recent_generations'].append({
                            'filename': json_file.name,
                            'timestamp': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                            'size': f'{file_stat.st_size / 1024:.2f} KB',
                            'patients': len(data)
                        })

                except Exception as e:
                    print(f"Error reading {json_file}: {e}")
                    continue

        # 讀取 custom_patients 目錄
        custom_dir = Path('output/custom_patients')
        if custom_dir.exists():
            custom_files = list(custom_dir.glob('*.json'))
            stats['total_files'] += len(custom_files)

            for json_file in sorted(custom_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            stats['total_patients'] += 1
                            _accumulate_stats(stats, data)
                except Exception as e:
                    continue

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_data():
    """生成 FHIR 資料的 API 端點"""
    global generation_status

    if generation_status['is_running']:
        return jsonify({'error': '已有生成任務正在執行中'}), 400

    try:
        # 獲取表單資料
        num_patients = int(request.form.get('num_patients', 2))
        num_conditions = int(request.form.get('num_conditions', 2))
        num_observations = int(request.form.get('num_observations', 3))
        num_medications = int(request.form.get('num_medications', 2))
        num_encounters = int(request.form.get('num_encounters', 1))  # 新增就診記錄數量
        num_allergies = int(request.form.get('num_allergies', 1))
        server_choice = request.form.get('server_choice', 'none')
        custom_server = request.form.get('custom_server', '')

        # 解析可選的時間範圍參數
        date_params = _parse_date_params(request.form.get)

        # 驗證輸入
        if num_patients < 1 or num_patients > 100:
            return jsonify({'error': '病人數量必須在 1-100 之間'}), 400
        if num_conditions < 0 or num_conditions > 20:
            return jsonify({'error': '疾病數量必須在 0-20 之間'}), 400
        if num_observations < 0 or num_observations > 50:
            return jsonify({'error': '觀察記錄數量必須在 0-50 之間'}), 400
        if num_medications < 0 or num_medications > 20:
            return jsonify({'error': '藥物數量必須在 0-20 之間'}), 400
        if num_encounters < 0 or num_encounters > 10:
            return jsonify({'error': '就診記錄數量必須在 0-10 之間'}), 400
        if num_allergies < 0 or num_allergies > 20:
            return jsonify({'error': '過敏數量必須在 0-20 之間'}), 400

        # 重置狀態
        generation_status = {
            'is_running': True,
            'progress': 0,
            'current_step': '準備生成資料...',
            'results': None,
            'error': None
        }

        # 在背景執行緒中執行生成任務
        config = BatchGenerationConfig(
            num_patients=num_patients,
            num_conditions=num_conditions,
            num_observations=num_observations,
            num_medications=num_medications,
            num_encounters=num_encounters,
            num_allergies=num_allergies,
            server_choice=server_choice,
            custom_server=custom_server,
            dates=date_params,
        )

        thread = threading.Thread(
            target=generate_data_background,
            args=(config,)
        )
        thread.daemon = True
        thread.start()

        return jsonify({'message': '開始生成資料', 'task_id': 'generate_task'})

    except ValueError as e:
        return jsonify({'error': f'輸入格式錯誤: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'發生錯誤: {str(e)}'}), 500

def generate_data_background(config):
    """背景執行緒中執行資料生成"""
    global generation_status

    try:
        generator = _generator

        # 步驟 1: 生成資料
        generation_status['current_step'] = f'生成 {config.num_patients} 個病人資料...'
        generation_status['progress'] = 10

        all_patient_data = []
        for i in range(config.num_patients):
            generation_status['current_step'] = f'生成第 {i+1}/{config.num_patients} 個病人...'
            generation_status['progress'] = 10 + (i / config.num_patients) * 40

            patient_data = generator.generate_complete_patient_data(
                config.num_conditions, config.num_observations, config.num_medications,
                config.num_allergies, config.num_encounters,
                encounter_date_from=config.dates.encounter_date_from,
                encounter_date_to=config.dates.encounter_date_to,
                condition_date_from=config.dates.condition_date_from,
                condition_date_to=config.dates.condition_date_to,
                observation_date_from=config.dates.observation_date_from,
                observation_date_to=config.dates.observation_date_to,
                allergy_date_from=config.dates.allergy_date_from,
                allergy_date_to=config.dates.allergy_date_to,
            )
            all_patient_data.append(patient_data)
            time.sleep(0.1)  # 模擬處理時間

        # 步驟 2: 儲存檔案
        generation_status['current_step'] = '儲存資料到檔案...'
        generation_status['progress'] = 50

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output/complete_patients_fixed")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"tw_complete_patients_fixed_{timestamp}.json"
        filepath = output_dir / filename

        save_data = []
        for data in all_patient_data:
            save_data.append({
                "patient": data["patient"],
                "encounters": data["encounters"],
                "conditions": data["conditions"],
                "allergies": data["allergies"],
                "observations": data["observations"],
                "medications": data["medications"],
                "medication_requests": data["medication_requests"]
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        generation_status['progress'] = 60

        # 步驟 3: 上傳到伺服器（如果需要）
        upload_results = None
        if config.server_choice != 'none':
            generation_status['current_step'] = '上傳資料到 FHIR 伺服器...'

            # 確定伺服器 URL
            if config.server_choice == 'local':
                server_url = "http://hapi-fhir:8080/fhir"
            elif config.server_choice == 'twcore':
                server_url = "https://twcore.hapi.fhir.tw/fhir"
            elif config.server_choice == 'hapi':
                server_url = "http://hapi.fhir.org/baseR4"
            elif config.server_choice == 'custom':
                server_url = config.custom_server

            upload_results = []
            for i, patient_data in enumerate(all_patient_data):
                generation_status['current_step'] = f'上傳第 {i+1}/{config.num_patients} 個病人...'
                generation_status['progress'] = 60 + (i / config.num_patients) * 35

                result = generator.upload_patient_data_to_server(patient_data, server_url)
                upload_results.append(result)
                time.sleep(0.5)  # 避免過於頻繁的請求

            # 儲存上傳結果
            upload_result_file = f"upload_results_fixed_{timestamp}.json"
            successful_patients = sum(1 for r in upload_results if r["patient"])
            resource_keys = ['encounters', 'allergies', 'conditions', 'observations', 'medications', 'medication_requests']
            upload_totals = {
                key: sum(len(r.get(key, [])) for r in upload_results)
                for key in resource_keys
            }
            total_errors = sum(len(r["errors"]) for r in upload_results)

            with open(upload_result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "upload_time": datetime.now().isoformat(),
                    "server_url": server_url,
                    "version": "web_ui",
                    "statistics": {
                        "patients": successful_patients,
                        **upload_totals,
                        "errors": total_errors
                    },
                    "results": upload_results
                }, f, ensure_ascii=False, indent=2)

        # 完成
        generation_status['current_step'] = '完成！'
        generation_status['progress'] = 100
        generation_status['is_running'] = False

        # 準備結果資料
        results = {
            'success': True,
            'filename': str(filepath),
            'num_patients': config.num_patients,
            'num_encounters': config.num_encounters * config.num_patients,
            'num_allergies': config.num_allergies * config.num_patients,
            'num_conditions': config.num_conditions * config.num_patients,
            'num_observations': config.num_observations * config.num_patients,
            'num_medications': config.num_medications * config.num_patients,
            'num_medication_requests': config.num_medications * config.num_patients,
            'timestamp': timestamp
        }

        if upload_results:
            results['upload'] = {
                'server_url': server_url,
                'successful_patients': successful_patients,
                **{f'total_{k}': v for k, v in upload_totals.items()},
                'total_errors': total_errors
            }

        generation_status['results'] = results

    except Exception as e:
        generation_status['is_running'] = False
        generation_status['error'] = str(e)
        generation_status['current_step'] = f'錯誤: {str(e)}'

@app.route('/status')
def get_status():
    """獲取生成狀態的 API 端點"""
    return jsonify(generation_status)

@app.route('/download/<filename>')
def download_file(filename):
    """下載生成的檔案"""
    try:
        filepath = Path("output/complete_patients_fixed") / filename
        if filepath.exists():
            return send_file(str(filepath), as_attachment=True)
        else:
            return jsonify({'error': '檔案不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/info')
def get_info():
    """獲取系統資訊"""
    return jsonify({
        'available_conditions': len(_generator.conditions),
        'available_observations': len(_generator.observations),
        'available_medications': len(_generator.medications),
        'available_allergies': len(_generator.allergies),
        'version': '1.0.0'
    })

@app.route('/api/resources/<resource_type>')
def get_resources(resource_type):
    """通用資源列表 API"""
    valid_types = ["conditions", "observations", "medications", "allergies"]
    if resource_type not in valid_types:
        return jsonify({'error': f'無效的資源類型: {resource_type}'}), 400
    category = request.args.get('category')
    limit = request.args.get('limit', type=int)
    return jsonify(_generator.list_available_items(resource_type, category=category, limit=limit))

@app.route('/api/conditions')
def get_conditions():
    return get_resources('conditions')

@app.route('/api/observations')
def get_observations():
    return get_resources('observations')

@app.route('/api/medications')
def get_medications():
    return get_resources('medications')

@app.route('/api/allergies')
def get_allergies():
    return get_resources('allergies')

@app.route('/api/categories')
def get_categories():
    """獲取所有類別"""
    return jsonify(_generator.get_categories())

@app.route('/api/search')
def search_items():
    """搜尋項目"""
    query = request.args.get('query', '')
    item_type = request.args.get('type', 'all')

    if not query:
        return jsonify({'error': '請提供搜尋關鍵字'}), 400

    return jsonify(_generator.search_items(query, item_type))

@app.route('/generate_custom', methods=['POST'])
def generate_custom():
    """生成自定義單一病人資料"""
    try:
        data = request.get_json()

        # 解析可選的時間範圍參數
        date_params = _parse_date_params(data.get)

        config = CustomGenerationConfig(
            selected_conditions=data.get('conditions', []),
            selected_observations=data.get('observations', []),
            selected_medications=data.get('medications', []),
            selected_allergies=data.get('allergies', []),
            server_choice=data.get('server_choice', '1'),
            custom_server=data.get('custom_server', ''),
            upload=data.get('upload', False),
            dates=date_params,
        )

        # 生成資料
        patient_data = _generator.generate_custom_patient_data(
            selected_conditions=config.selected_conditions,
            selected_observations=config.selected_observations,
            selected_medications=config.selected_medications,
            selected_allergies=config.selected_allergies,
            encounter_date_from=config.dates.encounter_date_from,
            encounter_date_to=config.dates.encounter_date_to,
            condition_date_from=config.dates.condition_date_from,
            condition_date_to=config.dates.condition_date_to,
            observation_date_from=config.dates.observation_date_from,
            observation_date_to=config.dates.observation_date_to,
            allergy_date_from=config.dates.allergy_date_from,
            allergy_date_to=config.dates.allergy_date_to,
        )

        if not patient_data:
            return jsonify({'error': '生成資料失敗'}), 500

        # 儲存檔案
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output/custom_patients")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"custom_patient_{timestamp}.json"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(patient_data, f, ensure_ascii=False, indent=2)

        # 準備回應資料
        patient_name = patient_data['patient']['name'][0]['text']
        result = {
            'success': True,
            'patient_name': patient_name,
            'filename': filename,
            'filepath': str(filepath),
            'stats': {
                'conditions': len(patient_data['conditions']),
                'observations': len(patient_data['observations']),
                'medications': len(patient_data['medications']),
                'medication_requests': len(patient_data['medication_requests']),
                'allergies': len(patient_data['allergies']),
            }
        }

        # 如果需要上傳
        if config.upload:
            if config.server_choice == "0":
                server_url = "http://hapi-fhir:8080/fhir"
            elif config.server_choice == "1":
                server_url = "https://twcore.hapi.fhir.tw/fhir"
            elif config.server_choice == "2":
                server_url = "http://hapi.fhir.org/baseR4"
            elif config.server_choice == "3":
                server_url = config.custom_server
            else:
                return jsonify({'error': '無效的伺服器選擇'}), 400

            upload_result = _generator.upload_patient_data_to_server(patient_data, server_url)
            result['upload'] = {
                'success': bool(upload_result["patient"]),
                'server_url': server_url,
                'patient_id': upload_result["patient"],
                'uploaded_conditions': len(upload_result['conditions']),
                'uploaded_observations': len(upload_result['observations']),
                'uploaded_medications': len(upload_result['medications']),
                'uploaded_medication_requests': len(upload_result['medication_requests']),
                'uploaded_allergies': len(upload_result.get('allergies', [])),
                'errors': upload_result['errors']
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'生成失敗: {str(e)}'}), 500

if __name__ == '__main__':
    # 確保輸出目錄存在
    Path("output/complete_patients_fixed").mkdir(parents=True, exist_ok=True)

    print("🏥 台灣 FHIR 病人資料生成器 - Web UI 版本")
    print("=" * 50)
    print("🌐 啟動網頁伺服器...")
    print("📱 請在瀏覽器中開啟: http://localhost:5000")
    print("⏹️  按 Ctrl+C 停止伺服器")

    app.run(debug=True, host='0.0.0.0', port=5000)
