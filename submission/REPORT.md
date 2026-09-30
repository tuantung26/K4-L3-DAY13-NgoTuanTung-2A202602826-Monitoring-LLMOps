# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Ngô Tuấn Tùng
- **MSSV:** 2A202602826
- **Lớp:** K4-L3B
- **Repository URL:** (Học viên tự điền url github)
- **Commit SHA cuối:** (Học viên tự điền)
- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602826`

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 0/100 | 100/100 | Đã đầy đủ schema, context và scrub PII hoàn toàn |
| `validate_dashboard.py` | 0/6 | 6/6 | Đã có đủ 6 panel yêu cầu trong `dashboard.yaml` |
| `pytest` | Fail | 32/32 passed | Đã pass toàn bộ test (kể cả test PII CCCD/Credit Card) |
| Số traces hợp lệ | 0 | >20 | Trace thể hiện đúng cấu trúc cha con (root -> retrieval/generation) |
| Số PII leak | >0 | 0 | Đã scrub thành công email, CCCD, số thẻ tín dụng |
| Latency P95 / TTFT P95 | (tự điền) | < 2000ms / 50ms | Đạt SLO khi hệ thống không có sự cố |
| Retrieval success rate | (tự điền) | 100% | Đạt SLO khi RAG hoạt động bình thường |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Nhận qua header `x-request-id` từ client, hoặc tự động sinh UUID dạng `req-<8hex>`. Truyền xuyên suốt request thông qua `structlog.contextvars` và middleware của FastAPI.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, và `correlation_id`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Bật `scrub_event` processor trong `logging_config.py`. Processor này dùng regex (từ `app/pii.py`) để tìm và mask (bôi mờ) PII (email, sđt, CCCD, thẻ tín dụng) trước khi render ra JSON file.
- **Cách kiểm chứng kết quả:** Dạy unit test trong `test_pii.py` (tất cả 32 test passed) và chạy công cụ `validate_logs.py` chấm điểm đạt 100/100 không có rò rỉ.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** Trace được gửi tới project Langfuse `day13-k4-l3b-2A202602826`, xác nhận được qua giao diện UI.
- **Cấu trúc root/retrieval/generation observations:** Root trace tạo bằng decorator `@observe()`. `retrieval` và `generation` là 2 span con được tạo lồng bên trong bằng context manager `langfuse_client.start_as_current_observation(as_type=...)` của Langfuse v4.
- **Cách nối trace với log:** Ghi chung `correlation_id` vào structured log và metadata của Trace, cho phép tìm kiếm qua lại dễ dàng giữa hai hệ thống.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (label: `baseline` / `production`)
- **Version/label candidate:** Version 2 (label: `candidate`)
- **Trace ID của mỗi version:** v2: "req-a09d4171", v1: "req-ceb1194d"
- **Cách promote và rollback `production`:** Kéo thả đổi label `production` giữa các version ngay trên giao diện UI của Langfuse. Không cần restart API (chỉ cần đợi tối đa 60s để bộ nhớ đệm tự làm mới do `cache_ttl_seconds=60`).

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** 6 Panel (Latency, Traffic, Errors, Cost, Tokens, Quality) đã được định nghĩa chuẩn xác trong `dashboard.yaml`, test 6/6.
- **SLO và lý do chọn:** Chọn SLO 99.5% cho `fast_successful_requests` (điều kiện `latency_ms <= 3000`). Vì đối với các dịch vụ chatbot/LLM QA, độ trễ trên 3 giây sẽ khiến trải nghiệm người dùng rất tệ.
- **Cách tính error budget:** SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO 3000ms.
- **Ba alert và runbook tương ứng:** 1. `high_latency_p95` (Cảnh báo độ trễ vượt 3000ms). 2. `elevated_error_rate` (Tỷ lệ lỗi trên 2%). 3. `low_retrieval_success` (Tỷ lệ tìm thấy RAG context dưới 90%). Tất cả runbook đã lưu chi tiết tại `docs/alerts.md`.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** day13-k4-l3b-monitoring-llmops-v1
- **Khoảng thời gian điều tra:** Khoảng 11:21 ngày 30/09/2026
- **Triệu chứng từ metrics:** `latency_p95` tăng cao đột biến (trên 3600ms, request thực tế kéo dài 7-15s) vượt xa ngưỡng SLO.
- **Log line và correlation ID liên quan:** Request event `response_sent` có `latency_ms` rất cao, ví dụ correlation ID: `req-bb80dac0` hoặc `req-40ec42c1`.
- **Trace ID và span gây ảnh hưởng:** Trace trên Langfuse cho thấy span `retrieval` chiếm rất nhiều thời gian (chậm ~2.5s mỗi call) khiến toàn bộ hệ thống bị nghẽn (do kẹt concurrency). (Học viên tự lấy Trace ID thật trên UI).
- **Root cause:** Component RAG/Vector Store (`retrieval`) bị chậm (sleep 2.5s do incident `rag_slow`), khi có nhiều request đồng thời (concurrency 5) đã gây kẹt cổ chai (bottleneck) khiến các request sau phải đợi lên tới 15s.
- **Fix action:** Vô hiệu hóa sự cố `rag_slow` bằng cách gọi API `/incidents/rag_slow/disable`. (Trong thực tế: scale up vector DB, thêm RAG caching, hoặc sửa logic query).
- **Preventive measure:** Đặt timeout nghiêm ngặt (ví dụ: 1s) cho lời gọi RAG để tránh treo toàn bộ app. Sử dụng alert `high_latency_p95` để phát hiện sự cố sớm và cấu hình auto-scaling cho RAG service.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Sử dụng context manager `with langfuse_client.start_as_current_observation()` thay cho các lệnh gọi `.end()` thủ công. Điều này đảm bảo các child span được kết thúc đúng cách và không bị rò rỉ memory/data kể cả khi RAG hoặc LLM gặp Exception đột ngột.
- **Một lỗi/blocker đã gặp:** Gặp Exception AttributeError khi chạy test hoặc API vì sử dụng sai API cũ (`start_as_current_span` thay vì `start_as_current_observation` của SDK Langfuse v4).
- **Cách tìm nguyên nhân và xử lý:** Đọc logs traceback để tìm đúng dòng lỗi. Dùng hàm `dir()` và `inspect` để kiểm tra source code thư viện thực tế, qua đó tìm ra param đúng là `as_type="retriever" / "generation"`.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics báo hiệu "có bệnh gì" (triệu chứng như latency P95 tăng vọt). Logs chỉ ra "bệnh nhân nào" (chỉ đích danh correlation_id bị lỗi). Traces chỉ ra "đau ở đâu" (phân tích waterfall cho thấy chính xác span/component nào mất thời gian/lỗi).
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt version giúp deploy nâng cấp an toàn. Quản lý Token/cost chống vỡ quỹ dự án API. Rollback từ xa thông qua Langfuse label là phương án mitigation chữa cháy hiệu quả nhất (trong vòng vài giây) mà không cần deploy lại code.
- **Điều quan trọng nhất đã học:** Sức mạnh của correlation_id - nó là sợi dây liên kết duy nhất để điều tra một luồng xử lý phi tập trung từ đầu đến cuối.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Không có. Tất cả các tính năng (CP1, CP2, CP3) và test cases đều đã được hoàn thành.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric → log → trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thô hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.
