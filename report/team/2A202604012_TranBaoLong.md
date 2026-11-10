# Báo cáo cá nhân — Trần Bảo Long (2A202604012)

## 1. Thông tin thành viên

- Họ tên: Trần Bảo Long
- MSSV: 2A202604012
- Email: tranbaolong5b@gmail.com
- GitHub: [BLong1501](https://github.com/BLong1501)

## 2. Phần việc phụ trách

Phụ trách CP3 — tool mới và unit test: thiết kế, cài đặt, ghi tài liệu, đăng ký tool vào hệ thống và kiểm tra bằng unit test offline.

## 3. Đóng góp cụ thể

- Xây dựng tool `verify_reference` tra cứu bản ghi tài liệu học thuật qua Crossref bằng DOI hoặc tiêu đề; trả về metadata và trạng thái tìm thấy.
- Thêm xử lý DOI không tồn tại, dữ liệu đầu vào rỗng/quá dài và lỗi HTTP; kết quả lỗi được trả dưới dạng error dict.
- Viết `TOOL.md`, khai báo tool trong `tools.yaml` và đăng ký trong `tools/__init__.py`.
- Viết 5 unit test với HTTP mock: DOI và metadata, tìm theo tiêu đề, input không hợp lệ, DOI không tồn tại và lỗi HTTP.
- Hỗ trợ thêm một vòng cải thiện quy tắc xác nhận publish: lần chạy v5 mới đạt 20/20 case. Đây là kết quả eval của prompt/tool declaration, không phải kết quả unit test của tool mới.

## 4. Bằng chứng

- Tool: [implementation](../../starter_v0/tools/verify_reference/tool.py), [TOOL.md](../../starter_v0/tools/verify_reference/TOOL.md).
- Đăng ký: [tools.yaml](../../starter_v0/artifacts/tools.yaml), [registry](../../starter_v0/tools/__init__.py).
- Unit test: [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py). Lệnh `pytest tests/test_tools_todo.py -q -k verify_reference`: **5 passed**. Toàn bộ test suite lần gần nhất: **72 passed, 14 skipped, 0 failed**; 14 test còn skipped là các TODO khác của starter.
- Commit CP3: [0f88142 — tool CP3](https://github.com/Vietzanh/K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval/commit/0f88142).
- Bằng chứng eval bổ sung: [v5 Gemini run](../../starter_v0/runs/v5_B_base_gemini_20261110T225536250990.json), **20/20**, không có provider error.
- Công cụ hỗ trợ: GitHub Copilot và pytest. Tự kiểm tra bằng unit test offline có HTTP mock, kiểm tra contract/registry và chạy eval; không đưa API key vào test hoặc báo cáo.

## 5. Tự đánh giá

Hoàn thành tool mới, tài liệu và hơn số unit test tối thiểu; các test của tool chạy offline, không phụ thuộc API thật. Kết quả kiểm tra toàn suite hiện còn 14 test TODO bị skip, nên chưa thể ghi nhận toàn suite là 0 skipped. Bước tiếp theo là phối hợp với người phụ trách eval nhóm để thêm case kiểm tra model chọn `verify_reference` đúng tình huống trong `eval_group.json`.
