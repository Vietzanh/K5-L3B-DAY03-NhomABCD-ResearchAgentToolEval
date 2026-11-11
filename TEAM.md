# Team

## Thông tin nhóm

- Tên nhóm: NhomABCD
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/Vietzanh/K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval · nhánh `main` · commit chốt: (điền khi nộp)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đoàn Sỹ Hưng | 2A202603990 | hungizumi1210@gmail.com | https://github.com/hgmdz1210 | Prompt & Eval lead |
|   2 | Trần Bảo Long | 2A202604012 | tranbaolong5b@gmail.com | https://github.com/BLong1501 | Tool mới & test |
|   3 | Trần Việt Anh | 2A202604029 | 26ai.anhtv2@vinuni.edu.vn | https://github.com/Vietzanh | Eval nhóm & Tool unit test |
|   4 | Phạm Văn Chiêu | 2A202604033 | chieupham1011@gmail.com | https://github.com/pvchiu | UI, chat live & báo cáo |

## Chia việc

| Vai | Thành viên | Phụ trách | File chính | Điểm |
| --- | ---------- | --------- | ---------- | ---- |
| 1. Prompt & Eval lead | Hưng | Sửa prompt/tool declaration, chạy v0→v7, ghi `version_log.csv`, bảng B1 + B2, mục 3 + B6 | `system_prompt.md`, `tools.yaml`, `runs/` | C1, C2, C3 |
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

## DoanSyHung-2A202603990

### Phần việc phụ trách

- Vai 1 (Prompt & Eval lead): sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, chạy base eval v0→v7, ghi `starter_v0/artifacts/version_log.csv`, viết bảng B1 + B2, mục 3 (Giải pháp) và B6 (Reflection) trong `report/team/group_report.md`.

### Đóng góp cụ thể

- Setup CP1 với provider OpenAI (`gpt-4o-mini`): preflight pass, `pytest` xanh, chạy baseline v0 = 0.70 (14/20) và phân loại 6 case FAIL (`out_of_scope`, `missing_info`, `wrong_boundary`, `wrong_tool`).
- v1 (`system_prompt.md`): bỏ 3 chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước); thêm ranh giới cho ngoài phạm vi, `clarify` khi thiếu handle/URL, và xác nhận trước khi `send`. Kết quả 0.70 → 0.90.
- v2 (`tools.yaml`): viết lại `clarify` (`response_type` bắt buộc, nghĩa của `text`/`yes_no`/`choice`) và `send` (chỉ gọi sau xác nhận `yes_no`). Sửa được R11.
- v3: merge tool mới `verify_reference` của Long vào `main`, đo bằng base eval rằng tool mới không làm hỏng case cũ (0.95). Ghi rõ trong log rằng mức tăng là do dao động của R10, không phải nhờ tool.
- v4: sửa rule gửi trong prompt (luôn `clarify(yes_no)` trước) và mô tả `timeline.screenname`. Sửa được R12, R10.
- v5: đưa mô tả `lookup` (convention query/topic/timeframe, do Long viết) vào `tools.yaml`. Đạt **1.00 (20/20)**.
- v6: thêm mục Routing vào prompt và viết lại 6 mô tả tool còn sơ sài (`social_search`, `fetch`, `format`, `policy`, `papers`, `paper_text`) để đạt tiêu chí C2. Base giữ 1.00.
- v7: đưa `social_search.search_type` vào `required`. Eval nhóm (OpenAI) tăng 0.90 → **1.00**, sửa G02.
- Chạy lại eval nhóm bằng `openai/gpt-4o-mini` cho v5, v6, v7, để giả thuyết G02 được đo cùng model với base.
- Phát hiện và xử lý lỗi `core.autocrlf` làm đổi `prompt_hash` dù nội dung không đổi; kiểm tra hash trước mỗi run để mỗi version chỉ khác đúng artifact đã ghi trong log.
- Viết B1 (bảng v0–v7, giả thuyết, metric, run file, nhận xét về dao động) và B2 (phân tích 11 lượt FAIL qua các version, phân loại lỗi prompt và lỗi tool declaration), mục 3 Giải pháp, B6 Reflection; báo cáo cá nhân `report/team/2A202603990_DoanSyHung.md`.

