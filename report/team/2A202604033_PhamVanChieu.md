# Báo cáo cá nhân — Phạm Văn Chiêu - 2A202604033

## 1. Thông tin thành viên

- Họ tên: Phạm Văn Chiêu
- MSSV: 2A202604033
- Email: chieupham1011@gmail.com
- GitHub: https://github.com/pvchiu

## 2. Phần việc phụ trách

Theo phân công trong [TEAM.md](../../TEAM.md) (Vai 4 — UI, chat live & báo cáo):

- Xây dựng giao diện web UI/UX bằng Streamlit (`starter_v0/app.py`) và cập nhật dependency trong `starter_v0/requirements.txt`.
- Triển khai link dùng thử public (Cloudflare Tunnel) để các nhóm khác test trong buổi showdown.
- Chạy phiên chat live (≥ 3 lượt gồm yêu cầu thường, thiếu thông tin → `clarify`, và xác nhận trước khi `send`) lưu vào `starter_v0/transcripts/*.transcript.json` và điền bảng B4.
- Soạn Phần A trong `report/team/group_report.md` trước showdown và tổng hợp/ráp Phần B báo cáo nhóm sau khi các thành viên hoàn tất phần của mình.
- Giai đoạn khởi tạo: cấu hình `.env`, kiểm tra hoạt động các tool (`lookup`, `fetch`, `timeline`, `social_search`), kiểm tra provider và chạy thử baseline `v0` phát hiện vấn đề quota của Gemini free tier.

## 3. Đóng góp cụ thể

1. **Xây dựng giao diện web Research Agent (`starter_v0/app.py`):**
   - Tích hợp trực tiếp vòng lặp `run_model_tool_loop`, `trim_history`, `write_transcript` từ `starter_v0/chat.py` và đọc động `artifacts/system_prompt.md`, `artifacts/tools.yaml` (qua `load_tool_declarations`), giúp UI tự cập nhật khi nhóm tối ưu `v1`–`v3` và tích hợp tool mới `verify_reference`.
   - Hỗ trợ **chuyển đổi qua lại trực tiếp giữa các phiên bản (`v0`–`v4` từ lịch sử Git và bản `Current` trên đĩa)** ở chế độ chỉ đọc trong bộ nhớ (không làm bẩn file của nhóm), tự động reset hội thoại khi đổi phiên bản để test đối chiếu hành vi qua từng vòng tối ưu.
   - Thiết kế UX minh bạch (đáp ứng tiêu chí C6, không che lỗi tool): tự động kiểm tra kết quả từng tool call trong `extract_turn_diagnostics()`, hiển thị rõ cảnh báo lỗi provider/tool (`st.error`) và tự động mở khung *Chi tiết Tool Calls & Kết quả* (3 tab: *Kết quả tóm tắt*, *Arguments*, *Raw JSON*) khi có lỗi.
   - Thiết kế UX tương tác cho `clarify` và boundary xác nhận `send`: hiển thị nút bấm nhanh **Có, xác nhận gửi** / **Không, hủy bỏ** khi `response_type == "yes_no"`, hiển thị nút chọn theo `options` khi `response_type == "choice"`, và cảnh báo guardrail `needs_confirmation` / `trust_boundary` (`untrusted_text` của tool `policy`).
   - Xây dựng sidebar hỗ trợ demo/showdown: chọn provider/model, 7 câu hỏi mẫu chạy nhanh (bao gồm test `verify_reference`), xem danh sách tools & system prompt đang nạp, trạng thái API key (không lộ secret), tự động lưu và cho phép tải xuống transcript JSON theo đúng chuẩn `chat.py`.
2. **Cập nhật dependency và hoàn thiện phần việc chuẩn bị báo cáo:**
   - Cài đặt `streamlit==1.67.0` trong môi trường ảo và bổ sung `streamlit>=1.50.0` vào `starter_v0/requirements.txt`.
   - Khôi phục file mẫu `report/team/MSSV_HoTen.md`, điền đầy đủ thông tin cá nhân + link GitHub vào `TEAM.md`, cập nhật Phần A (`A1`–`A3` gồm cả `verify_reference`), mục UI (`B5a`) và Mục 5 trong `report/team/group_report.md`.
