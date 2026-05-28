#!/bin/bash
# ============================================================
# 下载 paraformer-zh 语音识别模型（FunASR Paraformer-large）
# ============================================================
# ModelScope 链接:
#   https://www.modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
# HuggingFace 镜像:
#   https://huggingface.co/funasr/paraformer-zh
# ============================================================

set -e

TARGET_DIR="$(cd "$(dirname "$0")/../src/robot_slam/scripts/paraformer-zh" && pwd)"
mkdir -p "$TARGET_DIR"

echo "=== 下载 paraformer-zh 模型 ==="
echo "目标目录: $TARGET_DIR"
echo ""
echo "方式1: 从 ModelScope 下载 (推荐，国内快)"
echo "  git clone https://www.modelscope.cn/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch.git"
echo "  # 然后将 model.pt, tokens.json, am.mvn, seg_dict, config.yaml, configuration.json 复制到:"
echo "  # $TARGET_DIR"
echo ""
echo "方式2: 从 HuggingFace 下载"
echo "  git clone https://huggingface.co/funasr/paraformer-zh"
echo "  # 同上复制文件"
echo ""
echo "方式3: 使用 Python 自动下载"
echo "  pip install funasr modelscope"
echo "  python3 -c \"from funasr import AutoModel; AutoModel(model='iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch', model_revision='v2.0.4')\""
echo ""
echo "所需文件清单:"
echo "  - model.pt           (~1.7GB PyTorch 模型权重)"
echo "  - tokens.json         (词表)"
echo "  - am.mvn              (均值方差归一化)"
echo "  - seg_dict            (分词字典)"
echo "  - config.yaml         (模型配置)"
echo "  - configuration.json  (FunASR 配置)"
echo ""
echo "=== 下载完成后的目录结构 ==="
echo "$TARGET_DIR/"
echo "  ├── model.pt"
echo "  ├── tokens.json"
echo "  ├── am.mvn"
echo "  ├── seg_dict"
echo "  ├── config.yaml"
echo "  └── configuration.json"