### Bằng chứng

- Run JSON: `starter_v0/runs/v0_B_base_openai_20261110T181658629110.json`, `v1_..._20261110T190322024377.json`, `v2_..._20261110T191022732055.json`, `v3_..._20261110T193829691099.json`, `v4_..._20261110T194933137985.json`, `v5_B_base_openai_20261111T085803114637.json`, `v6_B_base_openai_20261111T092030353316.json`, `v7_B_base_openai_20261111T092529002036.json`; group (OpenAI): `v5/v6/v7_B_group_openai_*.json`.
- Version log: `starter_v0/artifacts/version_log.csv` (v0–v7).
- Commit: `62d409a` (v0), `1d1be28` (v1), `a8b1d00` (v2), `a9c8cda` (v3), `1ec845d` (v4), `d1fa954` (v5), `e02142c` (v6), `fe451fc` (v7).
- Báo cáo nhóm: `report/team/group_report.md` mục 3, B1, B2, B6.
- Báo cáo cá nhân: `report/team/2A202603990_DoanSyHung.md`.

## PhamVanChieu-2A202604033

### Phần việc phụ trách

- Vai 4: Xây dựng UI/UX Streamlit (`starter_v0/app.py`), cập nhật `starter_v0/requirements.txt`, mở link dùng thử (Cloudflare Tunnel).
- Chạy chat live (`starter_v0/chat.py`), hoàn thiện Phần A trước showdown và tổng hợp Phần B trong `report/team/group_report.md`.

### Đóng góp cụ thể

- Thiết kế và xây dựng giao diện web Streamlit (`starter_v0/app.py`): đọc động `system_prompt.md` + `tools.yaml`, hỗ trợ chuyển đổi qua lại trực tiếp giữa các snapshot Git (`v0`–`v7`) và bản trên đĩa (`Current`), tích hợp `run_model_tool_loop` (`chat.py`), hiển thị minh bạch tool calls & lỗi tool (không che lỗi), nút tương tác `clarify` (`yes_no`/`choice`), câu hỏi mẫu Showdown, tự động lưu & tải transcript JSON.
- Cập nhật `starter_v0/requirements.txt` (`streamlit>=1.50.0`), triển khai link dùng thử Cloudflare Tunnel (`https://meals-widescreen-seeking-oil.trycloudflare.com`), kiểm thử cục bộ (`AppTest` đủ cả 9 lựa chọn `Current` + `v0`–`v7`, `HTTP 200`, `pytest` `72 passed, 14 skipped`, `0 failed`).
- Hoàn thiện Phần A (`A1`–`A3` gồm tool mới `verify_reference`), bảng `B4` (6 lượt chat live trên `v7` qua UI/tunnel), mục UI ở `B5a` và mục `5` trong `report/team/group_report.md`; hoàn thiện báo cáo cá nhân `report/team/2A202604033_PhamVanChieu.md`.
- Thực hiện phiên chat live 6 lượt trên bản `v7` (`openai/gpt-4o-mini`) qua UI & Cloudflare Tunnel: `lookup` (tin AI), `verify_reference` (DOI Crossref), `clarify(text)` $\rightarrow$ bổ sung `@karpathy` (`timeline`), và `clarify(yes_no)` $\rightarrow$ hủy `send` an toàn; lưu tại `starter_v0/transcripts/ui_v7_openai_20261111T103408555020.transcript.json`.

### Bằng chứng

- Báo cáo cá nhân: `report/team/2A202604033_PhamVanChieu.md`
- Code, dependency UI & bằng chứng lỗi provider: `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/runs/v0_B_base_gemini_20261110T181044880645.json`
- Transcript chat live 6 lượt trên `v7` (`C6`/`B4`): `starter_v0/transcripts/ui_v7_openai_20261111T103408555020.transcript.json`
- Link Cloudflare Tunnel dùng thử: `https://meals-widescreen-seeking-oil.trycloudflare.com` (chạy `cloudflared tunnel --url http://localhost:8501`, `HTTP 200`)
- Báo cáo nhóm (Phần A, B4, B5a UI, Mục 5): `report/team/group_report.md`


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
- Chạy thử nghiệm và phân tích kết quả: Thực hiện evaluation trên các phiên bản prompt , thu được kết quả:
  - Prompt v4: Case accuracy đạt 90% (9/10 cases passed), Prompt v6: Case accuracy đạt 80% (8/10 cases passed)
  - Prompt v7: Case accuracy đạt 100% (10/10 cases passed).
    - Case accuracy: 100%.
    - Tool routing accuracy: 100%.
    - Argument accuracy: 10%.
    - Multi-turn accuracy: 100%.
