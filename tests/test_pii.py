from app.pii import hash_user_id, scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


# ── CP1: CCCD (12-digit national ID) ──────────────────────────────────────────

def test_scrub_cccd_plain() -> None:
    out = scrub_text("CCCD của tôi là 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_cccd_in_sentence() -> None:
    """CCCD số 12 chữ số không phải là số thẻ, phải bị scrub."""
    out = scrub_text("Số căn cước: 079204012345 của Nguyễn Văn A")
    assert "079204012345" not in out
    assert "REDACTED_CCCD" in out


def test_no_false_positive_short_number() -> None:
    """Số có ít hơn 12 chữ số không phải CCCD."""
    out = scrub_text("Mã đơn hàng: 12345678")
    assert "REDACTED_CCCD" not in out


# ── CP1: Credit / Debit card ──────────────────────────────────────────────────

def test_scrub_credit_card_plain() -> None:
    out = scrub_text("Thẻ 4111111111111111 đã bị từ chối")
    assert "4111111111111111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_credit_card_dashes() -> None:
    out = scrub_text("Card: 4111-1111-1111-1111 expired")
    assert "4111-1111-1111-1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_credit_card_spaces() -> None:
    out = scrub_text("Số thẻ: 5500 0000 0000 0004")
    assert "5500 0000 0000 0004" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_mixed_pii_in_one_string() -> None:
    """Một chuỗi chứa nhiều loại PII cùng lúc."""
    text = "Email user@example.com, phone 0901234567, CCCD 012345678901"
    out = scrub_text(text)
    assert "user@example.com" not in out
    assert "0901234567" not in out
    assert "012345678901" not in out
    assert "REDACTED_EMAIL" in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out


# ── hash_user_id ──────────────────────────────────────────────────────────────

def test_hash_user_id_returns_12_chars() -> None:
    result = hash_user_id("user-abc-123")
    assert len(result) == 12
    assert result.isalnum()


def test_hash_user_id_is_deterministic() -> None:
    assert hash_user_id("same-user") == hash_user_id("same-user")


def test_hash_user_id_differs_for_different_users() -> None:
    assert hash_user_id("user-A") != hash_user_id("user-B")
