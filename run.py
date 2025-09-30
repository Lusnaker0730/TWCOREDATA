#!/usr/bin/env python3
"""
台灣 FHIR 病人資料生成器 - 啟動腳本
Taiwan FHIR Patient Data Generator - Startup Script

使用方法 / Usage:
    python run.py          # 啟動Web界面 / Start Web UI
    python run.py --cli     # 使用命令列模式 / Use CLI mode
    python run.py --help    # 顯示幫助 / Show help
"""

import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='台灣 FHIR 病人資料生成器 / Taiwan FHIR Patient Data Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例 / Examples:
  python run.py                    # 啟動Web界面 (預設)
  python run.py --web              # 啟動Web界面
  python run.py --cli              # 使用命令列模式
  python run.py --port 8080        # 指定Web伺服器埠號
  python run.py --host 0.0.0.0     # 允許外部連線
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true', 
        default=True,
        help='啟動Web界面 (預設) / Start Web UI (default)'
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='使用命令列模式 / Use command line interface'
    )
    
    parser.add_argument(
        '--host', 
        default='localhost',
        help='Web伺服器主機位址 (預設: localhost) / Web server host (default: localhost)'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Web伺服器埠號 (預設: 5000) / Web server port (default: 5000)'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='啟用除錯模式 / Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # 檢查必要檔案是否存在
    required_files = [
        'app.py',
        'generate_TW_patients.py', 
        'config_loader.py',
        'config/conditions.json',
        'config/observations.json',
        'config/medications.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要檔案 / Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n請確保所有檔案都在正確位置 / Please ensure all files are in the correct location")
        sys.exit(1)
    
    # 確保輸出目錄存在
    output_dirs = [
        'output',
        'output/complete_patients_fixed',
        'output/custom_patients'
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    if args.cli:
        print("🏥 啟動命令列模式 / Starting CLI mode...")
        print("=" * 50)
        
        # 導入並執行命令列版本
        try:
            from generate_TW_patients import main as cli_main
            cli_main()
        except KeyboardInterrupt:
            print("\n\n👋 程式已停止 / Program stopped")
        except Exception as e:
            print(f"\n❌ 執行錯誤 / Execution error: {e}")
            sys.exit(1)
            
    else:
        print("🌐 啟動Web界面 / Starting Web UI...")
        print("=" * 50)
        print(f"🏠 主機位址 / Host: {args.host}")
        print(f"🔌 埠號 / Port: {args.port}")
        print(f"🌍 網址 / URL: http://{args.host}:{args.port}")
        print(f"🐛 除錯模式 / Debug mode: {'啟用' if args.debug else '停用'} / {'Enabled' if args.debug else 'Disabled'}")
        print("⏹️  按 Ctrl+C 停止伺服器 / Press Ctrl+C to stop server")
        print()
        
        # 導入並執行Web版本
        try:
            import app
            app.app.run(
                host=args.host,
                port=args.port,
                debug=args.debug
            )
        except KeyboardInterrupt:
            print("\n\n👋 伺服器已停止 / Server stopped")
        except Exception as e:
            print(f"\n❌ 伺服器錯誤 / Server error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
