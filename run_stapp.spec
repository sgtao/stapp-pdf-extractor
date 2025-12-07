# -*- mode: python ; coding: utf-8 -*-
# run_stapp.spec - PyInstallerの設定ファイル
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

"""
Streamlit関連の依存関係を自動収集:
- streamlit_hidden_imports: Streamlitの全サブモジュールを取得
- streamlit_data: Streamlitの必要なデータファイルを取得
"""
streamlit_hidden_imports = collect_submodules("streamlit")
streamlit_data = collect_data_files("streamlit")

# Analysis: アプリケーションの依存関係を分析し、必要なファイルを特定
a = Analysis(
    ["run_stapp.py"], # エントリーポイントとなるPythonスクリプト
    pathex=[],    # Pythonのインポートパスに追加するパス
    binaries=[],  # 必要なバイナリファイル（DLLなど）
    datas=[ # データファイルとその配置先を指定
        ("src/pages", "pages"),
        ("src/ui", "ui"),
        ("src/logic", "logic"),
        ("src/main.py", "."),  # メインスクリプト
    ]
    + streamlit_data,  # Streamlitのデータファイルを追加
    hiddenimports=[ # 明示的にインポートが必要なモジュールを指定
        "streamlit",
        "streamlit.web.cli",
        "src.ui.spiral_chart",
        "src.logic.calculations",
        # 以下は、Streamlitの依存パッケージ
        "altair",
        "pandas",
        "numpy",
        "plotly",
        "pillow",
        "packaging",
        "importlib_metadata",
        "validators",
        "tornado",
        "watchdog",
        "click",
        "rich",
        "protobuf",
    ]
    + streamlit_hidden_imports, # Streamlitの全サブモジュールを追加
    hookspath=["./hooks"],  # カスタムフックスクリプトのパス
    hooksconfig={},   # フックの設定
    runtime_hooks=[], # 実行時フックスクリプト
    excludes=[],      # 除外するモジュール
    noarchive=False,  # True: PYZアーカイブを作成しない
    optimize=0, # Pythonの最適化レベル（0-2）
)

# PYZ: Pythonモジュールをzip形式にアーカイブ化
pyz = PYZ(a.pure)

# EXE: 実行ファイルの設定
exe = EXE(
    pyz,  # PYZアーカイブ
    a.scripts,  # スクリプト
    [], # 追加のスクリプト
    exclude_binaries=True,  # True: バイナリファイルを別ディレクトリに配置
    name="run_stapp", # 出力される実行ファイルの名前
    debug=False,  # デバッグ情報を含めるか
    bootloader_ignore_signals=False,  # ブートローダーのシグナル処理
    strip=False,  # シンボル情報の削除
    upx=True, # UPXによる圧縮を有効化
    console=True, # コンソールウィンドウを表示
    disable_windowed_traceback=False, # ウィンドウモードでのトレースバック
    argv_emulation=False, # コマンドライン引数のエミュレーション
    target_arch=None, # ターゲットアーキテクチャ
    codesign_identity=None, # コード署名の識別子
    entitlements_file=None, # エンタイトルメントファイル
)

# COLLECT: 実行に必要な全ファイルを収集
coll = COLLECT(
    exe,  # 実行ファイル
    a.binaries, # バイナリファイル
    a.datas,  # データファイル
    strip=False,  # シンボル情報の削除
    upx=True, # UPXによる圧縮を有効化
    upx_exclude=[],   # UPX圧縮から除外するファイル
    name="run_stapp", # 出力ディレクトリ名
)
