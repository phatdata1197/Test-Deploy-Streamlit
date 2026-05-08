Code của bạn đã **đúng và khắc phục được lỗi PEM trước đó** nhờ dòng:

```python
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
```

Dòng này rất quan trọng vì khi paste private key vào Streamlit Secrets, các ký tự xuống dòng (`\n`) thường bị chuyển thành chuỗi ký tự literally là `\` và `n`, gây ra lỗi `InvalidPadding`. Dòng code trên sẽ chuyển chúng về dạng xuống dòng đúng.

Dưới đây là phiên bản **tối ưu hơn**, tận dụng tốt hơn cơ chế cache của Streamlit và cải thiện UX:

```python
import gspread as gs
import pandas as pd
import streamlit as st

# --- CẤU HÌNH ---
# Nên chuyển vào Secrets nếu deploy công khai
SHEET_ID = '1-YBba8d2RMhY5By3uT-NHSJ10Yt4ekcUwUb13kC3CmY'
SHEET_NAME = 'Trang tính1'

# --- KẾT NỐI ---
@st.cache_resource
def get_client():
    """Khởi tạo client kết nối Google Sheets."""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            # FIX LỖI PEM: Chuyển \\n thành \n thật sự
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
            return gs.service_account_from_dict(creds_dict)
        else:
            # Local development
            return gs.service_account(filename='Google Sheet Connector.json')
    except Exception as e:
        st.error(f"❌ Lỗi kết nối: {e}")
        return None

@st.cache_data(ttl=10)  # Cache dữ liệu 10 giây
def load_data(_client, sheet_id, sheet_name):
    """Tách riêng việc load data để cache hiệu quả hơn."""
    try:
        sh = _client.open_by_key(sheet_id)
        ws = sh.worksheet(sheet_name)
        data = ws.get_all_records()
        return data, sh.title
    except gs.WorksheetNotFound:
        st.error(f"❌ Không tìm thấy sheet '{sheet_name}'")
        return [], None
    except Exception as e:
        st.error(f"❌ Lỗi đọc dữ liệu: {e}")
        return [], None

# --- UI CHÍNH ---
st.set_page_config(page_title="Quản lý Google Sheet", layout="wide")

client = get_client()

if not client:
    st.error("Không thể kết nối. Vui lòng kiểm tra:")
    st.markdown("""
    1. Đã thêm `gcp_service_account` vào Secrets chưa?
    2. Đã bật Google Sheets API trong Google Cloud chưa?
    3. Đã share spreadsheet với service account email chưa?
    """)
    st.stop()

# Load dữ liệu
data, sheet_title = load_data(client, SHEET_ID, SHEET_NAME)

if sheet_title:
    st.title(f"📊 Quản lý: {sheet_title}")
    
    # Hiển thị dữ liệu
    st.subheader("Dữ liệu hiện tại")
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sheet đang trống hoặc không có dữ liệu.")

    # Form nhập liệu
    st.divider()
    st.subheader("➕ Thêm dữ liệu mới")
    
    with st.form("input_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Họ và tên", placeholder="Nguyễn Văn A")
        with col2:
            age = st.number_input("Tuổi", min_value=1, max_value=120, value=25, step=1)
        with col3:
            job = st.selectbox('Vị trí', ['DA', 'BI', 'DS', 'DE', 'PM'])
        
        submitted = st.form_submit_button("🚀 Thêm vào Sheet", use_container_width=True)
        
        if submitted:
            if not name or not name.strip():
                st.warning("⚠️ Vui lòng nhập họ tên!")
            else:
                try:
                    with st.spinner("Đang ghi dữ liệu..."):
                        # Mở lại worksheet để ghi (không dùng cached object cho ghi)
                        sh = client.open_by_key(SHEET_ID)
                        ws = sh.worksheet(SHEET_NAME)
                        ws.append_row([name.strip(), age, job])
                        
                        # Xóa cache data để load lại
                        load_data.clear()
                        st.success(f"✅ Đã thêm: {name} ({job})")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Lỗi khi ghi dữ liệu: {e}")
```

## 🎯 Những điểm cải tiến chính:

1. **Tách biệt Cache:** 
   - `@st.cache_resource`: Chỉ cache connection (không thay đổi)
   - `@st.cache_data`: Cache dữ liệu sheet, có `ttl=10` (tự động refresh sau 10s)

2. **Dùng `st.form`:** 
   - Ngăn việc app bị rerun mỗi khi nhập 1 ký tự (hiệu quả hơn `if st.button`)

3. **Xử lý lỗi chi tiết:** 
   - Bắt lỗi `WorksheetNotFound` nếu sai tên sheet
   - Kiểm tra `name.strip()` để tránh nhập khoảng trắng

4. **Clear cache đúng cách:**
   - Chỉ xóa cache `load_data` (không xóa cache connection) khi thêm dữ liệu mới

5. **UX tốt hơn:**
   - Thêm icon, layout rộng hơn (`layout="wide"`), placeholder cho input

## ⚠️ Lưu ý quan trọng:

Đảm bảo bạn đã **Share Google Sheet** với email:  
`demo-gs@stone-index-495614-p4.iam.gserviceaccount.com`  
(với quyền **Editor**), nếu không sẽ báo lỗi permission denied.
