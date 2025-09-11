@echo off
REM Di chuyển đến thư mục dự án
D:
cd D:\CRC_Website

REM (Tùy chọn) Kích hoạt môi trường ảo nếu có
REM call venv\Scripts\activate

REM Mở localhost trong trình duyệt
start http://localhost:5000

REM Chạy ứng dụng Flask
python app.py