- Phân tích lỗi qua các phiên bản:
  - G02 ở v4 và v6: Agent gọi đúng social_search, truyền đúng query và limit nhưng không truyền tường minh search_type="Latest", thay vào đó phụ thuộc vào giá trị mặc định của tool.
  - G05 ở v6: Agent gọi đúng policy nhưng chọn sai policy_area="external_publishing" thay vì tool_usage, khiến truy vấn policy trả về danh sách rỗng.

### Bằng chứng
- File/commit/PR:
  - starter_v0/data/eval_group.json: Bộ 10 test case.
  - Evaluation run v4: v4_B_group_openrouter_20261111T081004535910.
  - Evaluation run v6: v6_B_group_openrouter_20261111T091405140926.
  - Evaluation run v7: v7_B_group_openrouter_20261111T094308640312.
  - Báo cáo nhóm report/team/group_report.md mục (B3. Team Eval Cases)

## Trần Bảo Long - 2A202604012
 ### Phần việc phụ trách

- Phụ trách CP3 — tool mới và unit test: thiết kế, cài đặt, ghi tài liệu, đăng ký tool vào hệ thống và kiểm tra bằng unit test offline.

###  Đóng góp cụ thể

- Xây dựng tool `verify_reference` tra cứu bản ghi tài liệu học thuật qua Crossref bằng DOI hoặc tiêu đề; trả về metadata và trạng thái tìm thấy.
- Thêm xử lý DOI không tồn tại, dữ liệu đầu vào rỗng/quá dài và lỗi HTTP; kết quả lỗi được trả dưới dạng error dict.
- Viết `TOOL.md`, khai báo tool trong `tools.yaml` và đăng ký trong `tools/__init__.py`.
- Viết 5 unit test với HTTP mock: DOI và metadata, tìm theo tiêu đề, input không hợp lệ, DOI không tồn tại và lỗi HTTP.
- Hỗ trợ thêm một vòng cải thiện quy tắc xác nhận publish: lần chạy v5 mới đạt 20/20 case. Đây là kết quả eval của prompt/tool declaration, không phải kết quả unit test của tool mới.
- chạy kiểm tra lại v3, v4, v5.

###  Bằng chứng

- Tool: [implementation](../../starter_v0/tools/verify_reference/tool.py), [TOOL.md](../../starter_v0/tools/verify_reference/TOOL.md).
- Đăng ký: [tools.yaml](../../starter_v0/artifacts/tools.yaml), [registry](../../starter_v0/tools/__init__.py).
- Unit test: [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py). Lệnh `pytest tests/test_tools_todo.py -q -k verify_reference`: **5 passed**. Toàn bộ test suite lần gần nhất: **72 passed, 14 skipped, 0 failed**; 14 test còn skipped là các TODO khác của starter.
- Base eval v5 (Gemini, `gemini-3.8-flash`): **20/20 passed (100%)**, `provider_error_cases=0`; kết quả được lưu trong [v5 run JSON](../../starter_v0/runs/v5_B_base_gemini_20261110T225536250990.json) nhánh verify-reference-tool. Đây là base eval kiểm tra prompt/routing/arguments trên 20 case.
- Commit CP3: [0f88142 — tool CP3](https://github.com/Vietzanh/K5-L3B-DAY03-NhomABCD-ResearchAgentToolEval/commit/0f88142).
- Công cụ hỗ trợ: GitHub Copilot và pytest. Tự kiểm tra bằng unit test offline có HTTP mock, kiểm tra contract/registry và chạy eval; không đưa API key vào test hoặc báo cáo.

