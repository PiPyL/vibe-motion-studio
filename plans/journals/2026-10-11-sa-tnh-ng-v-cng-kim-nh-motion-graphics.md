---
title: Sửa tính đúng và cổng kiểm định motion graphics
date: 2026-10-11
summary: "Pipeline hết cắt nhạc, shell expansion và lệch transcript; cổng artifact làm fail khi lệch."
---

# Sửa tính đúng và cổng kiểm định motion graphics

## What happened

Review tại commit 570248a chỉ ra sáu lỗi pipeline và bốn khoảng trống kiểm định. Cook sửa trong repo: pad sidechain trước compressor, truyền argv không qua shell, một transcript nói (`data/vo-spoken.json`) dùng chung cho TTS, alignment, caption và word anchor, karaoke theo alignment hoặc cụm nghĩa và fail khi tràn khung, headline giữ `em`/`br`/accent pill, chữ Clay `#242b35` trên `#ff8a65`, và cổng đo stem/caption/social thoát mã 1.

Sau simplify, `--only` khi đổi ngôn ngữ vẫn có thể để WAV cũ sống sót. Đã siết: mọi clip cũ không được tái tạo thì lần đổi ngôn ngữ thoát. `python3 -m unittest discover -s scripts/tests` — 17 tests OK.

## Decision

Ưu tiên tính đúng và kiểm định trước style mới. Không render video chuẩn, không gọi TTS trả phí, không đổi `pcm_s16le`, không đồng bộ bản skill đã cài. Plan `plans/261011-0522-video-quality-hardening` chuyển `in-progress`. Checkbox mẫu trong phase vẫn để trống vì không mô tả việc đã làm. Phase sáng tạo và benchmark chưa bắt đầu.

## Next steps

Dựng vòng brief → storyboard → khung hình mẫu → animatic trước render dài. Sau đó mới làm bộ video chuẩn năm style, ngang/dọc, ngôn ngữ và thời lượng. Khi phát hành skill, cập nhật bản đã cài từ repo `1.2.0`. Chưa commit.

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
