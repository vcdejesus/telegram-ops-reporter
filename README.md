Telegram Sales Ingestion & Automation Bot 📊🤖
An open-source Python tool that turns Telegram into a mobile data-entry interface for sales and field operations, automatically syncing transactions to Google Sheets and backing up records to Google Drive.
📌 Overview
Collecting field sales or operational entries usually suffers from friction and manual delay. This project provides a lightweight, conversational point-of-sale workflow inside Telegram. Data entered by field operators is validated and immediately persisted to Google Sheets for live business intelligence dashboards, while archiving timestamped transaction CSVs in Google Drive.
✨ Key Features
Interactive Conversation Flow: Step-by-step guided data entry (operator, product, amount, payment method).
Google Sheets Integration: Instant row appending via gspread for real-time reporting.
Google Drive Backup: Automatic generation and cloud storage of transaction records.
Cloud-Ready (Render / PaaS): Embedded Flask health-check endpoint to maintain container uptime on web hosts.
Enterprise Security: Credential loading strictly managed via environment variables.
🛠️ Tech Stack & Architecture
Language: Python 3.10+
Messaging Engine: python-telegram-bot (v20+ Async)
APIs & Storage: Google Sheets API (gspread), Google Drive API v3
Web Service: Flask (Health-check monitor for cloud hosting)
🚀 Getting Started
Prerequisites
Python 3.10 or higher.
A Telegram Bot Token from @BotFather.
A Google Cloud Service Account with permissions enabled for:
Google Sheets API
Google Drive API
A Google Drive target folder ID and a target Google Sheet shared with the service account email.
Installation
Clone the repository:
git clone https://github.com/vcdejesus/telegram-ops-reporter.git
cd telegram-ops-reporter
Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate
Install required packages:
pip install -r requirements.txt
⚙️ Environment Variables
Configure the following variables in your hosting environment (Render, Railway, or local .env):
Variable	Description
TELEGRAM_TOKEN	Token provided by @BotFather
GOOGLE_CREDENTIALS_JSON	Full string content of the Google Service Account JSON
ID_PASTA_DRIVE	Google Drive target folder ID for CSV exports
NOME_DA_PLANILHA	Target Google Spreadsheet title
PORT	Port for the health-check web server (default: 10000)
💬 Bot Commands
/start - Displays initial greeting and instructions.
/novavenda - Initiates the 4-step sales registration conversation flow.
/cancelar - Aborts the current transaction session.
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
