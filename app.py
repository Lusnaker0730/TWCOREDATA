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

app = Flask(__name__)

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
        server_choice = request.form.get('server_choice', 'none')
        custom_server = request.form.get('custom_server', '')
        
        # 驗證輸入
        if num_patients < 1 or num_patients > 100:
            return jsonify({'error': '病人數量必須在 1-100 之間'}), 400
        if num_conditions < 0 or num_conditions > 20:
            return jsonify({'error': '疾病數量必須在 0-20 之間'}), 400
        if num_observations < 0 or num_observations > 50:
            return jsonify({'error': '觀察記錄數量必須在 0-50 之間'}), 400
        if num_medications < 0 or num_medications > 20:
            return jsonify({'error': '藥物數量必須在 0-20 之間'}), 400
        
        # 重置狀態
        generation_status = {
            'is_running': True,
            'progress': 0,
            'current_step': '準備生成資料...',
            'results': None,
            'error': None
        }
        
        # 在背景執行緒中執行生成任務
        thread = threading.Thread(
            target=generate_data_background,
            args=(num_patients, num_conditions, num_observations, num_medications, server_choice, custom_server)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': '開始生成資料', 'task_id': 'generate_task'})
        
    except ValueError as e:
        return jsonify({'error': f'輸入格式錯誤: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'發生錯誤: {str(e)}'}), 500

def generate_data_background(num_patients, num_conditions, num_observations, num_medications, server_choice, custom_server):
    """背景執行緒中執行資料生成"""
    global generation_status
    
    try:
        generator = TWFHIRGeneratorFixed()
        
        # 步驟 1: 生成資料
        generation_status['current_step'] = f'生成 {num_patients} 個病人資料...'
        generation_status['progress'] = 10
        
        all_patient_data = []
        for i in range(num_patients):
            generation_status['current_step'] = f'生成第 {i+1}/{num_patients} 個病人...'
            generation_status['progress'] = 10 + (i / num_patients) * 40
            
            patient_data = generator.generate_complete_patient_data(num_conditions, num_observations, num_medications)
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
                "conditions": data["conditions"],
                "observations": data["observations"],
                "medications": data["medications"],
                "medication_requests": data["medication_requests"]
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        generation_status['progress'] = 60
        
        # 步驟 3: 上傳到伺服器（如果需要）
        upload_results = None
        if server_choice != 'none':
            generation_status['current_step'] = '上傳資料到 FHIR 伺服器...'
            
            # 確定伺服器 URL
            if server_choice == 'twcore':
                server_url = "https://twcore.hapi.fhir.tw/fhir"
            elif server_choice == 'hapi':
                server_url = "http://hapi.fhir.org/baseR4"
            elif server_choice == 'custom':
                server_url = custom_server
            
            upload_results = []
            for i, patient_data in enumerate(all_patient_data):
                generation_status['current_step'] = f'上傳第 {i+1}/{num_patients} 個病人...'
                generation_status['progress'] = 60 + (i / num_patients) * 35
                
                result = generator.upload_patient_data_to_server(patient_data, server_url)
                upload_results.append(result)
                time.sleep(0.5)  # 避免過於頻繁的請求
            
            # 儲存上傳結果
            upload_result_file = f"upload_results_fixed_{timestamp}.json"
            successful_patients = sum(1 for r in upload_results if r["patient"])
            total_conditions = sum(len(r["conditions"]) for r in upload_results)
            total_observations = sum(len(r["observations"]) for r in upload_results)
            total_medications = sum(len(r["medications"]) for r in upload_results)
            total_medication_requests = sum(len(r["medication_requests"]) for r in upload_results)
            total_errors = sum(len(r["errors"]) for r in upload_results)
            
            with open(upload_result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "upload_time": datetime.now().isoformat(),
                    "server_url": server_url,
                    "version": "web_ui",
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
        
        # 完成
        generation_status['current_step'] = '完成！'
        generation_status['progress'] = 100
        generation_status['is_running'] = False
        
        # 準備結果資料
        results = {
            'success': True,
            'filename': str(filepath),
            'num_patients': num_patients,
            'num_conditions': num_conditions * num_patients,
            'num_observations': num_observations * num_patients,
            'num_medications': num_medications * num_patients,
            'num_medication_requests': num_medications * num_patients,
            'timestamp': timestamp
        }
        
        if upload_results:
            results['upload'] = {
                'server_url': server_url,
                'successful_patients': successful_patients,
                'total_conditions': total_conditions,
                'total_observations': total_observations,
                'total_medications': total_medications,
                'total_medication_requests': total_medication_requests,
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
    generator = TWFHIRGeneratorFixed()
    return jsonify({
        'available_conditions': len(generator.conditions),
        'available_observations': len(generator.observations),
        'available_medications': len(generator.medications),
        'version': '1.0.0'
    })

@app.route('/api/conditions')
def get_conditions():
    """獲取可用疾病列表"""
    generator = TWFHIRGeneratorFixed()
    category = request.args.get('category')
    limit = request.args.get('limit', type=int)
    return jsonify(generator.list_available_conditions(category=category, limit=limit))

@app.route('/api/observations')
def get_observations():
    """獲取可用觀察項目列表"""
    generator = TWFHIRGeneratorFixed()
    category = request.args.get('category')
    limit = request.args.get('limit', type=int)
    return jsonify(generator.list_available_observations(category=category, limit=limit))

@app.route('/api/medications')
def get_medications():
    """獲取可用藥物列表"""
    generator = TWFHIRGeneratorFixed()
    category = request.args.get('category')
    limit = request.args.get('limit', type=int)
    return jsonify(generator.list_available_medications(category=category, limit=limit))

@app.route('/api/categories')
def get_categories():
    """獲取所有類別"""
    generator = TWFHIRGeneratorFixed()
    return jsonify(generator.get_categories())

@app.route('/api/search')
def search_items():
    """搜尋項目"""
    generator = TWFHIRGeneratorFixed()
    query = request.args.get('query', '')
    item_type = request.args.get('type', 'all')
    
    if not query:
        return jsonify({'error': '請提供搜尋關鍵字'}), 400
    
    return jsonify(generator.search_items(query, item_type))

@app.route('/generate_custom', methods=['POST'])
def generate_custom():
    """生成自定義單一病人資料"""
    try:
        data = request.get_json()
        
        selected_conditions = data.get('conditions', [])
        selected_observations = data.get('observations', [])
        selected_medications = data.get('medications', [])
        server_choice = data.get('server_choice', '1')
        custom_server = data.get('custom_server', '')
        
        # 生成資料
        generator = TWFHIRGeneratorFixed()
        patient_data = generator.generate_custom_patient_data(
            selected_conditions=selected_conditions,
            selected_observations=selected_observations,
            selected_medications=selected_medications
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
                'medication_requests': len(patient_data['medication_requests'])
            }
        }
        
        # 如果需要上傳
        if data.get('upload', False):
            if server_choice == "1":
                server_url = "https://twcore.hapi.fhir.tw/fhir"
            elif server_choice == "2":
                server_url = "http://hapi.fhir.org/baseR4"
            elif server_choice == "3":
                server_url = custom_server
            else:
                return jsonify({'error': '無效的伺服器選擇'}), 400
            
            upload_result = generator.upload_patient_data_to_server(patient_data, server_url)
            result['upload'] = {
                'success': bool(upload_result["patient"]),
                'server_url': server_url,
                'patient_id': upload_result["patient"],
                'uploaded_conditions': len(upload_result['conditions']),
                'uploaded_observations': len(upload_result['observations']),
                'uploaded_medications': len(upload_result['medications']),
                'uploaded_medication_requests': len(upload_result['medication_requests']),
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