3. **Phần còn cần hoàn tất ở lượt chốt nộp bài cùng nhóm:**
   - Chạy phiên chat live chính thức ≥ 3 lượt trên bản chốt mới nhất (`v4`) gồm yêu cầu thường, thiếu thông tin `clarify`, xác nhận `send` để lưu `.transcript.json` chuẩn C6 và điền bảng `B4`.
   - Bật `cloudflared tunnel --url http://localhost:8501` lấy URL public điền vào `A1` & `B5a` khi showdown / nộp bài.
   - Ráp Phần B (`B1`–`B3` từ Hưng, Long, Việt Anh) và điền commit chốt vào `TEAM.md`.

## 4. Bằng chứng

- **File tạo / chỉnh sửa (thuộc phần cá nhân & Vai 4):**
  - `starter_v0/app.py`
  - `starter_v0/requirements.txt`
  - `TEAM.md`
  - `report/team/group_report.md` (Mục 1, Phần A `A1`–`A3`, B5a dòng UI, Mục 5)
  - `report/team/2A202604033_PhamVanChieu.md`
  - `starter_v0/runs/v0_B_base_gemini_20261110T181044880645.json` (bằng chứng thực tế lỗi giới hạn 5 RPM — `9/20` case `provider_error` của Gemini free tier phục vụ Mục 5)
  - Phiên chat thử giao diện thực tế ban đầu trên máy với OpenAI `gpt-4o-mini` (`lookup`) đã chạy kiểm chứng UI; transcript live ≥ 3 lượt chính thức trên bản chốt `v4` sẽ được chạy và commit bổ sung cho `B4` / `C6`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - **Công cụ AI đã dùng:** Trợ lý AI coding (Antigravity) hỗ trợ giải thích cấu trúc repo/rubric, kiểm tra tích hợp với `chat.py` / `providers` / `tools`, và xây dựng `starter_v0/app.py`.
  - **Cách tự kiểm tra kết quả:**
    1. Chạy `pytest` trong `starter_v0/` sau khi kéo `v4` và `verify_reference` của nhóm để xác minh contract test + example test + unit test tool mới đều xanh (`72 passed, 14 skipped`, `0 failed`).
    2. Chạy kiểm thử tự động `streamlit.testing.v1.AppTest` cho `starter_v0/app.py` để kiểm tra chuyển đổi qua lại `Current` / `v4` / `v3` / `v2` / `v1` / `v0`, nạp đủ 11 tools (kể cả `verify_reference`), hiển thị lỗi tool (`HTTPError 429`), cảnh báo `needs_confirmation`, và nút bấm `clarify` (`yes_no` / `choice`).
    3. Khởi chạy `streamlit run app.py` (cả chế độ headless `HTTP 200` lẫn chạy live trên trình duyệt với OpenAI `gpt-4o-mini`), đồng thời cài và xác minh `cloudflared version 2026.10.7` sẵn sàng trên máy.

## 5. Tự đánh giá

- Đã hoàn thành phần code UI/UX hoàn chỉnh (tương thích động với `v4` và tool mới `verify_reference`, hỗ trợ đổi snapshot `v0`–`v4`, minh bạch lỗi tool), `requirements.txt`, `TEAM.md`, Phần A của báo cáo nhóm, và báo cáo cá nhân đúng phạm vi Vai 4 mà không sửa/chồng lấn phần tối ưu prompt/tools (Hưng), tool mới/unit test (Long), hay 10 case eval nhóm (Việt Anh).
- 3 đầu việc cuối cần chốt trước giờ nộp bài cùng cả nhóm: (1) chạy 1 phiên chat live ≥ 3 lượt trên bản chốt mới nhất (`v4`) để điền `B4` và commit file `.transcript.json`; (2) mở Cloudflare Tunnel lấy link công khai điền vào `A1` & `B5a`; (3) ráp Phần B (`B1`–`B3`, `B5a`) với các thành viên và ghi commit chốt vào `TEAM.md`.
