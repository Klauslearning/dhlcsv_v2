

import streamlit as st
import pandas as pd
from utils import load_sku_memory, save_sku_memory
import os

# App title
st.set_page_config(page_title="DHL CSV Generator", layout="wide")
st.title("📦 DHL CSV 文件自动生成器")

# File uploader
uploaded_file = st.file_uploader("上传 Excel 或 Numbers 文件", type=["xlsx", "xls", "numbers"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Add required columns if missing
    required_columns = [
        "SKU", "Brand", "Item Description", "Quantity", "Units",
        "Selling", "Currency", "Country of Origin", "Weight"
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    # Load memory
    memory = load_sku_memory()

    # Apply memory logic
    for idx, row in df.iterrows():
        key = f"{row['SKU']}_{row['Brand']}_{row['Item Description']}".strip()
        if not row.get("Country of Origin"):
            df.at[idx, "Country of Origin"] = memory.get(key, {}).get("Country", "")
        if not row.get("Weight"):
            df.at[idx, "Weight"] = memory.get(key, {}).get("Weight", "")

    # Display editable table
    st.subheader("📝 编辑表格")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    # Export CSV (DHL format)
    if st.button("📤 导出 DHL 格式 CSV"):
        dhl_columns = [
            "Unique Item Number", "Item", "Item Description", "Commodity Code", "Quantity",
            "Units", "Value", "Currency", "Weight", "Weight 2", "Country of Origin",
            "Reference Type", "Reference Details", "Tax Paid"
        ]
        export_df = pd.DataFrame(columns=dhl_columns)

        for i, row in edited_df.iterrows():
            export_df.loc[i] = [
                1,
                "INV_ITEM",
                row["Item Description"],
                row.get("Commodity Code", ""),
                row["Quantity"],
                row["Units"],
                row["Selling"],
                row.get("Currency", "GBP"),
                row["Weight"],
                "",  # Weight 2 - always blank
                row["Country of Origin"],
                "", "", ""  # Reference Type / Details / Tax Paid
            ]

            # Save new memory
            if row["Country of Origin"] or row["Weight"]:
                save_sku_memory(
                    row["SKU"],
                    row["Brand"],
                    row["Item Description"],
                    country=row.get("Country of Origin", ""),
                    weight=row.get("Weight", "")
                )

        # Convert to CSV and download
        st.download_button(
            label="📥 下载 DHL CSV 文件",
            data=export_df.to_csv(index=False, header=False),
            file_name="dhl_output.csv",
            mime="text/csv"
        )