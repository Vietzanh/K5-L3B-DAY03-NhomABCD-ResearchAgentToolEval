# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: NhomABCD
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v5: `openai` (`gpt-4o-mini`)

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

Tất cả run dưới đây: provider `openai`, model `gpt-4o-mini`, suite `base` (20 case), `provider_error_cases = 0`, `measured_cases = 20`. Metric = `case_accuracy` (chi tiết routing / args / multiturn trong ngoặc). Hash là 12 ký tự đầu của `prompt_hash` / `tools_hash`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (prompt `eb1c8179815b`, tools `e69bc53ed884`) | Đo hành vi của starter chưa sửa. | — | 0.70 (routing 0.75, args 0.70, multiturn 1.00) | `starter_v0/runs/v0_B_base_openai_20261110T181658629110.json` |
| v1 | `system_prompt.md` (`e8f49e2218e7`) | Prompt starter bảo agent đoán thay vì hỏi, gửi không cần xác nhận và ép làm một bước, nên agent bịa handle/URL, gọi `send` cho cả câu ngoài phạm vi. Bỏ 3 chỉ dẫn xấu và thêm ranh giới (ngoài phạm vi thì từ chối, thiếu handle/URL thì `clarify`, gửi thì xác nhận trước, cho phép nhiều tool call) sẽ sửa R08, R10, R11, R12, R14. | 0.70 | 0.90 (1.00 / 0.90 / 1.00) | `starter_v0/runs/v1_B_base_openai_20261110T190322024377.json` |
| v2 | `tools.yaml` (`fa61162d23a2`): `clarify`, `send` | Mô tả `clarify`/`send` không nêu convention `response_type` và ranh giới xác nhận, nên model bỏ trống `response_type` (R11) hoặc hỏi nội dung bằng `text` thay vì `yes_no` (R12). | 0.90 | 0.90 (0.95 / 0.90 / 1.00) | `starter_v0/runs/v2_B_base_openai_20261110T191022732055.json` |
| v3 | `tools.yaml` (`5cc50d42da03`): thêm tool mới `verify_reference` | Thêm tool mới không làm giảm routing/args của các case base (base không có case nào cần tool này). | 0.90 | 0.95 (1.00 / 0.95 / 1.00) | `starter_v0/runs/v3_B_base_openai_20261110T193829691099.json` |
| v4 | `system_prompt.md` (`b0b1cc1000eb`) + `tools.yaml` (`c8745f713dff`): rule gửi, `timeline` | (1) Rule gửi của v1 bắt "trình bày nội dung sẽ gửi", nên khi chưa có nội dung, model hỏi nội dung bằng `text` (R12). (2) Mô tả `timeline.screenname` quá sơ sài nên model điền tên nền tảng "Twitter" (R10). *Version này gộp 2 giả thuyết.* | 0.95 | 0.90 (1.00 / 0.90 / 1.00) | `starter_v0/runs/v4_B_base_openai_20261110T194933137985.json` |
| v5 | `tools.yaml` (`a671973ddd4c`): `lookup` | Mô tả `lookup` không nêu convention query/topic/timeframe, nên model nhét "news" vào `query` và bỏ `topic="news"` (R03, R13). | 0.90 | **1.00** (1.00 / 1.00 / 1.00) | `starter_v0/runs/v5_B_base_openai_20261111T085803114637.json` |

Nhận xét:

