#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:44:33 2026

@author: trieukimlanh
streamlit run "/Users/trieukimlanh/Library/CloudStorage/GoogleDrive-lanhtk@hub.edu.vn/My Drive/Spyder/app/macro ver1.py"
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# ĐƯỜNG DẪN MẶC ĐỊNH ĐẾN GOOGLE SHEET (Nhiều Sheet tương tự Excel)
# ==============================================================================
# Thay mã ID Google Sheet thực tế của bạn vào đoạn '1A_B_C_D_XYZ' dưới đây
# Link gốc của bạn: "https://docs.google.com/spreadsheets/d/1jOUPOExIVzdfVWTYqHdDTodH05WdQEb7/edit?gid=72263712#gid=72263712"

# Đường dẫn đã được sửa đổi để tự động xuất toàn bộ các sheet thành file Excel (.xlsx):
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1jOUPOExIVzdfVWTYqHdDTodH05WdQEb7/export?format=xlsx"

# 1. CẤU HÌNH TRANG STREAMLIT
st.set_page_config(
    page_title="Macroeconomic Data Viewer", 
    page_icon="📈", 
    layout="wide"
)

st.title("📈 Macroeconomic Data Viewer")
st.subheader("=====TRIỆU KIM LANH=====")
st.markdown("Bước 1: Hệ thống tự động nạp dữ liệu từ Google Sheet mặc định. Bạn cũng có thể tải file Excel khác để thay thế.")
st.markdown("Bước 2: Chọn chỉ tiêu phân tích ở thanh bên (Sidebar) để xem các đồ thị tương ứng.")

# ==============================================================================
# SIDEBAR: UPLOAD FILE VÀ LỌC THỜI GIAN
# ==============================================================================
st.sidebar.header("🔌 Nguồn dữ liệu")
uploaded_file = st.sidebar.file_uploader(
    "Tải lên file dữ liệu mới để thay thế (Data_colab.xlsx)", 
    type=["xlsx"]
)

# ==============================================================================
# QUY TRÌNH ĐỌC VÀ CHUẨN HÓA DỮ LIỆU
# ==============================================================================
@st.cache_data
def load_and_process_data(file_or_url):
    try:
        # pd.read_excel có thể đọc trực tiếp cả file upload hoặc link URL xuất khẩu xlsx
        df_dict = pd.read_excel(file_or_url, sheet_name=None)
        
        # Ánh xạ tên các sheet tương ứng với cấu hình của bạn
        sheets_mapping = {
            'vnibor_q': 'vnibor_q', 'vnibor': 'vnibor', 'bond_y_q': 'bond_y_q','bond_y_m': 'bond_y_m',
            'ex_d': 'ex_d', 'ls1': 'ls1','ls2': 'ls2', 'credit': 'credit', 'm2': 'm2',
            'ls_wui': 'ls_wui', 'omo': 'omo', 'macro': 'macro', 'inf': 'inf'
        }
        
        processed_data = {}
        for key, sheet_name in sheets_mapping.items():
            if sheet_name in df_dict:
                df_sheet = df_dict[sheet_name].copy()
                # Đồng bộ tên cột ngày/date sang 'Date' để dễ quản lý
                date_col = 'date' if 'date' in df_sheet.columns else 'Ngày'
                
                if date_col in df_sheet.columns:
                    df_sheet['Date'] = pd.to_datetime(df_sheet[date_col])
                    df_sheet = df_sheet.sort_values('Date')
                    processed_data[key] = df_sheet

        # =====================================================================
        # LOGIC XỬ LÝ ĐẶC BIỆT CHO BOND_Y_M: Lấy ngày cuối cùng của mỗi tháng
        # =====================================================================
        if 'bond_y_m' in processed_data:
            df_bond_raw = processed_data['bond_y_m']
            # Tạo cột phụ lưu thông tin Năm-Tháng để gom nhóm
            df_bond_raw['Year_Month'] = df_bond_raw['Date'].dt.to_period('M')
            # Lấy dòng có ngày lớn nhất (ngày cuối cùng có dữ liệu) trong mỗi tháng
            df_bond_monthly = df_bond_raw.loc[df_bond_raw.groupby('Year_Month')['Date'].idxmax()]
            # Loại bỏ cột phụ để sạch dữ liệu
            df_bond_monthly = df_bond_monthly.drop(columns=['Year_Month']).sort_values('Date')
            # Ghi đè lại dữ liệu đã xử lý theo tháng vào dictionary
            processed_data['bond_y_m'] = df_bond_monthly
        
        return processed_data
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")
        return None

# ==============================================================================
# QUYẾT ĐỊNH NGUỒN DỮ LIỆU: ƯU TIÊN FILE UPLOAD -> NẾU TRỐNG THÌ DÙNG GOOGLE SHEET
# ==============================================================================
if uploaded_file is not None:
    # Nếu người dùng tải file lên, app sẽ đọc từ file excel đó
    data = load_and_process_data(uploaded_file)
    source_status = "🎯 Nạp dữ liệu từ file Excel tải lên thành công!"
else:
    # Ngược lại, khi vừa mở app hoặc không chọn file, app tự động lấy từ Google Sheet
    data = load_and_process_data(GOOGLE_SHEET_URL)
    source_status = "🌐 Tự động đồng bộ dữ liệu từ Google Sheet trực tuyến!"

