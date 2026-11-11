# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: NhomABCD
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `openai` (`gpt-4o-mini`)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent hỗ trợ tìm kiếm thông tin thời sự/web (`lookup`), theo dõi bài đăng theo tài khoản hoặc chủ đề trên X/Twitter (`timeline`, `social_search`), đọc nội dung URL (`fetch`), tìm và đọc paper arXiv (`papers`, `paper_text`), kiểm tra DOI/tiêu đề tài liệu học thuật qua metadata Crossref (`verify_reference`), tra tài liệu nội bộ (`policy`), tổng hợp thành digest (`format`), biết hỏi lại khi thiếu thông tin (`clarify`) và chỉ gửi Telegram (`send`) sau khi người dùng xác nhận rõ ràng.

**Cách chạy UI:**

Chạy từ thư mục `starter_v0/` (đã bổ sung `streamlit>=1.50.0` vào `starter_v0/requirements.txt`):

```powershell
cd starter_v0
pip install -r requirements.txt
streamlit run app.py
```

**Link dùng thử (deploy):**

Mở Cloudflare Tunnel trỏ vào cổng Streamlit (`cloudflared tunnel --url http://localhost:8501`):

> URL: *(dán link `https://*.trycloudflare.com` khi bật `cloudflared tunnel --url http://localhost:8501` lúc showdown/chấm bài)*

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận hành động (`text` / `yes_no` / `choice`) | không |
| `timeline` | Lấy các bài đăng gần đây trên X/Twitter của một tài khoản (`screenname`) | không |
| `social_search` | Tìm bài đăng trên X/Twitter theo từ khóa (`Latest` / `Top`) | không |
| `lookup` | Tìm kiếm thông tin/tin tức trên web (`topic`: `general`/`news`, `timeframe`) | không |
| `fetch` | Đọc nội dung văn bản/markdown từ một URL cụ thể | không |
| `format` | Trình bày danh sách kết quả đã thu thập thành digest markdown (`brief`, `sections`, `bullets`, `thread`, `daily_ai_vn`) | không |
| `send` | Gửi thông điệp lên Telegram channel (chỉ gửi khi `confirmed=true`) | không |
| `policy` | Tìm kiếm trong tài liệu chính sách nội bộ (`company_policy/*.md`) | không |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv | không |
| `paper_text` | Tải PDF bài báo arXiv và trích xuất văn bản | không |
| `verify_reference` | Kiểm tra DOI hoặc tiêu đề tài liệu học thuật trên Crossref để xác minh bản ghi và lấy metadata trích dẫn | **có** |

### A3. Câu hỏi mẫu để thử

