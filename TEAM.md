# Team

## Thông tin nhóm

- Tên nhóm: NhomABCD
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/Vietzanh/K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval · nhánh `main` · commit chốt: (điền khi nộp)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Doan Sy Hung | 2A202603990 | hungizumi1210@gmail.com | https://github.com/hgmdz1210 | Prompt & Eval lead |
|   2 | Long | <điền MSSV> | <điền email> | <điền GitHub> | Tool mới & test |
|   3 | Trần Việt Anh | 2A202604029 | 26ai.anhtv2@vinuni.edu.vn | https://github.com/Vietzanh | Eval nhóm & Tool unit test |
|   4 | Phạm Văn Chiêu | 2A202604033 | chieupham1011@gmail.com | https://github.com/pvchiu | UI, chat live & báo cáo |

## Chia việc

| Vai | Thành viên | Phụ trách | File chính | Điểm |
| --- | ---------- | --------- | ---------- | ---- |
| 1. Prompt & Eval lead | Hưng | Sửa prompt/tool declaration, chạy v1→v3, ghi `version_log.csv`, bảng B1 + B2 | `system_prompt.md`, `tools.yaml`, `runs/` | C1, C2, C3 |
| 2. Tool mới & test | Long | Viết ≥ 1 tool mới, `TOOL.md`, đăng ký trong `tools/__init__.py` + `tools.yaml`, ≥ 3 test/tool, `pytest` 0 failed, bảng B5a | `tools/<tên>/`, `tests/test_tools_todo.py` | C3 |
| 3. Eval nhóm | Việt Anh | Viết đúng 10 case (5 single + 5 multi), ≥ 1 case route tới tool mới, chạy `--suite group`, bảng B3 | `data/eval_group.json` | C4 |
| 4. UI, chat live & báo cáo | Chiêu | UI Streamlit + tunnel, 3 lượt chat live, Phần A trước showdown, ráp Phần B, `TEAM.md`, push/nộp | `app.py`, `requirements.txt`, `transcripts/`, `group_report.md` | C6, C7 |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## PhamVanChieu-2A202604033

### Phần việc phụ trách

- Vai 4: Xây dựng UI/UX Streamlit (`starter_v0/app.py`), cập nhật `starter_v0/requirements.txt`, mở link dùng thử (Cloudflare Tunnel).
- Chạy chat live (`starter_v0/chat.py`), hoàn thiện Phần A trước showdown và tổng hợp Phần B trong `report/team/group_report.md`.

### Đóng góp cụ thể

- Thiết kế và xây dựng giao diện web Streamlit (`starter_v0/app.py`): đọc động `system_prompt.md` + `tools.yaml`, hỗ trợ chuyển đổi qua lại trực tiếp giữa các snapshot Git (`v0`–`v4`) và bản trên đĩa (`Current`), tích hợp `run_model_tool_loop` (`chat.py`), hiển thị minh bạch tool calls & lỗi tool (không che lỗi), nút tương tác `clarify` (`yes_no`/`choice`), câu hỏi mẫu Showdown, tự động lưu & tải transcript JSON.
- Cập nhật `starter_v0/requirements.txt` (`streamlit>=1.50.0`) và kiểm thử cục bộ (`AppTest` đủ các version `v0`–`v4`, HTTP 200, `pytest` `72 passed, 14 skipped`, `0 failed`).
- Hoàn thiện Phần A (`A1`–`A3` gồm tool mới `verify_reference`), mục UI ở `B5a` và mục `5` trong `report/team/group_report.md`; hoàn thiện báo cáo cá nhân `report/team/2A202604033_PhamVanChieu.md`.
- *(Còn phiên chat live ≥ 3 lượt trên bản chốt mới nhất để điền `B4`, mở link Cloudflare Tunnel công khai và ráp Phần B cùng nhóm để chốt nộp bài.)*

### Bằng chứng

- Báo cáo cá nhân: `report/team/2A202604033_PhamVanChieu.md`
- Code, dependency UI & bằng chứng lỗi provider: `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/runs/v0_B_base_gemini_20261110T181044880645.json`
- Báo cáo nhóm (Phần A, B5a UI, Mục 5): `report/team/group_report.md`
- Transcript live bản chốt (C6/B4) & Link Cloudflare Tunnel: *(bổ sung ở commit chốt sau khi chạy phiên ≥ 3 lượt chuẩn và mở tunnel)*


## TranVietAnh-2A202604029

### Phần việc phụ trách

- Xây dựng bộ 10 test case bổ sung cho bộ evaluation có sẵn, gồm 5 single-turn (query) và 5 multi-turn (turns).
- Thiết kế các tình huống kiểm tra khả năng routing tool, trích xuất arguments, xử lý ngữ cảnh nhiều lượt và kiểm soát hành động bên ngoài.
- Bổ sung các test case nhằm đánh giá khả năng sử dụng những tool mới do nhóm phát triển.
- Chạy evaluation trên Prompt v4, phân tích kết quả và xác định các điểm cần cải thiện.

### Đóng góp cụ thể

- Thiết kế bộ test: Xây dựng 10 test case trong eval_group.json, bao phủ các tình huống như chuẩn hóa Twitter/X handle, tìm kiếm tweet theo chủ đề, lựa chọn phạm vi tìm kiếm, format dữ liệu có sẵn và tra cứu policy nội bộ.
- Kiểm tra các tool mới: Bổ sung các trường hợp kiểm tra khả năng routing đến verify_reference, policy, papers và paper_text, giúp đánh giá mức độ tích hợp các chức năng nghiên cứu mới của nhóm.
- Kiểm tra xử lý hội thoại nhiều lượt: Thiết kế các tình huống yêu cầu agent kế thừa chủ đề, cập nhật bộ lọc tìm kiếm, thay đổi số lượng kết quả, duy trì phạm vi truy vấn và xử lý yêu cầu hủy hành động gửi Telegram.
- Rà soát expected output: Đối chiếu từng test case với khai báo tool trong tools.yaml, chuẩn hóa expected tool calls và arguments để đảm bảo mỗi case kiểm tra được hành vi cụ thể, hạn chế các trường hợp pass dù agent truyền thiếu tham số quan trọng.
- Chạy thử nghiệm và phân tích kết quả: Thực hiện evaluation với prompt v4 , thu được kết quả:
  - Case accuracy: 90% (9/10 cases passed).
  - Tool routing accuracy: 100%.
  - Argument accuracy: 90%.
  - Multi-turn accuracy: 100%.
- Phân tích lỗi: Xác định G02 là test case duy nhất thất bại. Agent gọi đúng social_search, truyền đúng query và limit, nhưng không truyền tường minh search_type="Latest" mà dựa vào giá trị mặc định của tool. Từ đó nhận diện vấn đề trong việc ánh xạ đầy đủ intent của người dùng sang arguments.

### Bằng chứng

- File commit:
  - starter_v0/data/eval_group.json: Bộ 10 test case nhóm.
  - Evaluation run: v4_B_group_openrouter_20261111T081004535910.
  - Báo cáo nhóm `report/team/group_report.md` mục B3. Team Eval Cases
