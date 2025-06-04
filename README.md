# Backend API cho Dự án BI MOOCCubeX và Dự đoán Kết quả Học tập

Đây là backend API được xây dựng bằng **FastAPI**, một framework Python hiệu suất cao để xây dựng các API web hiện đại, nhanh chóng, dễ học và dựa trên các chuẩn Python type hints. API này phục vụ cho ứng dụng frontend [Phân tích dữ liệu và dự đoán kết quả học tập cho bộ dữ liệu MOOCCubeX](https://github.com/dngan0365/bi-moocubex-frontend) được xây dựng bằng Next.js.

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

5.  **Chạy server phát triển FastAPI:**
    Sử dụng Uvicorn (một ASGI server):
    ```bash
    uvicorn main:app --reload
    ```
    (Giả sử tệp chính của bạn là `main.py` và đối tượng FastAPI instance là `app`)

6.  Mở trình duyệt và truy cập:
    * API: `http://localhost:8000` (hoặc cổng khác nếu Uvicorn được cấu hình khác)
    * Tài liệu API tương tác (Swagger UI): `http://localhost:8000/docs`
    * Tài liệu API thay thế (ReDoc): `http://localhost:8000/redoc`



## 📂 Hướng Dẫn Thư Mục
```
.
├── .github/                # Cấu hình liên quan đến GitHub (ví dụ: CI/CD workflow)
│   └── ...                 # Có thể chứa các workflow GitHub Actions như test.yml, deploy.yml
├── api/                    # Định nghĩa các endpoint API (có thể chia theo domain: course, user, auth, v.v.)
│   ├── auth/               # Các endpoint hoặc logic xác thực người dùng (login, register, v.v.)
│   ├── course.py           # Logic xử lý các API liên quan đến khóa học
│   ├── user.py             # Logic xử lý các API liên quan đến người dùng
│   └── router.py           # Cấu hình định tuyến chính, nơi include tất cả các router
├── db/                     # Quản lý kết nối và thao tác cơ sở dữ liệu
│   └── dynamodb.py         # Cấu hình và truy vấn DynamoDB
├── lambda/                 # Thư mục chứa các hàm Lambda (AWS Lambda functions)
│   ├── course.py           # Hàm xử lý liên quan đến khóa học trên Lambda
│   └── user.py             # Hàm xử lý liên quan đến người dùng trên Lambda
├── models/                 # Định nghĩa các schema/model dữ liệu
│   └── ...                 # Các tệp định nghĩa cấu trúc dữ liệu: User,...
├── tests/                  # Bộ test cho hệ thống (unit test, integration test)
│   ├── __init__.py         # Để Python nhận diện đây là một package
│   └── test_core.py        # Test logic lõi (ví dụ: test cho hàm, API, services)
├── utils.py                # Tiện ích, hàm dùng chung giữa nhiều phần (helpers)
├── create.py               # Tập lệnh tạo dữ liệu, migration, schema khởi tạo, etc.
├── main.py                 # Điểm bắt đầu chạy ứng dụng (FastAPI app hoặc Lambda handler chính)
├── requirements.txt        # Danh sách các thư viện Python cần thiết để chạy project
├── dev-requirements.txt    # Thư viện bổ sung khi phát triển (test, lint, debug)
├── command.txt             # Các lệnh CLI dùng trong quá trình phát triển hoặc hướng dẫn
├── README.md               # Tài liệu giới thiệu và hướng dẫn sử dụng dự án
├── .gitignore              # Tệp cấu hình để loại trừ file/folder không cần push lên Git


```
📜 **API Endpoints Chính (Ví dụ)**
* **Authentication:** 
    * `POST /api/auth/token`: Đăng nhập, trả về access token.
    * `GET /api/users/me`: Lấy thông tin người dùng hiện tại (yêu cầu token).
* **Những hàm trong các folder sau được tích hợp vào lambda nên không có router, chỉ show để tham khảo**
* **Courses:**
    * `GET /api/top-courses/`: 
        - Mô tả: Truy vấn 5 khóa học có số lượng người dùng tham gia nhiều nhất.
        - Trường dữ liệu trả về: course_id, name, user_count.
    * `GET /api/monthly-users/`:
        - Mô tả: Lấy số lượng người dùng duy nhất theo từng tháng kể từ năm 2019.
        - Trường dữ liệu trả về: year, month, num_users.
    * `GET /api/yearly-users`:
      - Mô tả: Lấy số lượng người dùng duy nhất theo từng năm kể từ 2019
      - Trường dữ liệu trả về: year, num_users.
    * `GET /api/summary-stats`: 
      - Mô tả: Trả về thống kê tổng quan: Tổng số người dùng, Số khóa học kể từ tháng 7/2020, Số người dùng trong năm 2020
      - Trường dữ liệu trả về: total_users, total_courses, courses_since_july_2020, users_in_2020.
    * `GET /api/label-distribution`:
        - Mô tả: Thống kê phân phối nhãn (label) của người dùng với điều kiện cụ thể về thời gian (end_year, end_month).
        - Trường dữ liệu trả về: label, num_users.
    * `GET /api/course-enrollments`:
        - Mô tả: Truy vấn 100 khóa học có nhiều người tham gia nhất, kèm thông tin chi tiết.
        - Trường dữ liệu trả về: course_id, name, school, start_date, end_date, user_count.
    * `GET /api/course/{course_id}`:
        - Mô tả: Lấy thông tin chi tiết của một khóa học dựa theo course_id.
        - Trường dữ liệu trả về: course_id, name, start_date, end_date, duration_days, certificate, assignment, exam, video, video_count, exercise_count, chapter_count.
    * `GET /api/search-labels?course_id={id}`:
        - Mô tả: Đếm số người dùng theo label của một khóa học cụ thể. 
        - Tham số bắt buộc: course_id. Trường dữ liệu trả về: label, count.
    * `GET /api/course-video-count?course_id={id}`:
        - Mô tả: Thống kê số lượng video theo tháng và năm cho một khóa học cụ thể.
        - Trường dữ liệu trả về: year, month, video_count.
    * `GET /api/course-exercise-count?course_id={id}`:
        - Mô tả: Thống kê số lượng bài tập được nộp theo tháng và năm cho một khóa học.
        - Trường dữ liệu trả về: year, month, exercise_count.
    * `GET /api/course-comment-reply-sentiment?course_id={id}`:
        - Mô tả: Phân tích cảm xúc (sentiment) của bình luận và phản hồi trong một khóa học.
        - Trường dữ liệu trả về: comments: danh sách theo sentiment_label, year, month, comment_count
        - replies: tương tự nhưng là reply_count.
    * `GET /api/course-users?course_id={id}`:
        - Mô tả: Trả về danh sách tối đa 100 người dùng đã tham gia khóa học.
        - Trường dữ liệu trả về: user_id, school, user_month, user_year.

* **Users:**
    * `GET /api/user-course-info`:
      - Mô tả: Lấy thông tin tổng hợp của người dùng trong khóa học (profile, bài tập, video, điểm)
      - Tham số: course_id, user_id. Trả về: user_info, user_exercises, user_video, user_comments
    * `GET /api/user-course-score-proportion`:
      - Mô tả: Lấy thông tin điểm số từng phần của người dùng trong khóa học
      - Tham số: course_id, user_id. Trả về: assignment_score, final_exam_score, video_score, total_score
    * `GET /api/user-course-behaviour`:
      - Mô tả: Truy vết hành vi học tập theo tháng (xem video, nộp bài)
      - Tham số: course_id, user_id. Trả về: user_video, user_exercises
    * `GET /api/user-course-predict`:
      - Mô tả: Dự đoán khả năng hoàn thành khóa học bằng mô hình ML
      - Tham số: course_id, user_id. Trả về: Danh sách theo từng phase gồm predicted_label


🛠️ **Công Nghệ Sử Dụng**

* **Python** (Ngôn ngữ lập trình chính)
* **FastAPI** (Framework xây dựng API)
* **Uvicorn** (ASGI server để chạy FastAPI)
* **Pydantic** (Validation dữ liệu)
* **JSON Web Tokens (JWT)** (Cho xác thực)
* **Scikit-learn, Pandas, NumPy** (Cho xử lý dữ liệu và các tác vụ Machine Learning)

🤝 **Đóng Góp**

Nếu bạn muốn đóng góp cho dự án này, vui lòng [Mô tả quy trình đóng góp của bạn, ví dụ: fork repository, tạo branch mới, submit pull request với mô tả chi tiết].

---

Hy vọng README này hữu ích cho backend API của bạn! Hãy tùy chỉnh thêm các chi tiết cụ thể của dự án như tên các endpoints, cấu trúc thư mục chính xác, và các công nghệ phụ trợ khác mà bạn sử dụng.
