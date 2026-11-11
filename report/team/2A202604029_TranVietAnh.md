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

...

## 4. Bằng chứng

- File/commit/PR:
  - starter_v0/data/eval_group.json: Bộ 10 test case.
  - Evaluation run v4: v4_B_group_openrouter_20261111T081004535910.
  - Evaluation run v6: v6_B_group_openrouter_20261111T091405140926.
  - Evaluation run v7: v7_B_group_openrouter_20261111T094308640312.
  - Báo cáo nhóm report/team/group_report.md mục (B3. Team Eval Cases)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Sử dụng ChatGPT để hỗ trợ rà soát độ bao phủ test case, kiểm tra expected tool/arguments và hoàn thiện cấu trúc JSON.
  - Tự đối chiếu expect và actual_tool_calls trong kết quả JSON, kiểm tra trạng thái pass/fail và phân tích nguyên nhân của case thất bại.
  - Kiểm tra riêng các kết quả thực thi tool để phân biệt lỗi routing/arguments với lỗi phát sinh trong quá trình truy xuất dữ liệu.

## 5. Tự đánh giá

- Điểm làm tốt: Hoàn thành đủ 10 test case theo yêu cầu, đảm bảo tỷ lệ 5 single-turn và 5 multi-turn. Bộ test có độ bao phủ tương đối đa dạng, bao gồm cả các tool mới của nhóm và những tình huống kiểm tra khả năng duy trì ngữ cảnh, cập nhật thông tin qua nhiều lượt.
- Kết quả đạt được: Group evaluation trên Prompt v7 đạt 100% case accuracy, 100% tool routing accuracy, 100% argument accuracy và 100% multi-turn accuracy. Cả 10 test cases đều PASS, trong đó các lỗi trước đây ở G02 và G05 đã được khắc phục.
- Quá trình cải thiện: Qua các lần thử nghiệm, kết quả case accuracy lần lượt là 90% ở v4, 80% ở v6 và 100% ở v7. Việc theo dõi từng case giúp xác định cụ thể những vấn đề về truyền arguments và lựa chọn policy area, thay vì chỉ dựa vào điểm accuracy tổng thể.
- Điểm cần cải thiện: Kết quả argument accuracy chưa đạt 100%, cụ thể ở việc truyền tường minh tham số search_type và lựa chọn đúng policy_area. Ngoài ra, kết quả pass ở tầng routing và arguments chưa phản ánh đầy đủ độ chính xác của dữ liệu do tool trả về. Ví dụ, G03 được đánh giá pass vì gọi đúng verify_reference, nhưng kết quả Crossref vẫn cần được đối chiếu thêm với tiêu đề và tác giả của tài liệu gốc.
- Hướng cải thiện: Tiếp tục làm rõ mô tả các tham số trong tools.yaml, đặc biệt là sự khác biệt giữa tool_usage và external_publishing. Bổ sung quy tắc ánh xạ intent sang arguments để agent truyền đầy đủ các giá trị được yêu cầu thay vì phụ thuộc vào default. Đồng thời, mở rộng đánh giá chất lượng kết quả trả về từ tool, bên cạnh việc chỉ đánh giá routing và arguments.
  ...