- **v1 có tác động lớn nhất** (+0.20): 5/6 lỗi của v0 đến thẳng từ các chỉ dẫn xấu cố ý trong prompt starter.
- **Model dao động giữa các lần chạy.** R10 PASS ở v1, FAIL ở v2, PASS ở v3, dù v1→v3 không có thay đổi nào đụng `timeline`. R03/R13 PASS ở v1–v3 nhưng FAIL ở v4 khi mô tả `lookup` không đổi. Vì vậy bước 0.90 → 0.95 ở v3 **không phải nhờ tool mới**, mà do R10 tình cờ PASS. Bước 0.95 → 0.90 ở v4 cũng không phải do v4 làm hỏng `lookup`.
- **Bài học:** chỗ nào tool declaration còn mơ hồ (`timeline.screenname`, `lookup.query/topic`), kết quả sẽ không ổn định. Chỉ khi viết rõ convention vào mô tả tham số (v4, v5) thì các case đó mới PASS đều. Một lần 20/20 chưa đủ để kết luận ổn định; cần chạy lại cùng version để xác nhận.
- **Về phương pháp:** v1, v2, v3, v5 mỗi version đúng một giả thuyết. v4 gộp hai thay đổi (prompt + `timeline`), nên không tách riêng được tác động của từng thay đổi trong run v4.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON. Bảng gồm 6 case FAIL của baseline v0 và các case FAIL xuất hiện ở các version sau.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope (v0) | `out_of_scope` | `send(text="Nguyên hàm của x^2 là x^3/3 + C ...")` | Câu toán ngoài phạm vi; expected no tool + từ chối. Agent dùng `send` để trả lời. | v1: thêm mục Scope, ngoài research thì từ chối bằng text, không gọi tool; cấm dùng `send` để trả lời. PASS từ v1. |
| R14_out_of_scope_coding (v0) | `out_of_scope` | `send(text="Dưới đây là một hàm Python tính số Fibonacci ...")` | Yêu cầu viết code ngoài phạm vi; agent viết code rồi gọi `send`. | v1 (cùng fix với R08). PASS từ v1. |
| R10_missing_handle (v0) | `missing_info` | `timeline(screenname="sama")` | Không nói tài khoản nào; expected `clarify(text)`. Prompt starter bảo "chọn tài khoản nổi tiếng như Sam Altman". | v1: bỏ chỉ dẫn đoán, thêm rule "thiếu tài khoản thì `clarify`". PASS ở v1. |
| R11_missing_url (v0) | `missing_info` | `fetch(url="https://example.com/article")` | "Bài viết này" không có URL; agent bịa URL theo chỉ dẫn "assume a likely URL". | v1: thiếu URL thì `clarify(text)`. Agent chuyển sang `clarify` nhưng vẫn FAIL arg (dòng R11 v1 bên dưới). |
| R12_confirm_before_send (v0) | `wrong_boundary` | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gửi ngay không xin xác nhận, theo chỉ dẫn "just go ahead and do it". | v1: bỏ chỉ dẫn, thêm "phải xác nhận trước khi gửi". Agent chuyển sang `clarify` nhưng sai `response_type` (dòng R12 v1–v3 bên dưới). |
| R13_parallel_web_and_tweets (v0) | `wrong_tool` | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI", search_type="Latest")` | `lookup` thừa chữ "news" trong `query` và thiếu `topic="news"`. | PASS ở v1–v3 (dao động), FAIL lại ở v4; sửa gốc ở v5 (xem dòng R13 v4). |
| R11_missing_url (v1) | `missing_info` | `clarify(question="Bạn vui lòng cung cấp URL ...")`, không có `response_type` | Đúng tool nhưng thiếu `response_type="text"`, vì tham số này không bắt buộc và mô tả chỉ ghi "Kiểu trả lời". | v2: `response_type` thành `required`, mô tả rõ `text` / `yes_no` / `choice`. PASS từ v2. |
| R12_confirm_before_send (v1–v3) | `wrong_boundary` | `clarify(question="Bạn có thể cung cấp nội dung cụ thể mà bạn muốn đăng ...", response_type="text")` | Hỏi nội dung bằng `text` thay vì xin xác nhận bằng `yes_no`. Sửa mô tả tool ở v2 không đủ, vì prompt v1 vẫn ghi "showing what will be sent", mà câu hỏi không có nội dung để trình bày. | v4: sửa rule trong prompt, yêu cầu gửi chưa xác nhận thì bước đầu **luôn** là `clarify(yes_no)`, kể cả khi nội dung mơ hồ. PASS từ v4. |
| R10_missing_handle (v2) | `missing_info` | `timeline(screenname="Twitter")` | Hồi quy dù v2 không đụng `timeline`: model điền tên nền tảng vào `screenname`, vì mô tả chỉ ghi "Tên tài khoản". Rule trong prompt không đủ mạnh lúc model điền args. | v4: mô tả `timeline` chỉ dùng cho tài khoản user nêu rõ; `screenname` không có `@`, không bao giờ là tên nền tảng, không đoán; thiếu thì `clarify`. PASS từ v4. |
| R03_web_news_routing (v4) | `wrong_tool` | `lookup(query="AI news", topic="news", timeframe="day")` | Đúng tool và `topic`, nhưng `query` thừa "news" (expected `query="AI"`). | v5: mô tả `lookup` ghi query chỉ gồm chủ đề, không thêm "news"/"today"; tin tức thì `topic="news"`; hôm nay = `day`, tuần này = `week`. PASS ở v5. |
| R13_parallel_web_and_tweets (v4) | `wrong_tool` | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | Giống v0: `query` thừa "news" và thiếu `topic="news"`. | v5 (cùng fix với R03). PASS ở v5. |

