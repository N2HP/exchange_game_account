# Sử dụng Python 3.10
FROM python:3.10
COPY ./app /app
# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code vào container
COPY . .

# Mở cổng Flask
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]



