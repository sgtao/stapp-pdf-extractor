# run_stapp.py
import os
import sys

from streamlit.web import cli

def streamlit_run():
    # mainスクリプトへの相対パスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")

    # streamlit runコマンドをエミュレート
    sys.argv = ["streamlit", "run", main_script]
    sys.exit(cli.main())


if __name__ == "__main__":
    streamlit_run()