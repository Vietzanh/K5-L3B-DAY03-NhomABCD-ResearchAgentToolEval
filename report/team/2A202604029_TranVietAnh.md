# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trần Việt Anh
- MSSV: 2A202604029
- Email: 26ai.anhtv2@vinuni.edu.vn

## 2. Phần việc phụ trách

CP4 — Eval nhóm 10 case

- Xây dựng bộ 10 test case bổ sung cho bộ evaluation có sẵn, gồm 5 single-turn (query) và 5 multi-turn (turns).
- Thiết kế các tình huống kiểm tra khả năng routing tool, trích xuất arguments, xử lý ngữ cảnh nhiều lượt và kiểm soát hành động bên ngoài.
- Bổ sung các test case nhằm đánh giá khả năng sử dụng những tool mới do nhóm phát triển.
- Chạy evaluation trên prompt v4, phân tích kết quả và xác định các điểm cần cải thiện.
  ...

## 3. Đóng góp cụ thể

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

...

## 4. Bằng chứng

- File/commit/PR:
  - starter_v0/data/eval_group.json: Bộ 10 test case nhóm.
  - Evaluation run v5: v5_B_group_openrouter_20261111T091405140926.
  - Báo cáo nhóm report/team/group_report.md mục (B3. Team Eval Cases)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng ChatGPT để hỗ trợ rà soát độ bao phủ test case, kiểm tra expected tool/arguments và hoàn thiện cấu trúc JSON.
  - Tự đối chiếu expect và actual_tool_calls trong kết quả JSON, kiểm tra trạng thái pass/fail và phân tích nguyên nhân của case thất bại.
  - Kiểm tra riêng các kết quả thực thi tool để phân biệt lỗi routing/arguments với lỗi phát sinh trong quá trình truy xuất dữ liệu.

## 5. Tự đánh giá

- Điểm làm tốt: Hoàn thành đủ 10 test case theo yêu cầu, đảm bảo tỷ lệ 5 single-turn và 5 multi-turn. Bộ test có độ bao phủ tương đối đa dạng, bao gồm cả các tool mới của nhóm và những tình huống kiểm tra khả năng duy trì ngữ cảnh, cập nhật thông tin qua nhiều lượt.
- Kết quả đạt được: Group evaluation trên Prompt v5 đạt 80% case accuracy và 100% multi-turn accuracy. Agent định tuyến đúng tool trong cả 10 trường hợp, cho thấy khả năng lựa chọn công cụ và xử lý hội thoại nhiều lượt tương đối ổn định.
- Điểm cần cải thiện: Kết quả argument accuracy chưa đạt 100%, cụ thể ở việc truyền tường minh tham số search_type và lựa chọn đúng policy_area. Ngoài ra, kết quả pass ở tầng routing và arguments chưa phản ánh đầy đủ độ chính xác của dữ liệu do tool trả về. Ví dụ, G03 được đánh giá pass vì gọi đúng verify_reference, nhưng kết quả Crossref vẫn cần được đối chiếu thêm với tiêu đề và tác giả của tài liệu gốc.
- Hướng cải thiện: Tiếp tục làm rõ mô tả các tham số trong tools.yaml, đặc biệt là sự khác biệt giữa tool_usage và external_publishing. Bổ sung quy tắc ánh xạ intent sang arguments để agent truyền đầy đủ các giá trị được yêu cầu thay vì phụ thuộc vào default. Đồng thời, mở rộng đánh giá chất lượng kết quả trả về từ tool, bên cạnh việc chỉ đánh giá routing và arguments.
  ...
