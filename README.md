# Backend API cho Dự án BI MOOCCubeX và Dự đoán Kết quả Học tập

Đây là backend API được xây dựng bằng **FastAPI**, một framework Python hiệu suất cao để xây dựng các API web hiện đại, nhanh chóng, dễ học và dựa trên các chuẩn Python type hints. API này phục vụ cho ứng dụng frontend [Tên Frontend Project của bạn, ví dụ: MOOCCubeX Analytics Dashboard] được xây dựng bằng Next.js.

🎯 **Mục Đích của Repository**

Backend này chịu trách nhiệm cung cấp dữ liệu, xử lý logic nghiệp vụ và hỗ trợ các tính năng cốt lõi cho dự án phân tích dữ liệu MOOCCubeX và dự đoán kết quả học tập của học viên.

**Các tính năng chính của API bao gồm:**

* **Xác thực người dùng:** Cung cấp endpoints để đăng nhập, đăng ký (nếu có), và quản lý token (ví dụ: JWT) để phân quyền truy cập.
* **Quản lý khóa học:** Cung cấp API để truy xuất danh sách khóa học, thông tin chi tiết từng khóa học.
* **Cung cấp dữ liệu chuyên biệt:** API cho các nội dung liên quan đến "data-mining" và "data-quality", có thể bao gồm việc phục vụ dữ liệu đã xử lý hoặc kết quả phân tích.
* **Dự đoán kết quả học tập:** Endpoint chính để nhận dữ liệu đầu vào và trả về dự đoán kết quả học tập của học viên dựa trên các mô hình máy học đã huấn luyện.
* **Hỗ trợ BI:** Cung cấp các API để truy vấn dữ liệu tổng hợp hoặc các chỉ số cần thiết cho việc hiển thị trên dashboard BI.

🚀 **Cách Khởi Động (Backend)**

Để khởi chạy backend API này trên máy cục bộ của bạn, hãy làm theo các bước sau:

1.  **Clone repository (Nếu backend nằm trong một repo riêng):**
    ```bash
    git clone <URL_REPOSITORY_BACKEND_CỦA_BẠN>
    cd <TÊN_THƯ_MỤC_BACKEND_DỰ_ÁN>
    ```

2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    # Trên Windows
    venv\Scripts\activate
    # Trên macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình biến môi trường:**
    * Sao chép tệp `.env.example` thành `.env`.
    * Chỉnh sửa tệp `.env` với các cấu hình cần thiết (ví dụ: thông tin kết nối cơ sở dữ liệu, khóa bí mật JWT, API keys bên ngoài nếu có).
    ```env
    # Ví dụ .env
    DATABASE_URL="postgresql://user:password@host:port/database"
    SECRET_KEY="your_super_secret_key"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    # Thêm các biến khác nếu cần
    ```

5.  **Chạy database migrations (nếu sử dụng Alembic hoặc tương tự):**
    ```bash
    # Ví dụ với Alembic
    alembic upgrade head
    ```

6.  **Chạy server phát triển FastAPI:**
    Sử dụng Uvicorn (một ASGI server):
    ```bash
    uvicorn main:app --reload
    ```
    (Giả sử tệp chính của bạn là `main.py` và đối tượng FastAPI instance là `app`)

7.  Mở trình duyệt và truy cập:
    * API: `http://localhost:8000` (hoặc cổng khác nếu Uvicorn được cấu hình khác)
    * Tài liệu API tương tác (Swagger UI): `http://localhost:8000/docs`
    * Tài liệu API thay thế (ReDoc): `http://localhost:8000/redoc`
```
📜 **API Endpoints Chính (Ví dụ)**

API cung cấp các tài liệu tương tác tự động tại `/docs` (Swagger UI) và `/redoc`. Dưới đây là một số ví dụ về endpoints có thể có:

* **Authentication:**
    * `POST /api/v1/auth/token`: Đăng nhập, trả về access token.
    * `GET /api/v1/users/me`: Lấy thông tin người dùng hiện tại (yêu cầu token).
* **Courses:**
    * `GET /api/v1/courses/`: Lấy danh sách tất cả khóa học.
    * `GET /api/v1/courses/{course_id}`: Lấy thông tin chi tiết một khóa học.
* **Predictions:**
    * `POST /api/v1/predictions/student-outcome`: Gửi dữ liệu học viên và nhận kết quả dự đoán.
    * Body request có thể bao gồm các features cần thiết cho mô hình.
* **Data Mining / Data Quality Specific Endpoints:**
    * `GET /api/v1/data-mining/summary`: Lấy thông tin tổng quan về khai phá dữ liệu.
    * `GET /api/v1/data-quality/report/{dataset_id}`: Lấy báo cáo chất lượng dữ liệu cho một tập dữ liệu cụ thể.

🛠️ **Công Nghệ Sử Dụng**

* **Python** (Ngôn ngữ lập trình chính)
* **FastAPI** (Framework xây dựng API)
* **Uvicorn** (ASGI server để chạy FastAPI)
* **Pydantic** (Validation dữ liệu)
* **JSON Web Tokens (JWT)** (Cho xác thực)
* **Scikit-learn, Pandas, NumPy** (Cho xử lý dữ liệu và các tác vụ Machine Learning)

🤝 **Đóng Góp**

Nếu bạn muốn đóng góp cho dự án này, vui lòng [Mô tả quy trình đóng góp của bạn, ví dụ: fork repository, tạo branch mới, submit pull request với mô tả chi tiết].

📄 **Giấy Phép**

Dự án này được cấp phép theo [Tên Giấy Phép, ví dụ: MIT License]. Xem tệp `LICENSE` để biết thêm chi tiết (nếu có).

---

Hy vọng README này hữu ích cho backend API của bạn! Hãy tùy chỉnh thêm các chi tiết cụ thể của dự án như tên các endpoints, cấu trúc thư mục chính xác, và các công nghệ phụ trợ khác mà bạn sử dụng.
