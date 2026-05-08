import gspread as gs
import pandas as pd
import streamlit as st

key_file = 'Google Sheet Connector.json'
sheet_id = '1-YBba8d2RMhY5By3uT-NHSJ10Yt4ekcUwUb13kC3CmY'
sheet_name = 'Trang tính1'

client = gs.service_account(filename=key_file)
sh = client.open_by_key(sheet_id)
ws = sh.worksheet(sheet_name)

print(f"--- Kết nối thành công tới file: {sh.title} ---")

lst = ['Name','Age','Job']
# ws.append_row(lst)
print(ws.get_all_values())
 
data = ws.get_all_records()
df = pd.DataFrame(data=data)
df 

name = st.text_input("Nhap ten")
age = st.number_input("Nhap tuoi", value= 18, step=1)
job = st.selectbox('Chon job',['DA','BI','DS'])
row = [name,age,job]
submit = st.button("Submit here")
if submit:
    ws.append_row(row)