1. **Tìm tin tổng hợp:** `"Tin tức AI hôm nay có gì nổi bật?"`
2. **Tra cứu tài khoản X:** `"Lấy 5 tweet mới nhất của Elon Musk"`
3. **Kiểm tra hỏi lại (`clarify`) khi thiếu thông tin:** `"Tóm tắt 5 tweet mới nhất giúp mình"` *(sau đó bổ sung tên/handle ở lượt 2)*
4. **Kiểm tra guardrail xác nhận trước khi gửi (`send`):** `"Đăng bản tin này lên Telegram giúp mình"`
5. **Kiểm tra tool mới của nhóm (`verify_reference`):** `"Kiểm tra DOI 10.1038/s41586-021-03819-2 trên Crossref giúp mình"`

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_timeline_handle_normalization | Chuẩn hóa Twitter/X handle bằng cách loại bỏ ký tự @ và trích xuất đúng số lượng bài đăng. | timeline(screenname="karpathy", limit=7) | (PASS) Gọi đúng tool, truyền đúng handle và limit. |
| G02_social_search_latest_limit | Tìm bài đăng theo chủ đề, phân biệt với truy vấn theo tài khoản; lựa chọn Latest và trích đúng số lượng. | social_search(query="AI agent evaluation", search_type="Latest", limit=6) | (FAIL) Gọi đúng tool, query và limit nhưng thiếu tham số search_type="Latest" trong tool call. |
| G03_verify_reference_crossref | Xác minh tài liệu học thuật bằng tiêu đề trong metadata Crossref, không nhầm với tìm kiếm hoặc đọc paper. | verify_reference(reference="Attention Is All You Need") | (PASS) Route đúng tool mới verify_reference và truyền đúng reference. |
| G04_format_explicit_items_as_bullets | Nhận diện dữ liệu đã được cung cấp sẵn và sử dụng tool format thay vì tìm kiếm thêm thông tin. | format(items=[...], template="bullets", headline="AI Research") | (PASS) Gọi đúng tool, truyền chính xác dữ liệu và template. |
| G05_policy_tool_usage | Tra cứu quy định nội bộ về sử dụng tool bên ngoài, phân biệt policy search với web search. | policy(query=..., policy_area="tool_usage") | (PASS) Gọi đúng tool mới policy, chọn đúng policy area và truy xuất được tài liệu liên quan. |
| G06_multiturn_social_search_update_filters | Kế thừa chủ đề từ các lượt trước, cập nhật loại sắp xếp từ Top sang Latest và thay đổi số lượng kết quả. | social_search(query="OpenAI", search_type="Latest", limit=4) | (PASS) Giữ đúng query, cập nhật chính xác search_type và limit. |
| G07_multiturn_lookup_keep_general_scope | Thu hẹp chủ đề tìm kiếm qua nhiều lượt nhưng vẫn giữ phạm vi general, không tự chuyển sang news. | lookup(query="ứng dụng quantum computing trong y tế", topic="general") | (PASS) Giữ đúng topic và cập nhật query theo yêu cầu mới nhất. |
| G08_multiturn_papers_sort_and_limit | Kế thừa chủ đề tìm kiếm paper, cập nhật số lượng và lựa chọn sắp xếp theo ngày cập nhật gần nhất. | papers(query="multimodal RAG", max_results=3, sort_by="lastUpdatedDate") | (PASS) Gọi đúng tool mới papers, truyền đủ arguments và trả về 3 kết quả. |
| G09_multiturn_cancel_telegram_send | Xử lý yêu cầu hủy hành động publish, không tiếp tục gửi Telegram sau khi người dùng rút lại yêu cầu. | Không gọi tool (no_tool=true); phản hồi xác nhận đã hủy. | (PASS) Không gọi send, xác nhận yêu cầu đã được hủy. |
| G10_multiturn_paper_text_update_pages | Kế thừa arXiv ID và cập nhật số trang cần trích xuất từ 5 xuống 3 qua nhiều lượt. | paper_text(arxiv_url="2401.12345", max_pages=3) | (PASS) Giữ đúng arXiv ID, cập nhật số trang và trích xuất đúng 3 trang. |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `starter_v0/requirements.txt` (lệnh: `streamlit run app.py`; link tunnel cập nhật khi mở `cloudflared` lúc demo) | Đọc động `system_prompt.md` + `tools.yaml` (hiển thị đủ 11 tools gồm `verify_reference`), hỗ trợ đổi qua lại các snapshot Git `v0`–`v4`, đa lượt `run_model_tool_loop`, nút quick-reply `clarify` (`yes_no`/`choice`), tự lưu & tải transcript JSON; `AppTest` + `pytest` (`72 passed, 14 skipped`) đều xanh | Hiển thị trung thực lỗi tool/provider (`st.error` + tự mở expander); không dùng `unsafe_allow_html` với nội dung web; tách `untrusted_text` của `policy`; bảo vệ `send` bằng `needs_confirmation`; không commit `.env` |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

- **Lỗi provider Gemini (model mặc định treo, phiên bản API `v1` vs `v1beta`, và giới hạn 5 RPM):**
  - *Hiện tượng & Bằng chứng:* Khi kiểm tra bằng `scripts/preflight_provider.py --provider gemini`, model mặc định `gemini-3.8-flash` bị treo; khi chuyển sang `--model gemini-2.5-flash`, SDK `google-genai` mặc định gọi API `v1` nên báo lỗi `400 INVALID_ARGUMENT` vì `function_calling` yêu cầu `v1beta`. Sau khi thêm `GOOGLE_GENAI_API_VERSION=v1beta`, chạy 20 case `eval_base.json` vẫn bị lỗi `429 RESOURCE_EXHAUSTED` (free tier giới hạn 5 requests/phút) dẫn tới `provider_error_cases: 9`, `measured_cases: 11/20` (bằng chứng: `starter_v0/runs/v0_B_base_gemini_20261110T181044880645.json`).
  - *Cách xử lý:* Không dùng run Gemini bị lỗi làm baseline theo đúng quy tắc hợp lệ; nhóm chuyển sang dùng OpenAI (`gpt-4o-mini`) để đạt `provider_error_cases: 0` (`20/20` measured). Đồng thời trong giao diện `starter_v0/app.py`, mặc định ưu tiên provider đã cấu hình key ổn định (`openai`) và gợi ý sẵn `gemini-2.5-flash` nếu chuyển sang Gemini.
- *(Bổ sung thêm các khó khăn của thành viên khác nếu có sau khi ghép Phần B.)*

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