Phân loại theo nơi sửa:

- **Lỗi do prompt** (`system_prompt.md`): R08, R14 (phạm vi), R10, R11 (đoán thay vì hỏi), R12 (ranh giới gửi). Đều do chỉ dẫn xấu cố ý của starter hoặc rule chưa đủ chặt.
- **Lỗi do tool declaration** (`tools.yaml`): R11 (`response_type`), R10 (`screenname`), R03, R13 (`lookup` query/topic). Đều do mô tả tham số quá sơ sài, nên model tự điền theo đoán.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_timeline_handle_normalization | Chuẩn hóa Twitter/X handle bằng cách loại bỏ ký tự @ và trích xuất đúng số lượng bài đăng. | timeline(screenname="karpathy", limit=7) | PASS – Gọi đúng tool, truyền đúng handle và limit. |
| G02_social_search_latest_limit | Tìm bài đăng theo chủ đề, phân biệt với truy vấn theo tài khoản; lựa chọn Latest và trích đúng số lượng. | social_search(query="AI agent evaluation", search_type="Latest", limit=6) | FAIL – Gọi đúng tool, query và limit nhưng thiếu search_type="Latest" trong arguments. Tool sử dụng giá trị mặc định Latest khi thực thi. |
| G03_verify_reference_crossref | Xác minh tài liệu học thuật bằng tiêu đề trong metadata Crossref, không nhầm với tìm kiếm hoặc đọc paper. | verify_reference(reference="Attention Is All You Need") | PASS – Gọi đúng tool mới verify_reference và truyền đúng reference. |
| G04_format_explicit_items_as_bullets | Nhận diện dữ liệu đã được cung cấp sẵn và sử dụng tool format thay vì tìm kiếm thêm thông tin. | format(items=[...], template="bullets", headline="AI Research") | PASS – Gọi đúng tool, truyền chính xác dữ liệu và template. |
| G05_policy_tool_usage | Tra cứu quy định nội bộ về sử dụng tool bên ngoài, phân biệt policy search với web search. | policy(query=..., policy_area="tool_usage") | FAIL – Gọi đúng tool policy nhưng chọn sai policy_area="external_publishing"; expected là tool_usage. Tool trả về danh sách rỗng. |
| G06_multiturn_social_search_update_filters | Kế thừa chủ đề từ các lượt trước, cập nhật loại sắp xếp từ Top sang Latest và thay đổi số lượng kết quả. | social_search(query="OpenAI", search_type="Latest", limit=4) | PASS – Giữ đúng query, cập nhật chính xác search_type và limit. |
| G07_multiturn_lookup_keep_general_scope | Thu hẹp chủ đề tìm kiếm qua nhiều lượt nhưng vẫn giữ phạm vi general, không tự chuyển sang news. | lookup(query="ứng dụng quantum computing trong y tế", topic="general") | PASS – Giữ đúng topic và cập nhật query theo yêu cầu mới nhất. |
| G08_multiturn_papers_sort_and_limit | Kế thừa chủ đề tìm kiếm paper, cập nhật số lượng và lựa chọn sắp xếp theo ngày cập nhật gần nhất. | papers(query="multimodal RAG", max_results=3, sort_by="lastUpdatedDate") | PASS – Gọi đúng tool mới papers, truyền đầy đủ arguments và trả về 3 kết quả. |
| G09_multiturn_cancel_telegram_send | Xử lý yêu cầu hủy hành động publish, không tiếp tục gửi Telegram sau khi người dùng rút lại yêu cầu. | Không gọi tool (no_tool=true); phản hồi xác nhận đã hủy. | PASS – Không gọi tool, phản hồi xác nhận yêu cầu đã được hủy. |
| G10_multiturn_paper_text_update_pages | Kế thừa arXiv ID và cập nhật số trang cần trích xuất từ 5 xuống 3 qua nhiều lượt. | paper_text(arxiv_url="2401.12345", max_pages=3) | PASS – Giữ đúng arXiv ID, cập nhật số trang và trích xuất đúng 3 trang. |

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
