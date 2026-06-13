# 🩺 MedExamAgent

**AI 驱动的医学复习考点生成器**  
上传课程 PPT 和教材 PDF，自动提炼 **选择题、名词解释、大题、临床案例分析** 等结构化考点，帮你高效备考。

---

## ✨ 核心特性

- **多格式支持**：PPT 和 PDF 讲义均可上传，每个文件视为一个独立章节。
- **智能章节匹配**：自动通过教材书签 → 文字章节标题 → TF‑IDF 语义匹配，将讲义精准对应到教材段落。
- **五板块考点输出**：
  1. 📋 **知识框架**（基于 PPT 的层级梳理，结合执业医师等真题考点，标注重点难点）
  2. 📝 **考点复现**（选择题、名词解释、简答论述答题要点）
  3. 🏥 **案例分析**（AI 自编典型病例，含诊断思路和思考题）
  4. 🧠 **能力拓展**（临床思维、常见误区、真题切入点）
  5. 🔒 **内置自洽性验证**（模型自动检查答案一致性，防止前后矛盾）
- **知识融合规则**：以教材为准，PPT 补充，AI 仅补充公认的医学常识和考试经验。
- **纯本地运行**：数据不上传云端，仅调用 DeepSeek API 进行推理（传输的仅为讲义和教材文本，不包含用户隐私）。
- **精美界面**：科技感粒子背景 + 留白卡片设计，支持移动端响应式布局。
- **一键启动**：提供 `start.sh`（macOS/Linux）和 `start.bat`（Windows）脚本。

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.9 或更高版本
- 稳定的网络连接（用于访问 DeepSeek API）

### 2. 克隆项目
```bash
git clone https://github.com/Aisling-Huang/MedExamAgent-v1.0.git
cd MedExamAgent
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 获取 DeepSeek API Key
- 访问 [https://platform.deepseek.com](https://platform.deepseek.com) 注册并获取 Key（以 `sk-` 开头）
- 注意：Key 仅保存在你的本地，不会被上传或记录

### 5. 启动程序

- **Windows**：双击 `start.bat`
- **macOS / Linux**：在终端执行 `chmod +x start.sh && ./start.sh`

脚本会自动启动后端 API 和前端页面，并打开浏览器访问 `http://localhost:3000/app.html`。

> 如果你需要手动启动：  
> 终端1：`uvicorn api:app --host 127.0.0.1 --port 8000`  
> 终端2：`python3 -m http.server 3000 --bind 127.0.0.1`  
> 然后访问 `http://localhost:3000/app.html`

---

## 📖 使用方法

1. 在界面左侧填写 **DeepSeek API Key**。
2. 点击 **“添加课程 PPT / PDF 讲义”**，可多次点击上传多个文件（每个文件作为一个章节）。
3. 点击 **“上传教材 PDF”**，选择对应的参考教材。
4. 点击 **“🚀 开始生成考点”**，等待处理完成。
5. 在上方标签页切换章节，查看五板块考点内容。
6. 点击 **“📥 下载全部考点”** 可将所有内容保存为 Markdown 文件。

---

## 📁 项目结构

```
MedExamAgent/
├── preview.html              # 封面入口页
├── app.html                  # 功能主页面
├── api.py                    # FastAPI 后端
├── requirements.txt          # Python 依赖
├── config.yaml.example       # 配置文件模板（不包含真实 Key）
├── start.sh / start.bat      # 一键启动脚本
├── README.md
├── LICENSE
└── src/
    ├── extractors.py         # PPT/PDF 文本提取
    ├── generator.py          # 考点生成（含防幻觉 & 自洽机制）
    ├── utils.py              # 章节匹配、TF‑IDF 等工具
    └── main.py               # 命令行入口（可选）
```

---

## 🔒 隐私说明

- **所有文件处理均在本地完成**，教材和讲义**不会上传到任何云端**。
- 考点生成时，程序会将你上传的 PPT/教材文本发送到 DeepSeek API（`api.deepseek.com`），仅用于本次推理。  
  DeepSeek 官方声明 **不会将 API 调用数据用于模型训练**。
- 你的 API Key 仅用于本次请求，程序**不会记录、存储或上传**。
- 我们强烈建议：**不要上传包含真实患者隐私信息的文件**。

---

## ⚠️ 注意事项

- 本工具生成的考点**仅供学习参考**，不构成任何医学建议。所有临床决策应以权威教材、指南及主治医师意见为准。
- 如果你使用的教材受版权保护，请确保仅在个人学习范围内使用。
- 目前模型完全基于 DeepSeek 内置知识生成内容，**不进行联网搜索**，因此不会获取最新指南或新闻。如需最新信息，请自行查阅权威来源。

---

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request 帮助改进项目。  
如果你觉得有用，请给一个 ⭐ Star～

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE)。
