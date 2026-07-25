# DeepFaceLab - Web UI

在 [iperov/DeepFaceLab](https://github.com/iperov/DeepFaceLab) 基础上构建的 Web 界面版本。

原始 DeepFaceLab 引擎完整保留在 `engine/` 目录中，依然支持命令行使用。本项目的目标是为其增加 Web 操作界面。

## 项目结构

```
├── main.py           # Web UI 入口
├── ui/               # FastAPI Web UI (app, api, static)
├── engine/           # DeepFaceLab 原始源码
│   ├── main.py       # 原始命令行入口
│   ├── core/         # 神经网络库 (leras)、图像处理、多进程工具
│   ├── models/       # 换脸模型 (SAEHD, AMP, Quick96, XSeg)
│   └── ...
└── pyproject.toml    # uv 项目配置
```

## 快速开始

### 环境要求
- Python >= 3.6（完整引擎支持需要 <= 3.8）
- NVIDIA GPU + CUDA（训练与推理）
- [uv](https://docs.astral.sh/uv/) 包管理器

### 安装运行

```bash
# 克隆并初始化环境
git clone git@github.com:zhang-luming/DeepFaceLab.git
cd DeepFaceLab

# 创建虚拟环境并安装依赖
uv sync

# 启动 Web UI
uv run python main.py
```

浏览器访问 `http://localhost:8000`。

### 命令行使用（仅引擎）

原始 DeepFaceLab 命令行依旧可用：

```bash
python engine/main.py extract --input-dir data_src --output-dir data_src/aligned
python engine/main.py train --model SAEHD --model-dir model --training-data-src-dir data_src/aligned --training-data-dst-dir data_dst/aligned
python engine/main.py merge --model SAEHD --model-dir model --input-dir data_dst --output-dir result --output-mask-dir result_mask
```

## 开发

```bash
uv run python main.py          # 启动开发服务器
```

API 路由添加在 `ui/api/` 目录下，然后在 `ui/app.py` 中注册。

## 致谢

基于 [DeepFaceLab](https://github.com/iperov/DeepFaceLab) (iperov) 构建。
