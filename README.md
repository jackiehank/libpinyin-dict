# libpinyin-dict 词典生成工具

[![License: MPL-2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

> 此项目基于 [libpinyin-dict](https://github.com/broly8/libpinyin-dict)  fork 并改进，主要添加了中文分词和批量处理功能。

## 主要改进
- 获取 pinyin 由 web 方式改为本地 pypinyin 库
- 新增中文自动分词功能
- 支持目录批量处理

## 功能特点

- **中文分词**：自动从文本文件中提取中文词汇
- **拼音标注**：自动为中文词汇生成拼音
- **格式转换**：生成符合 ibus-libpinyin 格式的词典文件
- **批量处理**：支持单个文件和批量文件处理
- **智能过滤**：自动过滤非中文内容，确保词典纯净

## 环境要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - 快速的Python包管理器和安装器

## 快速开始

### 1. 安装 uv

```bash
# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 获取项目

```bash
git clone https://github.com/jackiehank/libpinyin-dict.git
cd libpinyin-dict
```

### 3. 安装依赖

```bash
uv sync
```

## 使用方法

### 基本工作流程

1. **准备原始文本文件** → 2. **中文分词处理** → 3. **生成拼音词典**

### 步骤1：准备原始文本

将包含中文内容的文本文件（支持 `.txt`, `.md`, `.csv`, `.json`, `.xml`, `.html` 格式）放在项目目录中。

### 步骤2：运行中文分词

```bash
# 处理单个文件
uv run chinese_segmenter.py document.txt

# 处理整个目录（自动合并结果）
uv run chinese_segmenter.py /path/to/documents/

# 递归处理子目录
uv run chinese_segmenter.py /path/to/documents/ -r

# 指定输出目录
uv run chinese_segmenter.py input.txt -o custom_output/
```

处理后的文件将保存在 `raw/` 目录中，包含提取的纯中文词汇。

### 步骤3：生成拼音词典

```bash
uv run fetch_pinyin.py
```

脚本会自动读取 `raw/` 目录中的所有文件，生成带拼音的词典文件，并保存在 `raw/result/` 目录中。

## 输出格式

生成的词典文件格式如下：

```
中国 zhong'guo
美国 mei'guo 49.9999
德国 de'guo 97.0
```

- 第一列：中文词汇
- 第二列：拼音（使用 `'` 分隔多音字）
- 第三列（可选）：词频权重
- 第四列（可选）：注释

## 高级选项

### 中文分词器选项

```bash
# 显示帮助信息
uv run chinese_segmenter.py -h

# 目录处理时不合并输出（每个文件单独输出）
uv run chinese_segmenter.py docs/ --no-merge

# 显示详细信息
uv run chinese_segmenter.py input.txt -v

# 查看版本信息
uv run chinese_segmenter.py --version
```

### 支持的输入文件格式

- 文本文件：`.txt`
- Markdown：`.md`
- 数据文件：`.csv`, `.json`
- 网页文件：`.xml`, `.html`, `.htm`

## 项目结构

```
libpinyin-dict/
├── chinese_segmenter.py    # 中文分词脚本
├── fetch_pinyin.py         # 拼音生成脚本
├── raw/                    # 分词结果目录
│   └── result/            # 最终词典文件目录
├── release/                # 原项目词典
├── pyproject.toml         # 项目配置和依赖
└── README.md              # 说明文档
```

## 故障排除

### 常见问题

1. **文件编码错误**
   - 确保所有文本文件使用 UTF-8 编码

2. **没有找到中文词汇**
   - 检查输入文件是否包含有效的中文内容
   - 确认文件格式受支持

3. **权限问题**
   - 确保对输入文件和输出目录有读写权限

### 获取帮助

如果遇到问题，可以：

1. 使用 `-v` 参数查看详细输出
2. 检查输入文件格式和编码
3. 确认所有依赖已正确安装

## 技术细节

- 使用 `jieba` 库进行中文分词
- 使用 `pypinyin` 库进行拼音转换
- 支持多种文本编码和文件格式
- 自动处理重名文件和重复词汇

## 许可证

本项目基于 Mozilla Public License 2.0 发布。

### 版权声明
- 原始代码版权归 [broly8](https://github.com/broly8) 所有
- 修改和改进版权归 [jackiehank](https://github.com/jackiehank)所有

此 Source Code Form 受 Mozilla Public License, v. 2.0 条款约束。
如果未随此文件分发 MPL 的副本，您可以在 http://mozilla.org/MPL/2.0/ 获取。

## 版权声明

我们尊重知识产权。如果您认为本项目侵犯了您的合法权益，请通过电子邮件联系我们。

此分支维护者: jackiehank(at)163
原始作者: suokunlong@126点com

---

Happy typing! 🎉