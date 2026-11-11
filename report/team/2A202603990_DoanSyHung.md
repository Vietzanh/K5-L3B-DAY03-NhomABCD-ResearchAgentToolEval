# Báo cáo cá nhân — Đoàn Sỹ Hưng (2A202603990)

## 1. Thông tin thành viên

- Họ tên: Đoàn Sỹ Hưng
- MSSV: 2A202603990
- Email: hungizumi1210@gmail.com
- GitHub: [hgmdz1210](https://github.com/hgmdz1210)

## 2. Phần việc phụ trách

Vai 1 — Prompt & Eval lead (C1, C2, C3):

- Sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`.
- Chạy base eval qua các version v0 → v7 bằng `openai` / `gpt-4o-mini`, và ghi `starter_v0/artifacts/version_log.csv`.
- Viết bảng B1 (Version Evidence), B2 (Failure Analysis), mục 3 (Giải pháp) và B6 (Reflection) trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

| Version | Thay đổi | Base | Kết quả chính |
|---|---|---:|---|
| v0 | baseline, starter chưa sửa | 0.70 | 6 case FAIL, mỗi case đã gán loại lỗi (`out_of_scope`, `missing_info`, `wrong_boundary`, `wrong_tool`) |
| v1 | `system_prompt.md`: bỏ 3 chỉ dẫn xấu, thêm phạm vi, "hỏi thay vì đoán", xác nhận trước khi gửi | 0.90 | Sửa R08, R10, R12 (đúng tool), R14 |
| v2 | `tools.yaml`: `clarify` (`response_type` bắt buộc), `send` (ranh giới xác nhận) | 0.90 | Sửa R11 |
| v3 | `tools.yaml`: merge tool mới `verify_reference` của Long | 0.95 | Tool mới không làm hỏng case cũ. Mức tăng là do dao động của R10, đã ghi rõ trong log |
| v4 | prompt: rule gửi luôn `clarify(yes_no)` trước; tools: `timeline.screenname` | 0.90 | Sửa R12, R10; R03/R13 dao động |
| v5 | `tools.yaml`: mô tả `lookup` (Long viết) | 1.00 | 20/20 |
| v6 | prompt: mục Routing; tools: viết lại 6 mô tả còn sơ sài | 1.00 | Đạt tiêu chí C2; group eval vẫn 0.90 (G02) |
| v7 | `tools.yaml`: `social_search.search_type` thành bắt buộc | 0.95 | Group eval 0.90 → **1.00**. M06 ở base dao động; 2 lần chạy lại đều 20/20 |

Ngoài các version:

- **Giữ hash đúng cho từng version.** Phát hiện `core.autocrlf=true` trên Windows làm git và `sed` đổi xuống dòng (LF/CRLF). Khi đó `prompt_hash` / `tools_hash` thay đổi dù nội dung không đổi, khiến một version trông như đã sửa thêm artifact khác. Trước mỗi run, mình kiểm tra hash để mỗi version chỉ khác đúng artifact đã ghi trong log. Hash của v6 và v7 trong commit khớp byte-by-byte với hash trong run JSON.
- **Đo eval nhóm trên cùng model.** Run group của nhóm ban đầu dùng OpenRouter. Mình chạy lại `eval_group.json` bằng `openai/gpt-4o-mini` cho v5, v6, v7, để giả thuyết G02 được đo trên cùng model với base. Run v5 dùng đúng prompt/tools của commit v5 (qua `--system-prompt` / `--tools`), không sửa file trong repo.
- **Phối hợp merge.** Merge tool `verify_reference` của Long vào `main` (fast-forward). Lấy riêng phần mô tả `lookup` từ nhánh của Long cho v5. Không lấy phần rule gửi của Long vì xung đột với v4 và R12 đã PASS.

## 4. Bằng chứng

- **Run JSON (base)**:
  - `starter_v0/runs/v0_B_base_openai_20261110T181658629110.json`
  - `starter_v0/runs/v1_B_base_openai_20261110T190322024377.json`
  - `starter_v0/runs/v2_B_base_openai_20261110T191022732055.json`
  - `starter_v0/runs/v3_B_base_openai_20261110T193829691099.json`
  - `starter_v0/runs/v4_B_base_openai_20261110T194933137985.json`
  - `starter_v0/runs/v5_B_base_openai_20261111T085803114637.json`
  - `starter_v0/runs/v6_B_base_openai_20261111T092030353316.json`
  - `starter_v0/runs/v7_B_base_openai_20261111T092529002036.json`

  Tất cả có `provider_error_cases = 0` và `measured_cases = total_cases`.
- **Run JSON (group, OpenAI)**:
  - `starter_v0/runs/v5_B_group_openai_20261111T092139732111.json`
  - `starter_v0/runs/v6_B_group_openai_20261111T092303331306.json`
  - `starter_v0/runs/v7_B_group_openai_20261111T092704075080.json`
- **Version log**: `starter_v0/artifacts/version_log.csv` (v0–v7, có hash, giả thuyết, metric trước/sau).
- **Commit**: `62d409a` (v0), `1d1be28` (v1), `a8b1d00` (v2), `a9c8cda` (v3), `1ec845d` (v4), `d1fa954` (v5), `fabe401` (v6), `5688df0` (v7), `cf93ba3` (B1/B2).
- **Test**: `pytest` 72 passed, 14 skipped, 0 failed. `tests/test_tool_contract.py` xanh sau mỗi lần sửa `tools.yaml`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả**: dùng Claude Code để đọc run JSON, đề xuất giả thuyết, soạn câu chữ cho prompt/tool declaration, và nháp bảng báo cáo. Cách tự kiểm tra:
  - Mọi số liệu trong log và báo cáo đều lấy từ run JSON thật, không lấy từ dự đoán.
  - Chạy `pytest` sau mỗi lần sửa `tools.yaml`.
  - Đối chiếu hash trong run với file đang commit.
  - Quét key API thật trong các file trước mỗi lần push.
  - Khi kết quả không như dự đoán (v2 không sửa được R12; v3 tăng điểm nhưng không nhờ tool mới; v7 có M06 fail), ghi đúng kết quả thay vì sửa lại cho đẹp.

## 5. Tự đánh giá

- **Làm tốt**: vòng lặp giả thuyết → sửa → đo có bằng chứng đầy đủ cho từng version. Kết quả cuối đạt base 1.00 ở v5/v6 và group 1.00 ở v7. Tách được rõ lỗi do prompt (hành vi) và lỗi do tool declaration (convention tham số). Ghi trung thực các lần dao động thay vì nhận công cho chúng.
- **Chưa tốt**: v4 và v6 gộp hai thay đổi trong một version, nên không tách riêng được tác động của từng thay đổi. Mỗi version chỉ có một run chính thức, nên kết luận về độ ổn định còn yếu: các lần chạy lại kiểm tra không được giữ trong `runs/`.
- **Bài học**: với `gpt-4o-mini`, chỗ nào mô tả tham số còn mơ hồ thì kết quả dao động giữa các lần chạy. Rule chung trong prompt không thay được convention viết ngay trong mô tả tham số. Và tham số có giá trị default thì phải đặt `required` mới chắc model truyền rõ.