# ==============================================================================
# GIAO DIỆN CHÍNH SAU KHI CÓ DỮ LIỆU
# ==============================================================================
if data:
    st.sidebar.success(source_status)
    
    # CHUYỂN ĐỔI TỪ TABS SANG RADIO BUTTON TRÊN SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Chọn phân hệ chỉ tiêu")
    
    # [Giữ nguyên toàn bộ phần mã logic điều hướng và vẽ đồ thị phía sau của bạn...]
    # --- CẤU HÌNH NỘI DUNG HELP CHO TỪNG PHÂN HỆ (MARKDOWN) ---
    help_text = """
    💡 **Hướng dẫn nhanh các phân hệ:**
    * **🏦 Lãi suất thị trường 2:** Lãi suất liên ngân hàng, lãi suất trái phiếu chính phủ (so sánh).
    * **📈 Lãi suất thị trường 1:** Lãi suất huy động, lãi suất cho vay, ngắn hạn, trung dài hạn, cao nhất, thấp nhất, VND, USD.
    * **📊 Tín dụng, Cung tiền & OMO:** Diễn biến dư nợ tín dụng, cơ cấu dư nợ, tổng phương tiện thanh toán, cơ cấu tổng phương tiện thanh toán, bơm hút ròng tiền trên thị trường mở.
    * **🌍 Chỉ số Bất ổn & FFR:** Chỉ số Bất ổn Toàn cầu (WUI), Chỉ số Bất ổn Chính sách Tiền tệ Mỹ (MPUI) và Lãi suất Quỹ liên bang Fed (FFR).
    * **⚖️ Tỷ giá & Lạm phát:** Tỷ giá trung tâm VND/USD (ngày), Kỳ vọng lạm phát điều tra của các TCTD (BQ năm nay so với năm trước) và Thay đổi CPI (so với cùng kỳ) (%).
    * **📊 Kinh tế vĩ mô (Macro):** Xem các chỉ tiêu vĩ mô đồng thời.
    """
    
    # --- SIDEBAR RADIO BUTTON ---
    menu_selection = st.sidebar.radio(
        "Di chuyển giữa các màn hình:",
        [
            "🏦 Lãi suất thị trường 2", 
            "📈 Lãi suất thị trường 1", 
            "📊 Tín dụng, Cung tiền & OMO", 
            "🌍 Chỉ số Bất ổn & FFR", 
            "⚖️ Tỷ giá & Lạm phát",
            "📊 Kinh tế vĩ mô (Macro)"
        ],
        help=help_text  # Hiển thị tooltip hướng dẫn chung khi di chuột vào tiêu đề
    )
    # Đỡ mất công gõ lại, định nghĩa hàm lấy danh sách cột hợp lệ (bỏ cột Date, Kỳ, Ngày, v.v.)
    def get_numeric_cols(df):
        exclude = ['Date', 'date', 'Ngày', 'Kỳ', 'ky', 'Quarter', 'Quý', 'Year', 'Năm']
        return [col for col in df.columns if col not in exclude and not pd.api.types.is_datetime64_any_dtype(df[col])]

    # ----------------------------------------------------------------------
    # MODE 1: LÃI SUẤT THỊ TRƯỜNG 2 (TƯƠNG ỨNG TAB 1 CŨ)
    # ----------------------------------------------------------------------
    if menu_selection == "🏦 Lãi suất thị trường 2":
        if 'vnibor_q' in data and 'bond_y_q' in data and 'vnibor' in data:
            
            # Tên chỉ tiêu mặc định cũ nếu tồn tại trong file
            col_qd_def = "Lãi suất bình quân liên ngân hàng qua đêm\nĐơn vị: %"
            col_1w_def = "Lãi suất bình quân liên ngân hàng 1 tuần\nĐơn vị: %"
            col_bond_def = "Lợi suất trái phiếu chính phủ 1 năm\nĐơn vị: %"

            # =====================================================================
            # ĐỒ THỊ 1: Tạo bộ lọc thời gian & Tần suất riêng cho Đồ thị 1
            # =====================================================================
            st.subheader("1. Diễn biến Lãi suất liên ngân hàng")
            
            # Bổ sung chọn tần suất riêng cho Đồ thị 1
            freq_t1 = st.radio(
                "Chọn tần suất hiển thị (Đồ thị 1):",
                ["Theo quý (Dữ liệu Quý)", "Theo tháng (Dữ liệu Tháng)"],
                horizontal=True,
                key="freq_selector_t1"
            )
            
            # Gán nguồn dữ liệu dựa trên tần suất Đồ thị 1
            vnibor_source_t1 = data['vnibor'] if freq_t1 == "Theo tháng (Dữ liệu Tháng)" else data['vnibor_q']

            # THIẾT LẬP THỜI GIAN ĐỘNG CHO ĐỒ THỊ 1 DỰA TRÊN VNIBOR SOURCE
            min_date_t1 = vnibor_source_t1['Date'].min().to_pydatetime() if not vnibor_source_t1.empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_t1 = vnibor_source_t1['Date'].max().to_pydatetime() if not vnibor_source_t1.empty else pd.to_datetime("2026-06-30").to_pydatetime()

            st.markdown("##### 📅 Khung thời gian phân tích (Đồ thị 1)")
            c1, c2 = st.columns(2)
            with c1:
                start_date_t1 = pd.to_datetime(st.date_input(
                    "Từ ngày (Đồ thị 1)", 
                    min_value=min_date_t1, max_value=max_date_t1, value=min_date_t1, 
                    key="start_t1"
                ))
            with c2:
                end_date_t1 = pd.to_datetime(st.date_input(
                    "Đến ngày (Đồ thị 1)", 
                    min_value=min_date_t1, max_value=max_date_t1, value=max_date_t1, 
                    key="end_t1"
                ))

            # Lọc dữ liệu Đồ thị 1
            v_q = vnibor_source_t1[(vnibor_source_t1['Date'] >= start_date_t1) & (vnibor_source_t1['Date'] <= end_date_t1)]
            available_cols_v1 = get_numeric_cols(v_q)
            
            # Gợi ý mặc định
            default_v1 = [c for c in available_cols_v1 if any(k in c for k in ['qua đêm', '1 tuần'])]
            if not default_v1 and available_cols_v1: 
                default_v1 = available_cols_v1[:min(2, len(available_cols_v1))]
            
            selected_v1 = st.multiselect("Chọn các chỉ tiêu VNIBOR muốn hiển thị:", available_cols_v1, default=default_v1, key="sel_t1_g1")
            
            if selected_v1:
                fig1 = go.Figure()
                for col in selected_v1:
                    y_val = v_q[col]*100 if v_q[col].max() <= 1 else v_q[col]
                    display_name = col.split('\n')[0]
                    fig1.add_trace(go.Scatter(x=v_q['Date'], y=y_val, mode='lines+markers', name=display_name))
                
                fig1.update_layout(
                    title=f"Lãi suất liên ngân hàng ({freq_t1.split(' ')[0].lower()})", 
                    xaxis_title="Ngày", 
                    yaxis_title="Tỷ lệ (%)", 
                    template="plotly_white", 
                    hovermode="x unified",
                    height=500,
                    legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            st.write("---") # Đường kẻ phân cách giữa 2 đồ thị

            # =====================================================================
            # ĐỒ THỊ 2: Tạo bộ lọc thời gian & Tần suất riêng cho Đồ thị 2
            # =====================================================================
            st.subheader("2. Tương quan VNIBOR và Lợi suất TPCP")
            
            # Bổ sung chọn tần suất riêng cho Đồ thị 2
            freq_t2 = st.radio(
                "Chọn tần suất hiển thị (Đồ thị 2):",
                ["Theo quý (Dữ liệu Quý)", "Theo tháng (Dữ liệu Tháng)"],
                horizontal=True,
                key="freq_selector_t2"
            )
            
            # Gán nguồn dữ liệu động dựa trên tần suất Đồ thị 2
            vnibor_source_t2 = data['vnibor'] if freq_t2 == "Theo tháng (Dữ liệu Tháng)" else data['vnibor_q']
            
            if freq_t2 == "Theo tháng (Dữ liệu Tháng)" and 'bond_y_m' in data:
                bond_source_t2 = data['bond_y_m']
            else:
                bond_source_t2 = data['bond_y_q']

            # THIẾT LẬP THỜI GIAN ĐỘNG CHO ĐỒ THỊ 2 (Ưu tiên theo nguồn VNIBOR của đồ thị 2)
            min_date_t2 = vnibor_source_t2['Date'].min().to_pydatetime() if not vnibor_source_t2.empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_t2 = vnibor_source_t2['Date'].max().to_pydatetime() if not vnibor_source_t2.empty else pd.to_datetime("2026-06-30").to_pydatetime()

            st.markdown("##### 📅 Khung thời gian phân tích (Đồ thị 2)")
            c3, c4 = st.columns(2)
            with c3:
                start_date_t2 = pd.to_datetime(st.date_input(
                    "Từ ngày (Đồ thị 2)", 
                    min_value=min_date_t2, max_value=max_date_t2, value=min_date_t2, 
                    key="start_t2"
                ))
            with c4:
                end_date_t2 = pd.to_datetime(st.date_input(
                    "Đến ngày (Đồ thị 2)", 
                    min_value=min_date_t2, max_value=max_date_t2, value=max_date_t2, 
                    key="end_t2"
                ))
    
            # Lọc khung thời gian riêng cho Đồ thị 2 từ các nguồn dữ liệu độc lập vừa gán
            v_q_g2 = vnibor_source_t2[(vnibor_source_t2['Date'] >= start_date_t2) & (vnibor_source_t2['Date'] <= end_date_t2)]
            b_q_g2 = bond_source_t2[(bond_source_t2['Date'] >= start_date_t2) & (bond_source_t2['Date'] <= end_date_t2)]

            available_cols_v2 = get_numeric_cols(v_q_g2)
            available_cols_b2 = get_numeric_cols(b_q_g2)
            
            cc1, cc2 = st.columns(2)
            with cc1:
                default_v2_col = next((c for c in available_cols_v2 if 'qua đêm' in c), available_cols_v2[0] if available_cols_v2 else None)
                idx_v2 = available_cols_v2.index(default_v2_col) if default_v2_col in available_cols_v2 else 0
                selected_v2 = st.selectbox("Chọn chỉ tiêu liên ngân hàng (Trục VNIBOR):", available_cols_v2, index=idx_v2, key="sel_t1_g2_v")
            with cc2:
                default_b2_col = next((c for c in available_cols_b2 if any(k in c for k in ['10 năm', '1 năm'])), available_cols_b2[0] if available_cols_b2 else None)
                idx_b2 = available_cols_b2.index(default_b2_col) if default_b2_col in available_cols_b2 else 0
                selected_b2 = st.selectbox("Chọn chỉ tiêu Trái phiếu Chính phủ:", available_cols_b2, index=idx_b2, key="sel_t1_g2_b")
            
            if selected_v2 and selected_b2:
                fig2 = go.Figure()
                y_v2 = v_q_g2[selected_v2]*100 if v_q_g2[selected_v2].max() <= 1 else v_q_g2[selected_v2]
                y_b2 = b_q_g2[selected_b2]*100 if b_q_g2[selected_b2].max() <= 1 else b_q_g2[selected_b2]
                
                display_v2 = selected_v2.split('\n')[0]
                display_b2 = selected_b2.split('\n')[0]
                
                fig2.add_trace(go.Scatter(x=v_q_g2['Date'], y=y_v2, mode='lines+markers', name=display_v2))
                fig2.add_trace(go.Scatter(x=b_q_g2['Date'], y=y_b2, mode='lines+markers', name=display_b2, line=dict(dash='dash')))
                
                fig2.update_layout(
                    title=f"Mối tương quan giữa VNIBOR và Lợi suất TPCP ({freq_t2.split(' ')[0].lower()})", 
                    xaxis_title="Ngày", 
                    yaxis_title="Tỷ lệ (%)", 
                    template="plotly_white", 
                    hovermode="x unified",
                    height=500,
                    legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------------------------
    # MODE 2: LÃI SUẤT THỊ TRƯỜNG 1 (TƯƠNG ỨNG TAB 2 CŨ)
    # ----------------------------------------------------------------------
    elif menu_selection == "📈 Lãi suất thị trường 1":
        if 'ls1' in data and 'ls2' in data:
            
            # =====================================================================
            # ĐỒ THỊ 1: CHI TIẾT LÃI SUẤT HUY ĐỘNG & CHO VAY (DỮ LIỆU LS1)
            # =====================================================================
            st.subheader("1. Diễn biến Lãi suất Huy động và Cho vay chi tiết (Tháng)")
            
            # THIẾT LẬP THỜI GIAN ĐỘNG CHO LS1
            min_date_ls1 = data['ls1']['Date'].min().to_pydatetime() if not data['ls1'].empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_ls1 = data['ls1']['Date'].max().to_pydatetime() if not data['ls1'].empty else pd.to_datetime("2026-06-30").to_pydatetime()

            # Bộ lọc thời gian độc lập cho Đồ thị 1
            st.markdown("##### 📅 Khung thời gian phân tích (Đồ thị 1)")
            c1_t1, c2_t1 = st.columns(2)
            with c1_t1:
                start_date_ls1 = pd.to_datetime(st.date_input(
                    "Từ ngày (Đồ thị 1)", 
                    min_value=min_date_ls1, max_value=max_date_ls1, value=min_date_ls1, 
                    key="start_ls1"
                ))
            with c2_t1:
                end_date_ls1 = pd.to_datetime(st.date_input(
                    "Đến ngày (Đồ thị 1)", 
                    min_value=min_date_ls1, max_value=max_date_ls1, value=max_date_ls1, 
                    key="end_ls1"
                ))

            # Lọc dữ liệu ls1 theo khung thời gian riêng
            ls1_df = data['ls1'][(data['ls1']['Date'] >= start_date_ls1) & (data['ls1']['Date'] <= end_date_ls1)]
            
            # Quét và phân loại cột cho bảng ls1
            all_cols_ls1 = get_numeric_cols(ls1_df)
            hd_cols_ls1 = [c for c in all_cols_ls1 if 'LSHĐ' in c]
            cv_cols_ls1 = [c for c in all_cols_ls1 if any(k in c for k in ['LSCV', 'LSCH', 'Cho vay'])]

            # Giao diện bộ chọn chỉ tiêu song song
            cc1, cc2 = st.columns(2)
            with cc1:
                default_hd1 = [c for c in hd_cols_ls1 if 'Kỳ hạn > 12 tháng' in c][:2]
                if not default_hd1 and hd_cols_ls1: default_hd1 = hd_cols_ls1[:2]
                selected_hd1 = st.multiselect("🏦 Chọn Lãi suất Huy động (ls1):", hd_cols_ls1, default=default_hd1, key="sel_hd_ls1")
            with cc2:
                default_cv1 = [c for c in cv_cols_ls1 if 'SXKD thông thường (Nhóm NHTM NN)' in c][:2]
                if not default_cv1 and cv_cols_ls1: default_cv1 = cv_cols_ls1[:2]
                selected_cv1 = st.multiselect("💸 Chọn Lãi suất Cho vay (ls1):", cv_cols_ls1, default=default_cv1, key="sel_cv_ls1")

            selected_t2_g1 = selected_hd1 + selected_cv1

            if selected_t2_g1:
                fig3 = go.Figure()
                for idx, col in enumerate(selected_t2_g1):
                    y_val = ls1_df[col]*100 if ls1_df[col].max() <= 1 else ls1_df[col]
                    marker_symbol = 'square' if idx % 2 == 0 else 'circle'
                    display_name = col.strip().split('\n')[0]
                    fig3.add_trace(go.Scatter(x=ls1_df['Date'], y=y_val, mode='lines+markers', name=display_name, marker=dict(symbol=marker_symbol)))
                
                fig3.update_layout(
                    title="Biến động các chỉ tiêu lãi suất chi tiết",
                    xaxis_title="Ngày",
                    yaxis_title="Lãi suất (%)", 
                    template="plotly_white", 
                    hovermode="x unified",
                    height=520,
                    legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                    xaxis=dict(tickangle=45)
                )
                st.plotly_chart(fig3, use_container_width=True)

            # =====================================================================
            # ĐỒ THỊ 2: LÃI SUẤT HUY ĐỘNG & CHO VAY TỔNG HỢP (DỮ LIỆU LS2)
            # =====================================================================
            st.write("---")
            st.subheader("2. Diễn biến Lãi suất Huy động và Cho vay tổng hợp (Cột nhóm)")
            
            # THIẾT LẬP THỜI GIAN ĐỘNG CHO LS2
            min_date_ls2 = data['ls2']['Date'].min().to_pydatetime() if not data['ls2'].empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_ls2 = data['ls2']['Date'].max().to_pydatetime() if not data['ls2'].empty else pd.to_datetime("2026-06-30").to_pydatetime()

            # Bộ lọc thời gian độc lập cho Đồ thị 2
            st.markdown("##### 📅 Khung thời gian phân tích (Đồ thị 2)")
            c1_t2, c2_t2 = st.columns(2)
            with c1_t2:
                start_date_ls2 = pd.to_datetime(st.date_input(
                    "Từ ngày (Đồ thị 2)", 
                    min_value=min_date_ls2, max_value=max_date_ls2, value=min_date_ls2, 
                    key="start_ls2"
                ))
            with c2_t2:
                end_date_ls2 = pd.to_datetime(st.date_input(
                    "Đến ngày (Đồ thị 2)", 
                    min_value=min_date_ls2, max_value=max_date_ls2, value=max_date_ls2, 
                    key="end_ls2"
                ))

            # Lọc dữ liệu ls2 theo khung thời gian riêng
            ls2_df = data['ls2'][(data['ls2']['Date'] >= start_date_ls2) & (data['ls2']['Date'] <= end_date_ls2)]
            
            # Quét và phân loại cột cho bảng ls2
            all_cols_ls2 = get_numeric_cols(ls2_df)
            hd_cols_ls2 = [c for c in all_cols_ls2 if 'huy động' in c.lower()]
            cv_cols_ls2 = [c for c in all_cols_ls2 if 'cho vay' in c.lower()]

            # Giao diện bộ chọn chỉ tiêu song song
            cc3, cc4 = st.columns(2)
            with cc3:
                default_hd2 = [c for c in hd_cols_ls2 if 'trên 12 tháng' in c.lower()]
                if not default_hd2 and hd_cols_ls2: default_hd2 = hd_cols_ls2[:2]
                selected_hd2 = st.multiselect("🏦 Chọn Lãi suất Huy động tổng hợp (ls2):", hd_cols_ls2, default=default_hd2, key="sel_hd_ls2")
            with cc4:
                default_cv2 = [c for c in cv_cols_ls2 if 'trung và dài hạn' in c.lower()]
                # Kiểm tra nếu danh sách mặc định trống thì tự động lấy 2 cột đầu tiên
                if not default_cv2: default_cv2 = cv_cols_ls2[:2]
                selected_cv2 = st.multiselect("💸 Chọn Lãi suất Cho vay tổng hợp (ls2):", cv_cols_ls2, default=default_cv2, key="sel_cv_ls2")

            selected_bar2 = selected_hd2 + selected_cv2

            if selected_bar2:
                # Kiểm tra định dạng phần trăm thập phân thô
                is_decimal = ls2_df[selected_bar2[0]].max() <= 1
                
                # Nhân 100 nếu dữ liệu là dạng thập phân
                plot_df = ls2_df.copy()
                if is_decimal:
                    for col in selected_bar2:
                        plot_df[col] = plot_df[col] * 100

                fig_bar2 = px.bar(
                    plot_df, 
                    x='Kỳ' if 'Kỳ' in plot_df.columns else 'Date', 
                    y=selected_bar2, 
                    barmode='group', 
                    labels={'value': 'Lãi suất (%)', 'variable': 'Chỉ tiêu'},
                    color_discrete_sequence=['#3b71ca', '#f17a28', '#708090', '#008080']
                )
                
                # Định dạng nhãn hiển thị đầu cột
                fig_bar2.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
                
                # Tính toán biên trục Y linh hoạt
                max_val = max([plot_df[c].max() for c in selected_bar2])
                min_val = min([plot_df[c].min() for c in selected_bar2])
                
                fig_bar2.update_layout(
                    title="So sánh biên độ lãi suất theo các kỳ gần đây",
                    yaxis_title="Lãi suất (%)",
                    yaxis=dict(range=[max(0, min_val - 1.5), max_val + 1.5]), 
                    template="plotly_white",
                    height=520,
                    legend=dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                    xaxis=dict(title="Kỳ báo cáo", tickangle=45)
                )
                st.plotly_chart(fig_bar2, use_container_width=True)
        else:
            st.error("Không tìm thấy đủ dữ liệu của hai sheet 'ls1' và 'ls2' trong hệ thống!")

    # ----------------------------------------------------------------------
    # MODE 3: TÍN DỤNG & PHƯƠNG TIỆN THANH TOÁN (TƯƠNG ỨNG TAB 3 CŨ)
    # ----------------------------------------------------------------------
    elif menu_selection == "📊 Tín dụng, Cung tiền & OMO":
        # Khởi tạo định danh chuỗi mặc định cũ
        col_m2_pct_def = "Tổng phương tiện thanh toán (M2) - % từ đầu năm (M)\nĐơn vị: %"
        col_cre_pct_def = "Tổng dư nợ tín dụng - % từ đầu năm (M)\nĐơn vị: %"
        col_tckt_pct_def = "Tiền gửi của các TCKT - % từ đầu năm (M)\nĐơn vị: %"
        col_cd_pct_def = "Tiền gửi của cư dân - % từ đầu năm (M)\nĐơn vị: %"
        
        col_tckt_val_def = "Tiền gửi của các TCKT - Giá trị (M)\nĐơn vị: Tỷ VND"
        col_dancu_val_def = "Tiền gửi của cư dân - Giá trị (M)\nĐơn vị: Tỷ VND"
        col_m2_val_def = "Tổng phương tiện thanh toán (M2) - Giá trị (M)\nĐơn vị: Tỷ VND"
        col_omo_val_def = "   Bơm hút tiền ròng (tỷ VND)"
    
        if 'credit' in data:
            # THIẾT LẬP THỜI GIAN ĐỘNG CHO SHEET CREDIT
            min_date_credit = data['credit']['Date'].min().to_pydatetime() if not data['credit'].empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_credit = data['credit']['Date'].max().to_pydatetime() if not data['credit'].empty else pd.to_datetime("2026-06-30").to_pydatetime()

            # =========================================================================
            # --- ĐỒ THỊ 1: CẤU TRÚC QUY MÔ GIÁ TRỊ SẢN LƯỢNG TIỀN TỆ ---
            # =========================================================================
            st.markdown("##### 📅 Khung thời gian phân tích Quy mô & Tăng trưởng Tín dụng (Đồ thị 1)")
            c1, c2 = st.columns(2)
            with c1:
                start_date_t3_cre = pd.to_datetime(st.date_input(
                    "Từ ngày (Tín dụng)", 
                    min_value=min_date_credit, max_value=max_date_credit, value=min_date_credit, 
                    key="start_t3_cre"
                ))
            with c2:
                end_date_t3_cre = pd.to_datetime(st.date_input(
                    "Đến ngày (Tín dụng)", 
                    min_value=min_date_credit, max_value=max_date_credit, value=max_date_credit, 
                    key="end_t3_cre"
                ))
    
            cre_df = data['credit'][(data['credit']['Date'] >= start_date_t3_cre) & (data['credit']['Date'] <= end_date_t3_cre)]
            available_cols_cre = get_numeric_cols(cre_df)
            
            st.subheader("1. Tổng phương tiện thanh toán và Cơ cấu Tiền gửi (Triệu tỷ VND)")
            
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                def_b1 = col_tckt_val_def if col_tckt_val_def in available_cols_cre else available_cols_cre[0]
                sel_b1 = st.selectbox("Cấu phần Cột Chồng 1 (Tiền gửi TCKT):", available_cols_cre, index=available_cols_cre.index(def_b1), key="t3_g1_b1")
            with cc2:
                def_b2 = col_dancu_val_def if col_dancu_val_def in available_cols_cre else available_cols_cre[min(1, len(available_cols_cre)-1)]
                sel_b2 = st.selectbox("Cấu phần Cột Chồng 2 (Tiền gửi Dân cư):", available_cols_cre, index=available_cols_cre.index(def_b2), key="t3_g1_b2")
            with cc3:
                def_l1 = col_m2_val_def if col_m2_val_def in available_cols_cre else available_cols_cre[min(2, len(available_cols_cre)-1)]
                sel_l1 = st.selectbox("Đường Tổng thể xu hướng (M2):", available_cols_cre, index=available_cols_cre.index(def_l1), key="t3_g1_l1")
            
            # Tiến hành quy đổi đơn vị tính tự động /1.000.000 nếu dữ liệu là tỷ đồng
            v_tckt = cre_df[sel_b1] / 1000000 if cre_df[sel_b1].max() > 1000 else cre_df[sel_b1]
            v_dancu = cre_df[sel_b2] / 1000000 if cre_df[sel_b2].max() > 1000 else cre_df[sel_b2]
            v_m2 = cre_df[sel_l1] / 1000000 if cre_df[sel_l1].max() > 1000 else cre_df[sel_l1]
            
            fig_comb = go.Figure()
            fig_comb.add_trace(go.Bar(x=cre_df['Kỳ'] if 'Kỳ' in cre_df.columns else cre_df['Date'], y=v_tckt, name=sel_b1.split('\n')[0], marker_color='#f17a28'))
            fig_comb.add_trace(go.Bar(x=cre_df['Kỳ'] if 'Kỳ' in cre_df.columns else cre_df['Date'], y=v_dancu, name=sel_b2.split('\n')[0], marker_color='#a6a6a6'))
            fig_comb.add_trace(go.Scatter(x=cre_df['Kỳ'] if 'Kỳ' in cre_df.columns else cre_df['Date'], y=v_m2, name=sel_l1.split('\n')[0], mode='lines+markers+text', text=v_m2.apply(lambda x: f"{x:,.2f}"), textposition='top center', line=dict(color='#3b71ca', width=3)))
            fig_comb.update_layout(
                barmode='stack', 
                template="plotly_white", 
                yaxis_title="Quy mô hiển thị (Triệu tỷ / Đơn vị chuẩn)",
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_comb, use_container_width=True)
            
            # =========================================================================
            # --- ĐỒ THỊ 2: TỐC ĐỘ TĂNG TRƯỞNG M2 & TÍN DỤNG ---
            # =========================================================================
            st.markdown("---")
            st.subheader("2. Cung tiền M2 và Dư nợ Tín dụng (từ đầu năm)")
            
            # Bộ lọc thời gian riêng biệt cho Đồ thị 2 sử dụng thời gian động từ credit
            st.markdown("##### 📅 Khung thời gian phân tích Tốc độ tăng trưởng (Đồ thị 2)")
            ct1, ct2 = st.columns(2)
            with ct1:
                start_date_t3_g2 = pd.to_datetime(st.date_input(
                    "Từ ngày (Tốc độ tăng trưởng)", 
                    min_value=min_date_credit, max_value=max_date_credit, value=min_date_credit, 
                    key="start_t3_g2"
                ))
            with ct2:
                end_date_t3_g2 = pd.to_datetime(st.date_input(
                    "Đến ngày (Tốc độ tăng trưởng)", 
                    min_value=min_date_credit, max_value=max_date_credit, value=max_date_credit, 
                    key="end_t3_g2"
                ))
    
            # Lọc tập dữ liệu riêng biệt cho đồ thị 2
            cre_df_g2 = data['credit'][(data['credit']['Date'] >= start_date_t3_g2) & (data['credit']['Date'] <= end_date_t3_g2)]
            available_cols_cre_g2 = get_numeric_cols(cre_df_g2)
    
            if not cre_df_g2.empty:
                ccc1, ccc2 = st.columns([3, 1]) 
                with ccc1:
                    def_mult_all = [c for c in [col_m2_pct_def, col_cre_pct_def] if c in available_cols_cre_g2]
                    sel_mult_all = st.multiselect(
                        "Chọn các chỉ tiêu muốn hiển thị:", 
                        available_cols_cre_g2, 
                        default=def_mult_all, 
                        key="t3_g2_metrics"
                    )
                with ccc2:
                    chart_type = st.selectbox(
                        "Kiểu hiển thị:", 
                        ["Dạng Đường (Line)", "Dạng Cột (Bar)"], 
                        index=0, 
                        key="t3_g2_chart_type"
                    )
                
                fig_pct = go.Figure()
                
                if sel_mult_all:
                    for col in sel_mult_all:
                        y_val = cre_df_g2[col]*100 if cre_df_g2[col].max() <= 1 else cre_df_g2[col]
                        
                        if chart_type == "Dạng Đường (Line)":
                            fig_pct.add_trace(go.Scatter(
                                x=cre_df_g2['Date'], 
                                y=y_val, 
                                name=col.split('\n')[0], 
                                mode='lines+markers+text',
                                text=y_val.apply(lambda x: f"{x:,.2f}%"),
                                textposition='top center',
                                line=dict(width=2.5)
                            ))
                        else: # Dạng Cột (Bar)
                            x_axis = cre_df_g2['Kỳ'] if 'Kỳ' in cre_df_g2.columns else cre_df_g2['Date']
                            fig_pct.add_trace(go.Bar(
                                x=x_axis, 
                                y=y_val, 
                                name=col.split('\n')[0], 
                                text=y_val.apply(lambda x: f"{x:,.2f}%"),
                                textposition='outside',
                                opacity=0.85
                            ))
                            
                    fig_pct.update_layout(
                        template="plotly_white", 
                        yaxis_title="% Thay đổi",
                        barmode="group" if chart_type == "Dạng Cột (Bar)" else None,
                        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_pct, use_container_width=True)
                else:
                    st.info("Vui lòng chọn ít nhất một chỉ tiêu để hiển thị đồ thị.")
            else:
                st.warning("Không có dữ liệu tăng trưởng trong khoảng thời gian đã chọn.")
    
        # =========================================================================
        # --- ĐỒ THỊ 3: KHỐI LƯỢNG NGHIỆP VỤ THỊ TRƯỜNG MỞ OMO ---
        # =========================================================================
        st.markdown("---")
        if 'omo' in data:
            st.subheader("3. Bơm/Hút tiền ròng trên thị trường mở (OMO)")
            
            # THIẾT LẬP THỜI GIAN ĐỘNG CHO SHEET OMO
            min_date_omo = data['omo']['Date'].min().to_pydatetime() if not data['omo'].empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_omo = data['omo']['Date'].max().to_pydatetime() if not data['omo'].empty else pd.to_datetime("2026-06-30").to_pydatetime()

            st.markdown("##### 📅 Khung thời gian phân tích Nghiệp vụ OMO")
            c1, c2 = st.columns(2)
            with c1:
                start_date_t3_omo = pd.to_datetime(st.date_input(
                    "Từ ngày (OMO)", 
                    min_value=min_date_omo, max_value=max_date_omo, value=min_date_omo, 
                    key="start_t3_omo"
                ))
            with c2:
                end_date_t3_omo = pd.to_datetime(st.date_input(
                    "Đến ngày (OMO)", 
                    min_value=min_date_omo, max_value=max_date_omo, value=max_date_omo, 
                    key="end_t3_omo"
                ))
    
            omo_df = data['omo'][(data['omo']['Date'] >= start_date_t3_omo) & (data['omo']['Date'] <= end_date_t3_omo)]
            available_cols_omo = get_numeric_cols(omo_df)
            
            def_omo = col_omo_val_def if col_omo_val_def in available_cols_omo else available_cols_omo[0]
            selected_omo_col = st.selectbox("Chọn chỉ tiêu khối lượng ròng OMO điều tiết:", available_cols_omo, index=available_cols_omo.index(def_omo), key="sel_t3_omo")
            
            fig_omo = px.bar(omo_df, x='Kỳ' if 'Kỳ' in omo_df.columns else 'Date', y=selected_omo_col, title="Khối lượng ròng điều tiết thanh khoản", color_discrete_sequence=['#6b1d2f'])
            fig_omo.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
            fig_omo.update_layout(
                template="plotly_white", 
                yaxis_title="Giá trị số liệu",
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_omo, use_container_width=True)

    # ----------------------------------------------------------------------
    # MODE 4: CHỈ SỐ BẤT ỔN TOÀN CẦU VÀ LÃI SUẤT FED (TƯƠNG ỨNG TAB 4 CŨ)
    # ----------------------------------------------------------------------
    elif menu_selection == "🌍 Chỉ số Bất ổn & FFR":
        if 'ls_wui' in data:
            
            # THIẾT LẬP THỜI GIAN ĐỘNG CHO SHEET LS_WUI
            min_date_wui = data['ls_wui']['Date'].min().to_pydatetime() if not data['ls_wui'].empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date_wui = data['ls_wui']['Date'].max().to_pydatetime() if not data['ls_wui'].empty else pd.to_datetime("2026-06-30").to_pydatetime()

            # Tạo bộ lọc thời gian riêng cho Tab 4
            st.markdown("##### 📅 Khung thời gian phân tích (Phân hệ 4)")
            c1, c2 = st.columns(2)
            with c1:
                start_date_t4 = pd.to_datetime(st.date_input(
                    "Từ ngày (Phân hệ 4)", 
                    min_value=min_date_wui, max_value=max_date_wui, value=min_date_wui, 
                    key="start_t4"
                ))
            with c2:
                end_date_t4 = pd.to_datetime(st.date_input(
                    "Đến ngày (Phân hệ 4)", 
                    min_value=min_date_wui, max_value=max_date_wui, value=max_date_wui, 
                    key="end_t4"
                ))

            wui_df = data['ls_wui'][(data['ls_wui']['Date'] >= start_date_t4) & (data['ls_wui']['Date'] <= end_date_t4)]
            available_cols_wui = get_numeric_cols(wui_df)
            
            col_wui_def = "WUI, GDP weighted average"
            col_bbd_def = "BBD MPU Index Based on Access World News"
            col_ffr_def = "Monetary policy-related, Rate, Percent per annum"
            
            # Đồ thị 1: Trục tung kép (Twin X-axis) WUI vs BBD MPU
            st.subheader("1. Chỉ số Bất ổn Toàn cầu (WUI) và Bất ổn Chính sách Tiền tệ Mỹ (MPUI)")
            
            cx1, cx2 = st.columns(2)
            with cx1:
                def_w1 = col_wui_def if col_wui_def in available_cols_wui else available_cols_wui[0]
                sel_w1 = st.selectbox("Chọn chỉ tiêu Trục trái (Ví dụ WUI):", available_cols_wui, index=available_cols_wui.index(def_w1), key="t4_g1_l")
            with cx2:
                def_w2 = col_bbd_def if col_bbd_def in available_cols_wui else available_cols_wui[min(1, len(available_cols_wui)-1)]
                sel_w2 = st.selectbox("Chọn chỉ tiêu Trục phải (Ví dụ BBD MPU):", available_cols_wui, index=available_cols_wui.index(def_w2), key="t4_g1_r")
            
            fig_twin1 = go.Figure()
            fig_twin1.add_trace(go.Scatter(x=wui_df['Date'], y=wui_df[sel_w1], name=f"{sel_w1.split(',')[0]} (Trục trái)", mode='lines+markers'))
            fig_twin1.add_trace(go.Scatter(x=wui_df['Date'], y=wui_df[sel_w2], name=f"{sel_w2.split(',')[0]} (Trục phải)", mode='lines+markers', yaxis='y2', line=dict(color='red')))
            
            fig_twin1.update_layout(
                template="plotly_white",
                yaxis=dict(title=sel_w1.split(',')[0]),
                yaxis2=dict(title=sel_w2.split(',')[0], overlaying='y', side='right'),
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_twin1, use_container_width=True)
            
            # Đồ thị 2: Trục tung kép FFR vs BBD MPU
            st.subheader("2. Lãi suất liên bang Fed (FFR) và Chỉ số Bất ổn Chính sách tiền tệ Mỹ (MPUI)")
            
            cy1, cy2 = st.columns(2)
            with cy1:
                def_f1 = col_ffr_def if col_ffr_def in available_cols_wui else available_cols_wui[min(2, len(available_cols_wui)-1)]
                sel_f1 = st.selectbox("Chọn chỉ tiêu Lãi suất chính sách (Trục trái):", available_cols_wui, index=available_cols_wui.index(def_f1), key="t4_g2_l")
            with cy2:
                def_f2 = col_bbd_def if col_bbd_def in available_cols_wui else available_cols_wui[min(1, len(available_cols_wui)-1)]
                sel_f2 = st.selectbox("Chọn chỉ tiêu Bất ổn vĩ mô công cụ (Trục phải):", available_cols_wui, index=available_cols_wui.index(def_f2), key="t4_g2_r")
            
            fig_twin2 = go.Figure()
            y_f1 = wui_df[sel_f1]*100 if wui_df[sel_f1].max() <= 1 and "Percent" in sel_f1 else wui_df[sel_f1]
            fig_twin2.add_trace(go.Scatter(x=wui_df['Date'], y=y_f1, name=f"{sel_f1.split(',')[0]} (Trục trái)", mode='lines'))
            fig_twin2.add_trace(go.Scatter(x=wui_df['Date'], y=wui_df[sel_f2], name=f"{sel_f2.split(',')[0]} (Trục phải)", mode='lines+markers', yaxis='y2', line=dict(color='red')))
            
            fig_twin2.update_layout(
                template="plotly_white",
                yaxis=dict(title=sel_f1.split(',')[0]),
                yaxis2=dict(title=sel_f2.split(',')[0], overlaying='y', side='right'),
                legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_twin2, use_container_width=True)

    # ----------------------------------------------------------------------
    # MODE 5: TỶ GIÁ TRUNG TÂM & KỲ VỌNG LẠM PHÁT (TƯƠNG ỨNG TAB 5 CŨ)
    # ----------------------------------------------------------------------
    elif menu_selection == "⚖️ Tỷ giá & Lạm phát":
        # =========================================================================
        # --- ĐỒ THỊ 1: BIẾN ĐỘNG TỶ GIÁ TRUNG TÂM ---
        # =========================================================================
        st.subheader("1. Diễn biến Tỷ giá trung tâm VND/USD")
        if 'ex_d' in data:
            # Đảm bảo cột 'Date' ở định dạng datetime trước khi lấy min/max
            data['ex_d']['Date'] = pd.to_datetime(data['ex_d']['Date'])
            
            # Tự động tính toán ngày bắt đầu và kết thúc động từ dữ liệu thực tế
            min_date_ex = data['ex_d']['Date'].min()
            max_date_ex = data['ex_d']['Date'].max()
            
            # Tạo bộ lọc thời gian riêng biệt cho Đồ thị Tỷ Giá
            st.markdown("##### 📅 Khung thời gian phân tích Tỷ giá trung tâm")
            c1, c2 = st.columns(2)
            with c1:
                start_date_t5_ex = pd.to_datetime(st.date_input("Từ ngày (Tỷ giá)", min_date_ex, key="start_t5_ex"))
            with c2:
                end_date_t5_ex = pd.to_datetime(st.date_input("Đến ngày (Tỷ giá)", max_date_ex, key="end_t5_ex"))
    
            ex_df = data['ex_d'][(data['ex_d']['Date'] >= start_date_t5_ex) & (data['ex_d']['Date'] <= end_date_t5_ex)]
            available_cols_ex = get_numeric_cols(ex_df)
            
            col_ex_def = "Tỷ giá trung tâm\nĐơn vị: VND"
            def_ex = col_ex_def if col_ex_def in available_cols_ex else available_cols_ex[0]
            selected_ex_col = st.selectbox("Chọn chỉ tiêu tỷ giá / dữ liệu biến động muốn vẽ:", available_cols_ex, index=available_cols_ex.index(def_ex), key="sel_t5_ex")
            
            if selected_ex_col:
                fig_ex = px.line(
                    ex_df, 
                    x='Date', 
                    y=selected_ex_col, 
                    title=f"Diễn biến chỉ tiêu: {selected_ex_col.split('\n')[0]}", 
                    template="plotly_white"
                )
                
                if len(ex_df) > 1:
                    # Điểm đầu và điểm cuối
                    v_start = ex_df[selected_ex_col].iloc[0]
                    v_end = ex_df[selected_ex_col].iloc[-1]
                    
                    fmt_start = f"{v_start:,.0f}" if v_start > 100 else f"{v_start:,.2f}"
                    fmt_end = f"{v_end:,.0f}" if v_end > 100 else f"{v_end:,.2f}"
                    
                    fig_ex.add_annotation(x=ex_df['Date'].iloc[0], y=v_start, text=fmt_start, showarrow=True, arrowhead=2, ax=0, ay=-30)
                    fig_ex.add_annotation(x=ex_df['Date'].iloc[-1], y=v_end, text=fmt_end, showarrow=True, arrowhead=2, ax=0, ay=-30)
                
                st.plotly_chart(fig_ex, use_container_width=True)
        else:
            st.warning("Không tìm thấy dữ liệu tỷ giá ('ex_d')")
    
        # =========================================================================
        # --- ĐỒ THỊ 2: KỲ VỌNG LẠM PHÁT & THAY ĐỔI CPI (BẢN TƯƠNG TÁC PLOTLY) ---
        # =========================================================================
        st.markdown("---") # Đường kẻ phân cách giữa 2 phần
        st.subheader("2. Kỳ vọng lạm phát và thay đổi CPI")
        
        if 'inf' in data:
            inf = data['inf']
            
            # Đảm bảo cột 'Ngày' ở định dạng datetime trước khi lấy min/max
            inf['Ngày'] = pd.to_datetime(inf['Ngày'])
            
            # Tự động tính toán ngày bắt đầu và kết thúc động từ dữ liệu thực tế
            min_date_inf = inf['Ngày'].min()
            max_date_inf = inf['Ngày'].max()
            
            # Tạo bộ lọc thời gian riêng biệt cho Đồ thị Lạm phát
            st.markdown("##### 📅 Khung thời gian phân tích Lạm phát")
            c3, c4 = st.columns(2)
            with c3:
                start_date_inf = st.date_input("Từ ngày (Lạm phát)", min_date_inf, key="start_t5_inf")
            with c4:
                end_date_inf = st.date_input("Đến ngày (Lạm phát)", max_date_inf, key="end_t5_inf")
    
            # Lọc dữ liệu theo thời gian người dùng chọn
            df_inf = inf[(inf["Ngày"] >= pd.to_datetime(start_date_inf)) & (inf["Ngày"] <= pd.to_datetime(end_date_inf))]
            
            if not df_inf.empty:
                # Tạo đối tượng đồ thị bằng Plotly go.Figure() thay thế hoàn toàn cho plt.subplots()
                fig_inf = go.Figure()
                
                # Đường 1: Kỳ vọng lạm phát - Marker hình tròn (circle)
                fig_inf.add_trace(go.Scatter(
                    x=df_inf['Kỳ'],
                    y=df_inf["Kỳ vọng lạm phát (BQ năm nay so với năm trước)"],
                    name="Kỳ vọng lạm phát điều tra hàng tháng",
                    mode="lines+markers",
                    line=dict(color='#a0b2c6', width=3.5),
                    marker=dict(symbol="circle", size=8)
                ))
                
                # Đường 2: Thay đổi CPI - Marker hình vuông (square / chữ 's' trong bản gốc)
                fig_inf.add_trace(go.Scatter(
                    x=df_inf['Kỳ'],
                    y=df_inf["Thay đổi CPI (% so với cùng kỳ trước)"],
                    name="Thay đổi CPI (% so với cùng kỳ trước)",
                    mode="lines+markers",
                    line=dict(color='#1f4e79', width=3.5),
                    marker=dict(symbol="square", size=8)
                ))
                
                # Định dạng cấu trúc hiển thị giống hệt phong cách bản gốc cũ
                fig_inf.update_layout(
                    title=dict(
                        text="Kỳ vọng lạm phát và thay đổi CPI (%)",
                        font=dict(size=14, weight='bold'),
                        pad=dict(b=15)
                    ),
                    template="plotly_white",
                    xaxis=dict(tickangle=45, title=""), # Góc nghiêng trục X 45 độ
                    yaxis=dict(
                        title="",
                        showgrid=True,
                        gridcolor='rgba(211, 211, 211, 0.7)' # Bật grid ngang giống Excel/Matplotlib
                    ),
                    legend=dict(
                        orientation="h",       # Chú thích nằm ngang phía dưới
                        yanchor="top", 
                        y=-0.25, 
                        xanchor="center", 
                        x=0.5
                    ),
                    margin=dict(l=40, r=40, t=50, b=40)
                )
                
                # Hiển thị đồ thị Plotly có tính năng tương tác lên Streamlit
                st.plotly_chart(fig_inf, use_container_width=True)
                
            else:
                st.warning("Không có dữ liệu lạm phát trong khoảng thời gian đã chọn.")
        else:
            st.warning("Không tìm thấy dữ liệu lạm phát ('inf')")
                  
    # ----------------------------------------------------------------------
    # MODE 6: KINH TẾ VĨ MÔ (NỐI TIẾP SAU KHỐI CỦA CÁC MODE TRƯỚC)
    # ----------------------------------------------------------------------
    elif menu_selection == "📊 Kinh tế vĩ mô (Macro)":
        if 'macro' in data:
            st.subheader("📊 Phân tích Chỉ tiêu Kinh tế Vĩ mô tổng hợp")
            
            # 1. Lấy dữ liệu vĩ mô gốc và chuẩn hóa tên cột (Xóa khoảng trắng thừa đầu/cuối)
            macro_df_raw = data['macro'].copy()
            macro_df_raw.columns = [str(c).strip() for c in macro_df_raw.columns]
            
            # 2. Thiết lập khung thời gian tự động dựa trên dữ liệu thực tế
            min_date = macro_df_raw['Date'].min().to_pydatetime() if not macro_df_raw.empty else pd.to_datetime("2022-01-01").to_pydatetime()
            max_date = macro_df_raw['Date'].max().to_pydatetime() if not macro_df_raw.empty else pd.to_datetime("2026-06-30").to_pydatetime()

            st.markdown("##### 📅 Khung thời gian phân tích (Vĩ mô)")
            c1, c2 = st.columns(2)
            with c1:
                # BỔ SUNG: min_value và max_value để mở khóa lịch không bị kẹt ở năm 2016
                start_macro = pd.to_datetime(st.date_input(
                    "Từ ngày (Macro)", 
                    min_value=min_date,
                    max_value=max_date,
                    value=min_date, 
                    key="start_macro"
                ))
            with c2:
                # BỔ SUNG: đồng bộ giới hạn cho ô Đến ngày
                end_macro = pd.to_datetime(st.date_input(
                    "Đến ngày (Macro)", 
                    min_value=min_date,
                    max_value=max_date,
                    value=max_date, 
                    key="end_macro"
                ))
            # Lọc dữ liệu theo thời gian
            macro_df = macro_df_raw[(macro_df_raw['Date'] >= start_macro) & (macro_df_raw['Date'] <= end_macro)].copy()
            x_axis_macro = macro_df['Kỳ'] if 'Kỳ' in macro_df.columns else macro_df['Date']

            if not macro_df.empty:
                
                # =====================================================================
                # CẤU TRÚC: GOM TẤT CẢ 5 CHỈ TIÊU RADIO VỀ 1 CỘT DUY NHẤT (ĐỒNG BỘ CHUẨN)
                # =====================================================================
                macro_options = [
                    "🛒 1. Tiêu dùng, Sản xuất & PMI",
                    "🏢 2. Thu hút vốn đầu tư nước ngoài (FDI)",
                    "🚢 3. Hoạt động Xuất Nhập Khẩu & Cán cân",
                    "🪙 4. Tỷ giá, Lạm phát & Biến động Tiền tệ",
                    "🔑 5. Thị trường Hàng hóa toàn cầu & Tài sản"
                ]
                
                if 'macro_radio_idx' not in st.session_state:
                    st.session_state.macro_radio_idx = 0

                def on_macro_change():
                    st.session_state.macro_radio_idx = macro_options.index(st.session_state.temp_macro_selection)

                st.radio(
                    "📊 Chọn nhóm chỉ tiêu vĩ mô muốn theo dõi:",
                    macro_options,
                    index=st.session_state.macro_radio_idx,
                    key="temp_macro_selection",
                    on_change=on_macro_change,
                    label_visibility="visible"
                )

                macro_group = macro_options[st.session_state.macro_radio_idx]
                st.markdown("---")
                
                # =====================================================================
                # HỘP CHỌN CHỈ TIÊU CHI TIẾT THEO TÊN CỘT CHÍNH THỨC 100%
                # =====================================================================
                selected_cols = []
                all_columns = list(macro_df.columns)
                
                if macro_group == "🛒 1. Tiêu dùng, Sản xuất & PMI":
                    pmi_pool = [
                        'Tổng mức bán lẻ hàng hóa & Dịch vụ (triệu tỷ VND)',
                        'Tăng trưởng tổng mức bán lẻ hàng hóa & Dịch vụ YoY',
                        'Chỉ số Nhà quản trị mua hàng - PMI (Index)',
                        'Chỉ số sản xuất công nghiệp - IIP (Tăng trưởng YoY)'
                    ]
                    available_pmi = [c for c in pmi_pool if c in all_columns]
                    selected_cols = st.multiselect(
                        "🎯 Tùy chỉnh các chỉ tiêu hiển thị trên đồ thị:", 
                        available_pmi, 
                        default=available_pmi if available_pmi else None, 
                        key="macro_pmi_select"
                    )
                    
                elif macro_group == "🏢 2. Thu hút vốn đầu tư nước ngoài (FDI)":
                    fdi_pool = [
                        'FDI (Đăng ký) (triệu tỷ VND)',
                        'Tăng trưởng FDI (Đăng ký) YoY',
                        'FDI (Thực hiện) (triệu tỷ VND)',
                        'Tăng trưởng FDI (Thực hiện) YoY'
                    ]
                    available_fdi = [c for c in fdi_pool if c in all_columns]
                    selected_cols = st.multiselect(
                        "🎯 Tùy chỉnh cấu phần FDI hiển thị:", 
                        available_fdi, 
                        default=available_fdi[:2] if available_fdi else None, 
                        key="macro_fdi_select"
                    )
                    
                elif macro_group == "🚢 3. Hoạt động Xuất Nhập Khẩu & Cán cân":
                    trade_pool = [
                        'Cán cân thương mại hàng hóa (triệu tỷ VND)',
                        'Cán cân thương mại hàng hóa của DN FDI (triệu tỷ VND)',
                        'Cán cân thương mại hàng hóa của DN trong nước (triệu tỷ VND)',
                        'Xuất khẩu (triệu tỷ VND)', 'Tăng trưởng xuất khẩu YoY',
                        'Xuất khẩu của DN FDI (triệu tỷ VND)', 'Tăng trưởng xuất khẩu của DN FDI YoY',
                        'Xuất khẩu của DN trong nước (triệu tỷ VND)', 'Tăng trưởng xuất khẩu của DN trong nước YoY',
                        'Nhập khẩu (triệu tỷ VND)', 'Tăng trưởng nhập khẩu YoY',
                        'Nhập khẩu của DN FDI (triệu tỷ VND)', 'Tăng trưởng nhập khẩu của DN FDI YoY',
                        'Nhập khẩu của DN trong nước (triệu tỷ VND)', 'Tăng trưởng nhập khẩu của DN trong nước YoY'
                    ]
                    available_trade = [c for c in trade_pool if c in all_columns]
                    selected_cols = st.multiselect(
                        "🎯 Tích chọn cấu phần thương mại:", 
                        available_trade, 
                        default=[c for c in available_trade if c in ['Xuất khẩu (triệu tỷ VND)', 'Nhập khẩu (triệu tỷ VND)', 'Cán cân thương mại hàng hóa (triệu tỷ VND)']], 
                        key="macro_trade_select"
                    )
                    
                elif macro_group == "🪙 4. Tỷ giá, Lạm phát & Biến động Tiền tệ":
                    sub_group = st.selectbox(
                        "📂 Chọn tiểu mục chỉ tiêu vĩ mô cụ thể:", 
                        ["Chỉ số giá & Tỷ giá thương mại (CPI, FX)", "Biến động Tăng trưởng Cung tiền & Tín dụng hệ thống"], 
                        key="macro_sub_select"
                    )
                    
                    if sub_group == "Chỉ số giá & Tỷ giá thương mại (CPI, FX)":
                        cpi_pool = [
                            'Chỉ số giá tiêu dùng (Tăng trưởng YoY)',
                            'Lạm phát cơ bản (Tăng trưởng YoY)',
                            'Tỷ giá Mua (VND-USD) (VCB)',
                            'Tỷ giá Bán (VND-USD) (VCB)'
                        ]
                        available_cpi = [c for c in cpi_pool if c in all_columns]
                        selected_cols = st.multiselect(
                            "🎯 Chọn chỉ tiêu Lạm phát & Tỷ giá:", 
                            available_cpi, 
                            default=available_cpi if available_cpi else None, 
                            key="macro_cpi_select"
                        )
                    else:
                        money_pool = [
                            'Tổng phương tiện thanh toán (triệu tỷ VND)',
                            'Tăng trưởng tổng phương tiện thanh toán MoM',
                            'Tăng trưởng tổng phương tiện thanh toán YoY',
                            'Tiền gửi (triệu tỷ VND)',
                            'Tăng trưởng tiền gửi YoY',
                            'Dư nợ tín dụng (triệu tỷ VND)',
                            'Tăng trưởng dư nợ tín dụng YoY',
                            'Dư nợ tín dụng/GDP danh nghĩa',
                            'Chênh lệch Tăng trưởng Tổng phương tiện thanh toán vs. Tín dụng',
                            'Lãi suất bình quân liên ngân hàng qua đêm (%)',
                            'Lãi suất huy động VND - Kỳ hạn > 12 tháng - Cao nhất (%)'
                            'Lãi suất huy động VND - Kỳ hạn > 12 tháng - Thấp nhất (%)'
                        ]
                        available_money = [c for c in money_pool if c in all_columns]
                        selected_cols = st.multiselect(
                            "🎯 Tùy chỉnh chọn cấu phần cung tiền & tín dụng:", 
                            available_money, 
                            default=[c for c in available_money if any(k in c for k in ['Tổng phương tiện', 'Dư nợ tín dụng (triệu tỷ VND)'])], 
                            key="macro_money_select"
                        )
                        
                elif macro_group == "🔑 5. Thị trường Hàng hóa toàn cầu & Tài sản":
                    asset_pool = [
                        'Vàng SJC - Giá bán ra (triệu VND/lượng)',
                        'Dầu thô - Brent (USD/thùng)',
                        'Giá vàng giao ngay (USD/ounce)'
                    ]
                    available_assets = [c for c in asset_pool if c in all_columns]
                    selected_cols = st.multiselect(
                        "🎯 Tích chọn các lớp tài sản để đối chiếu:", 
                        available_assets, 
                        default=available_assets if available_assets else None, 
                        key="macro_asset_select"
                    )

                # =====================================================================
                # LOGIC VẼ ĐỒ THỊ TỰ ĐỘNG PHÂN TÁCH THANG ĐO ĐỘNG (ĐA ĐỒ THỊ NẾU > 2 THANG ĐO)
                # =====================================================================
                st.markdown("### 📊 Đồ thị phân tích chi tiết")
                
                if selected_cols:
                    # 1. Định nghĩa từ điển để chuẩn hóa tên thang đo chuẩn cho từng cột thực tế
                    col_to_unit = {}
                    for col in selected_cols:
                        if any(k in col for k in ['%', 'YoY', 'MoM']):
                            col_to_unit[col] = "Tỷ lệ (%)"
                        elif any(k in col for k in ['PMI', 'Index']):
                            col_to_unit[col] = "Chỉ số (Index)"
                        elif any(k in col for k in ['VND-USD', 'Tỷ giá']):
                            col_to_unit[col] = "Tỷ giá (VND/USD)"
                        elif 'USD/thùng' in col:
                            col_to_unit[col] = "Giá dầu (USD/thùng)"
                        elif 'USD/ounce' in col:
                            col_to_unit[col] = "Giá vàng TG (USD/ounce)"
                        elif 'triệu VND/lượng' in col:
                            col_to_unit[col] = "Giá vàng VN (triệu VND/lượng)"
                        else:
                            col_to_unit[col] = "Giá trị tuyệt đối (triệu tỷ VND)"

                    # 2. Gom các cột đã chọn theo từng nhóm thang đo thực tế
                    unique_units = list(set(col_to_unit.values()))
                    
                    # Phân bổ thang đo vào Đồ thị 1 và Đồ thị 2 (nếu có)
                    chart1_units = unique_units[:2]  # Đồ thị 1 nhận tối đa 2 thang đo (Trái/Phải)
                    chart2_units = unique_units[2:]  # Thang đo thứ 3 trở đi sẽ bị đẩy xuống Đồ thị 2
                    
                    # Chia danh sách cột tương ứng cho 2 đồ thị
                    chart1_cols = [c for c in selected_cols if col_to_unit[c] in chart1_units]
                    chart2_cols = [c for c in selected_cols if col_to_unit[c] in chart2_units]

                    # ==========================================
                    # VẼ ĐỒ THỊ 1 (Hỗ trợ tối đa 2 bên Trái / Phải)
                    # ==========================================
                    if chart1_cols:
                        fig1 = go.Figure()
                        use_dual_axis1 = len(chart1_units) == 2
                        
                        unit_left1 = chart1_units[0]
                        unit_right1 = chart1_units[1] if use_dual_axis1 else None

                        for col in chart1_cols:
                            current_unit = col_to_unit[col]
                            display_name = col.split('\n')[0]
                            
                            # Chuẩn hóa nếu số thập phân thô biểu diễn phần trăm
                            y_val = macro_df[col] * 100 if (current_unit == "Tỷ lệ (%)" and macro_df[col].max() <= 1 and '%' not in col) else macro_df[col]
                            
                            # Cấu hình kiểu vẽ: Khối lượng thương mại/FDI vẽ dạng Cột (Bar), còn lại vẽ Đường (Line)
                            is_bar = (current_unit == "Giá trị tuyệt đối (triệu tỷ VND)") and (macro_group in ["🏢 2. Thu hút vốn đầu tư nước ngoài (FDI)", "🚢 3. Hoạt động Xuất Nhập Khẩu & Cán cân"])
                            
                            if use_dual_axis1:
                                if current_unit == unit_right1:
                                    fig1.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers', yaxis="y2"))
                                else:
                                    if is_bar:
                                        fig1.add_trace(go.Bar(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})"))
                                    else:
                                        fig1.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers'))
                            else:
                                if is_bar:
                                    fig1.add_trace(go.Bar(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})"))
                                else:
                                    fig1.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers'))

                        # Đường tham chiếu PMI 50 điểm
                        if macro_group == "🛒 1. Tiêu dùng, Sản xuất & PMI" and any('PMI' in c for c in chart1_cols):
                            pmi_ref_axis = "y2" if (use_dual_axis1 and unit_right1 == "Chỉ số (Index)") else "y"
                            fig1.add_shape(type="line", xref="paper", yref=pmi_ref_axis, x0=0, y0=50, x1=1, y1=50, line=dict(color="Red", width=1.5, dash="dash"))

                        # Cấu hình Layout Đồ thị 1
                        layout1 = {
                            "title": f"Diễn biến chính: {macro_group}",
                            "template": "plotly_white",
                            "hovermode": "x unified",
                            "height": 500,
                            "legend": dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                            "xaxis": dict(title="Thời gian (Kỳ/Ngày)", tickangle=45)
                        }
                        
                        if use_dual_axis1:
                            layout1["yaxis"] = dict(title=f"<b>Trục Trái</b> ({unit_left1})", side="left")
                            layout1["yaxis2"] = dict(title=f"<b>Trục Phải</b> ({unit_right1})", side="right", overlaying="y", showgrid=False)
                            layout1["barmode"] = "group"
                        else:
                            layout1["yaxis"] = dict(title=unit_left1)
                            if unit_left1 == "Giá trị tuyệt đối (triệu tỷ VND)":
                                layout1["barmode"] = "group"

                        fig1.update_layout(**layout1)
                        st.plotly_chart(fig1, use_container_width=True)

                    # ==========================================
                    # VẼ ĐỒ THỊ 2 (Dành cho thang đo thứ 3 dôi ra)
                    # ==========================================
                    if chart2_cols:
                        st.write("") 
                        st.markdown("##### 📌 Đồ thị bổ sung (Chỉ tiêu có thang đo khác)")
                        
                        fig2 = go.Figure()
                        use_dual_axis2 = len(chart2_units) == 2
                        
                        unit_left2 = chart2_units[0]
                        unit_right2 = chart2_units[1] if use_dual_axis2 else None

                        for col in chart2_cols:
                            current_unit = col_to_unit[col]
                            display_name = col.split('\n')[0]
                            
                            y_val = macro_df[col] * 100 if (current_unit == "Tỷ lệ (%)" and macro_df[col].max() <= 1 and '%' not in col) else macro_df[col]
                            is_bar = (current_unit == "Giá trị tuyệt đối (triệu tỷ VND)") and (macro_group in ["🏢 2. Thu hút vốn đầu tư nước ngoài (FDI)", "🚢 3. Hoạt động Xuất Nhập Khẩu & Cán cân"])

                            if use_dual_axis2:
                                if current_unit == unit_right2:
                                    fig2.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers', yaxis="y2"))
                                else:
                                    if is_bar:
                                        fig2.add_trace(go.Bar(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})"))
                                    else:
                                        fig2.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers'))
                            else:
                                if is_bar:
                                    fig2.add_trace(go.Bar(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})"))
                                else:
                                    fig2.add_trace(go.Scatter(x=x_axis_macro, y=y_val, name=f"{display_name} ({current_unit})", mode='lines+markers'))

                        # Cấu hình Layout Đồ thị 2
                        layout2 = {
                            "title": f"Chỉ tiêu bổ sung thuộc nhóm đơn vị riêng biệt",
                            "template": "plotly_white",
                            "hovermode": "x unified",
                            "height": 450,
                            "legend": dict(orientation="h", yanchor="top", y=-0.38, xanchor="center", x=0.5),
                            "xaxis": dict(title="Thời gian", tickangle=45)
                        }
                        
                        if use_dual_axis2:
                            layout2["yaxis"] = dict(title=f"<b>Trục Trái</b> ({unit_left2})", side="left")
                            layout2["yaxis2"] = dict(title=f"<b>Trục Phải</b> ({unit_right2})", side="right", overlaying="y", showgrid=False)
                            layout2["barmode"] = "group"
                        else:
                            layout2["yaxis"] = dict(title=unit_left2)
                            if unit_left2 == "Giá trị tuyệt đối (triệu tỷ VND)":
                                layout2["barmode"] = "group"

                        fig2.update_layout(**layout2)
                        st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Vui lòng lựa chọn ít nhất một chỉ tiêu cụ thể ở hộp chọn phía trên để kết xuất đồ thị phân tích.")
