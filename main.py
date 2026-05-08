import gspread as gs
import pandas as pd
import streamlit as st

# --- CẤU HÌNH ---
sheet_id = '1-YBba8d2RMhY5By3uT-NHSJ10Yt4ekcUwUb13kC3CmY'
sheet_name = 'Trang tính1'

# --- KẾT NỐI ---
@st.cache_resource # Dùng cache để không phải kết nối lại mỗi lần load trang
def init_connection():
    try:
        # Cách 1: Ưu tiên dùng Secrets (Dành cho Streamlit Cloud)
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"].to_dict()
            # Quan trọng: Sửa lỗi định dạng private_key
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            return gs.service_account_from_dict(creds_dict)
        
        # Cách 2: Dùng file local (Dành cho chạy dưới máy cá nhân)
        else:
            return gs.service_account(filename='Google Sheet Connector.json')
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return None

client = init_connection()

if client:
    sh = client.open_by_key(sheet_id)
    ws = sh.worksheet(sheet_name)

    st.title(f"Quản lý dữ liệu: {sh.title}")

    # --- HIỂN THỊ DỮ LIỆU ---
    st.subheader("Dữ liệu hiện tại")
    data = ws.get_all_records()
    df = pd.DataFrame(data=data)
    st.dataframe(df) # Dùng st.dataframe để hiển thị đẹp hơn trên web

    # --- NHẬP DỮ LIỆU ---
    st.divider()
    st.subheader("Nhập thông tin mới")
    
    # Dùng columns để form nhìn cân đối hơn
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Nhập tên")
    with col2:
        age = st.number_input("Nhập tuổi", min_value=1, max_value=100, value=18, step=1)
    with col3:
        job = st.selectbox('Chọn job', ['DA', 'BI', 'DS'])

    row = [name, age, job]
    
    if st.button("Submit here"):
        if name: # Kiểm tra tránh để tên trống
            with st.spinner("Đang lưu dữ liệu..."):
                ws.append_row(row)
                st.success(f"Đã thêm thành công: {name}")
                # Clear cache để bảng phía trên cập nhật lại dữ liệu mới
                st.cache_resource.clear()
                st.rerun() 
        else:
            st.warning("Vui lòng nhập tên trước khi bấm Submit.")
else:
    st.error("Không thể khởi tạo kết nối với Google Sheets. Vui lòng kiểm tra lại Secrets.")
