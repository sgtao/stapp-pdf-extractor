# stapp-pdf-extractor
- [streamlit](https://streamlit.io/)でPDFファイルから情報抽出する

## Usage
- [poetry cli](https://python-poetry.org/docs/)を利用する

### Setup
```sh
poetry install

# start poetry virtual env.
## poetry shell # for poetry 1.x version

## Bash/Zsh/Csh # for poetry 2.x version
eval $(poetry env activate)

## Powershell
Invoke-Expression (poetry env activate)
## Fish
eval (poetry env activate)

# when finish poetry virtual env.
deactivate
```

### コマンド一覧
- [pyproject.toml](./pyproject.toml) の `[tool.taskipy.tasks]` 定義より：
```sh
$ task --list
run                 streamlit run src/main.py
test                pytest tests
test-cov            pytest tests --cov --cov-branch -svx
test-report         pytest tests --cov --cov-report=html
format              black --line-length 79 src
lint                flake8 src
check-format        run lint check after format
export-requirements export requirements.txt file
export-req-with-dev export requirements-dev.txt file
rm-dist             remove build and dist directory
make-dist           make distribution package
```

### Start as local service
```sh
# on poetry env.
# streamlit hello
task run
# streamlit run src/main.py
# Local URL: http://localhost:8501
```


### format and lint check
```sh
# task format
# task lint
task check-format
```


### Test with `pytest`
- [streamlitのテスト手法](https://docs.streamlit.io/develop/concepts/app-testing/get-started)を参考にテストを実施
```sh
# on poetry env
# pytest tests/test_main.py
task test
```

### Test coverage

#### show c1 coverage
```sh
# on poetry env
task test-cov
```

#### output HTML coverage report
```sh
# on poetry env
task test-report
```

### Export `requirements.txt` file

- export `requirements.txt` file of only `[tool.poetry.dependencies]` packages
```sh
# on poetry env
task export-requirements
```

- export `requirements.txt` file of `[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]` packages
```sh
# on poetry env
task export-req-with-dev
```

### Build Docker image and run
```sh
# Build Docker image
sudo task docker-build

# run docker container
sudo task docker-run
```

#### priviredge setting:
- to execute docker command without sudo, set following:
```sh
sudo usermod -aG docker $USER
newgrp docker
```

### make packages
- make package file under dist for run stapp without Python
```sh
# make distribution package on poetry env
task make-dist
```

- clear package
```sh
# remove distribution package on poetry env
task rm-dist
```

- run package
```sh
# run package without poetry env
./dist/run_stapp/run_stapp
```

## 使用ライブラリ

このプロジェクトは以下のオープンソースライブラリを使用しています：

- [Streamlit](https://streamlit.io/) - Apache License 2.0

  Copyright © 2019-2024 Streamlit Inc.

  Streamlitは、データアプリケーションを簡単に作成するためのオープンソースライブラリです。


## ライセンス
MIT License

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](./LICENSE) ファイルをご覧ください。

ただし、このプロジェクトは Apache License 2.0 でライセンスされている Streamlit を使用しています。
Streamlit のライセンス全文は [こちら](https://github.com/streamlit/streamlit/blob/develop/LICENSE) でご確認いただけます。
