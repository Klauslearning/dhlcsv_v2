import streamlit as st
import pandas as pd
from utils import get_memory_values, save_sku_memory
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
        "Selling", "Currency", "Country of Origin", "Weight", "Commodity Code"
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    # Apply memory logic with enhanced matching
    st.subheader("🔍 智能记忆填充")
    memory_status = st.empty()
    
    for idx, row in df.iterrows():
        sku = str(row.get('SKU', '')).strip()
        brand = str(row.get('Brand', '')).strip()
        item_desc = str(row.get('Item Description', '')).strip()
        
        if sku or brand or item_desc:
            memory_values = get_memory_values(sku, brand, item_desc)
            
            # Apply memory values if fields are empty
            if not row.get("Country of Origin"):
                df.at[idx, "Country of Origin"] = memory_values['country']
            if not row.get("Weight"):
                df.at[idx, "Weight"] = memory_values['weight']
            if not row.get("Commodity Code"):
                df.at[idx, "Commodity Code"] = memory_values['commodity_code']
    
    memory_status.success("✅ 智能记忆填充完成！系统已自动填充已知商品的编码、重量和产地信息。")

    # Display editable table
    st.subheader("📝 编辑表格")
    st.info("💡 提示：手动编辑任何字段后，系统会自动记住这些值，下次遇到相同商品时会自动填充。")
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        num_rows="dynamic",
        column_config={
            "Commodity Code": st.column_config.TextColumn(
                "海关编码",
                help="输入海关商品编码 (HS Code)"
            ),
            "Weight": st.column_config.NumberColumn(
                "重量 (kg)",
                help="商品重量，单位：公斤",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.3f"
            ),
            "Country of Origin": st.column_config.SelectboxColumn(
                "产地",
                help="选择商品原产国",
                options=["", "CN", "IT", "FR", "US", "GB", "DE", "JP", "KR", "TH", "VN", "IN", "TR", "ES", "PT", "NL", "BE", "CH", "AT", "SE", "NO", "DK", "FI", "PL", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "EE", "LV", "LT", "MT", "CY", "LU", "IE", "GR"]
            )
        }
    )

    # Export CSV (DHL format)
    if st.button("📤 导出 DHL 格式 CSV"):
        dhl_columns = [
            "Unique Item Number", "Item", "Item Description", "Commodity Code", "Quantity",
            "Units", "Value", "Currency", "Weight", "Weight 2", "Country of Origin",
            "Reference Type", "Reference Details", "Tax Paid"
        ]
        export_df = pd.DataFrame(columns=dhl_columns)

        # Track what needs to be saved to memory
        memory_updates = []

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

            # Prepare memory update
            memory_updates.append({
                'sku': str(row.get('SKU', '')).strip(),
                'brand': str(row.get('Brand', '')).strip(),
                'item_desc': str(row.get('Item Description', '')).strip(),
                'commodity_code': str(row.get('Commodity Code', '')).strip(),
                'weight': str(row.get('Weight', '')).strip(),
                'country': str(row.get('Country of Origin', '')).strip()
            })

        # Save all memory updates
        for update in memory_updates:
            if update['sku'] or update['brand'] or update['item_desc']:
                save_sku_memory(
                    sku=update['sku'],
                    brand=update['brand'],
                    item_description=update['item_desc'],
                    commodity_code=update['commodity_code'] if update['commodity_code'] else None,
                    weight=update['weight'] if update['weight'] else None,
                    country=update['country'] if update['country'] else None
                )

        # Convert to CSV and download
        csv_data = export_df.to_csv(index=False, header=False)
        st.download_button(
            label="📥 下载 DHL CSV 文件",
            data=csv_data,
            file_name="dhl_output.csv",
            mime="text/csv"
        )
        
        st.success("✅ CSV 文件已生成！所有编辑的数据已保存到智能记忆中。")

# Display memory database info
if st.sidebar.checkbox("📊 显示记忆数据库信息"):
    st.sidebar.subheader("智能记忆数据库")
    
    if os.path.exists("data/sku_memory_db.csv"):
        memory_df = pd.read_csv("data/sku_memory_db.csv")
        if not memory_df.empty:
            st.sidebar.write(f"📈 已记忆商品数量: {len(memory_df)}")
            st.sidebar.write("📋 记忆字段:")
            st.sidebar.write("• 海关编码 (Commodity Code)")
            st.sidebar.write("• 重量 (Weight)")
            st.sidebar.write("• 产地 (Country of Origin)")
            
            if st.sidebar.button("🗑️ 清空记忆数据库"):
                os.remove("data/sku_memory_db.csv")
                st.sidebar.success("记忆数据库已清空！")
                st.rerun()
        else:
            st.sidebar.write("📝 记忆数据库为空")
    else:
        st.sidebar.write("📝 记忆数据库尚未创建")