# 專案交接紀錄（handoff.md）

## 📍 目前狀態（2026-09-26）
- **RDQ 規格訪談完成**：確認產出「成果表（自動圖文排版）」、「簽到表」與「內聘講師領據」（由社群成員輪流擔任）。規格卡位於 `rdq/RDQ-spec-steam-community-docs-20260926.md`，狀態為 `confirmed`。
- **全域 Skill 與本地腳本已就緒**：
  - 全域 Skill：`~/.gemini/config/skills/steam-community-docs/`
  - 本地生成腳本：`scripts/generate_docs.py`、`scripts/send_gmail.py`、`scripts/install_skill.py`
  - 跨平台一鍵設定：`setup.bat` (Windows 11) 與 `setup.sh` (macOS)
  - 核心資料設定檔：`scripts/members.json`、`scripts/sessions_plan.json`
- **已完成驗證**：已完成 docx 生成、東亞字型（標楷體）注入、照片壓縮與跨平台 PDF 轉存之端到端測試。
- **Gmail 成果繳交與確認機制就緒**：嚴格實施「寄信前對話預覽確認」，僅夾帶成果表與簽到表（排除領據），支援一鍵喚起 Gmail 撰寫視窗。
- **專案結構初始化**：已配置 `AGENTS.md`、`ANTIGRAVITY.md`、`README.md`、`.gitignore`，並於 Obsidian 建立專案駕駛艙。

## 🧭 下一步行動
1. 當使用者提供各場次活動照片與時間時，自動比對場次並詢問內聘講師，一鍵產出對應 MMDD 資料夾與完整報支檔案。
2. 呈現 Gmail 繳交預覽，經使用者確認後協助寄送至 `tc.steam114@gmail.com`。
3. 追蹤 115 年度 16 節鐘點費（共 16,000 元）之社群成員輪流內聘講師領據，於 115 年 11 月 20 日前完成核銷。

