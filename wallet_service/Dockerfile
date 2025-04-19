# Sử dụng Python 3.10
FROM python:3.10

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt và cài đặt thư viện trước (tối ưu cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ code vào container
COPY ./app /app

# Mở cổng Flask (nếu chạy API)
EXPOSE 5000

# Lệnh mặc định: chạy Flask app bằng Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

