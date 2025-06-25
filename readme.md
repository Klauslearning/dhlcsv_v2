

# 📦 DHL CSV 自动生成工具（Streamlit 版本）

一个面向个人代购/品牌代理的实用工具，支持从 Excel/Numbers 文件中提取商品信息，自动生成 DHL 上传所需的发货 CSV 文件，符合其标准格式要求。支持记忆功能（自动填写商品重量和产地），支持手动修改并导出。

---

## 🚀 功能特点

- ✅ 上传 Excel 或 Numbers 导出表格（`.xlsx` 格式）
- ✅ 自动填充 DHL 所需字段：Item Description、Quantity、Value、Weight、Country of Origin 等
- ✅ 内置智能记忆系统：基于 SKU/品牌/描述自动匹配【原产国】与【重量】
- ✅ 支持前端手动编辑、即时保存到数据库（CSV）
- ✅ 一键导出 DHL 可读格式的 CSV（无表头）
- ✅ 无需登录、无服务器，仅用 Streamlit Cloud 即可部署

---

## 🧰 技术栈

- `Python 3.8+`
- `pandas`
- `streamlit`
- `openpyxl`

---

## 📁 项目结构

```
.
├── app.py                  # 主应用入口（Streamlit UI）
├── utils.py                # SKU记忆逻辑（原产地+重量）
├── requirements.txt        # Python依赖
├── .streamlit/
│   └── config.toml         # Cloud运行配置
├── data/
│   └── sku_memory_db.csv   # 自动记忆数据库
└── README.md               # 当前说明文件
```

---

## 🔧 本地运行方法

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/DHLCSV_StreamlitApp.git
cd DHLCSV_StreamlitApp

# 安装依赖
pip install -r requirements.txt

# 启动程序
streamlit run app.py
```

---

## ☁️ Streamlit Cloud 部署指南

1. 将本项目上传 GitHub
2. 打开 [streamlit.io/cloud](https://streamlit.io/cloud)，点击 **“New App”**
3. 选择你的 repo → `branch: main` → `main file: app.py`
4. 点击 Deploy 即可在线访问工具页面

---

## 📥 输入文件格式要求

| 字段名             | 必须 | 说明                       |
|--------------------|------|----------------------------|
| SKU                | 否   | 商品编号（可选）           |
| Brand              | 否   | 品牌名（可选）             |
| Item Description   | ✅   | 商品描述                   |
| Quantity           | ✅   | 数量                       |
| Units              | ✅   | 单位，如 `EA`, `PCS` 等    |
| Selling            | ✅   | 单价                       |
| Currency           | 否   | 默认 `GBP`                 |
| Commodity Code     | 否   | 海关编码（可留空）         |
| Country of Origin  | 否   | 原产地（支持记忆）         |
| Weight             | 否   | 重量（支持记忆/估算）      |

---

## 📤 输出文件示例（DHL CSV）

```csv
1,INV_ITEM,LV Handbag M46234,4202210010,1,EA,1200,GBP,0.8,,CN,,, 
```

---

## 📌 注意事项

- 系统会记住用户填写的每个 SKU+品牌+描述 对应的产地和重量，自动补全
- 文件导出时 **不包含表头**，符合 DHL 上传要求
- 请确保上传 `.xlsx` 文件（Numbers 可导出）

---


## 🗺️ 项目部署流程图解

```mermaid
flowchart TD
    A[上传商品表格] --> B[前端读取 Excel 数据]
    B --> C{是否已有 SKU/描述 记忆}
    C -- 是 --> D[自动填入国家和重量]
    C -- 否 --> E[留空，等待用户输入]
    D & E --> F[用户前端补充 & 编辑]
    F --> G[点击“导出 DHL CSV”]
    G --> H[生成无表头 CSV 文件]
    H --> I[可上传至 DHL 官网]

## 📫 联系与贡献

欢迎提 issue 或 pull request 来完善此工具。  
项目作者：`@Klauslearning`