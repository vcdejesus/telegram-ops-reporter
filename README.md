# Telegram Sales Ingestion & Automation Bot 📊🤖

An open-source Python tool that turns Telegram into a mobile data-entry interface for sales and field operations, automatically syncing transactions to Google Sheets and backing up records to Google Drive.

## 📌 Overview

Collecting field sales or operational entries usually suffers from friction and manual delay. This project provides a lightweight, conversational point-of-sale workflow inside Telegram. Data entered by field operators is validated and immediately persisted to Google Sheets for real-time dashboards, while archiving transaction CSVs in Google Drive.

## ✨ Key Features

- **Interactive Conversation Flow:** Step-by-step guided data entry (operator, product, amount, payment method).
- **Google Sheets Integration:** Instant row appending via `gspread` for live business reporting.
- **Google Drive Backup:** Automatic generation and storage of timestamped transaction records.
- **Cloud-Ready (Render / PaaS):** Embedded Flask health-check server to maintain container uptime.
- **Enterprise Security:** Credential loading strictly via environment variables (`GOOGLE_CREDENTIALS_JSON` and `TELEGRAM_TOKEN`).
