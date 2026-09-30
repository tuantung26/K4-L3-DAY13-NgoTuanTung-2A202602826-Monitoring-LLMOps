# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1 — high_latency_p95 {#high-latency-p95}

- Tên: `high_latency_p95`
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#day13-oncall`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms` vs SLO 3000ms
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn SLO, trải nghiệm giảm với feature `qa`.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Latency** → xác nhận P95/P99 cao và thời điểm bắt đầu.
  2. Lọc `data/logs.jsonl` với `event == "response_sent" and latency_ms > 3000`, lấy một `correlation_id`.
  3. Mở trace cùng `correlation_id` trên Langfuse → so sánh span `retrieval` và `generation` tìm bước chậm.
- Mitigation tạm thời: nếu `retrieval` chậm → tắt incident `rag_slow`; nếu `generation` chậm → rollback prompt trên Langfuse.
- Owner: `student-2A202602826`

## Alert 2 — elevated_error_rate {#elevated-error-rate}

- Tên: `elevated_error_rate`
- Severity: critical
- Duration: 3m
- Kênh thông báo: Slack `#day13-oncall`
- SLI/SLO liên quan: error budget SLO `fast_successful_requests`; guardrail `error_rate_pct_max: 2`
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` liên tục trong 3 phút
- Ảnh hưởng tới người dùng: người dùng nhận HTTP 500, không nhận câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Errors** → xác nhận `error_rate_pct` và loại lỗi phổ biến nhất.
  2. Lọc `data/logs.jsonl` với `event == "request_failed"`, lấy `correlation_id` và `error_type`.
  3. Mở trace cùng `correlation_id` trên Langfuse → xem span nào có status ERROR.
- Mitigation tạm thời: nếu lỗi từ retrieval → tắt incident `tool_fail`; nếu từ LLM → rollback prompt.
- Owner: `student-2A202602826`

## Alert 3 — low_retrieval_success {#low-retrieval-success}

- Tên: `low_retrieval_success`
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#day13-oncall`
- SLI/SLO liên quan: guardrail `retrieval_success_rate_pct_min: 90`
- Điều kiện và thời gian duy trì: `tool_success_rate_pct < 90%` liên tục trong 5 phút
- Ảnh hưởng tới người dùng: RAG không tìm được context → câu trả lời chất lượng thấp, `quality_score` giảm.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Errors** → xác nhận `tool_success_rate_pct` thấp.
  2. Lọc `data/logs.jsonl` với `tool_name == "retrieval" and tool_success == false`, lấy `correlation_id`.
  3. Mở trace cùng `correlation_id` trên Langfuse → xem span `retrieval` có input bất thường không.
- Mitigation tạm thời: tắt incident `rag_slow` nếu đang bật; kiểm tra query trong span có chứa ký tự lạ.
- Owner: `student-2A202602826`

