# RMIT Cyber Security Course Advisor (AI ChatBot)

An AI-powered chatbot designed to assist RMIT Cyber Security students with course planning, data extraction, and conversational queries—implemented in Python using Streamlit and AWS Bedrock (Claude AI).

---

## 🚀 Features

- **Conversational AI:** Chatbot interface powered by Claude AI (AWS Bedrock) for natural language course queries.
- **Multi-format Data Support:** Upload and query course data in JSON, CSV, PDF, SQLite, and image formats.
- **OCR & PDF Extraction:** Extract text from images and PDFs using `pytesseract` and `pdfplumber`.
- **AWS Cognito Authentication:** Secure login with your RMIT credentials (kept safe via `.env` and `python-dotenv`).
- **Course Data Scraping:** Automated script to scrape and update course data from the RMIT website.
- **Database Integration:** Store and query courses in an SQLite database.
- **Downloadable Chat History:** Save and load chat history in JSON format.
- **Typing Animation:** Simulated typing for AI responses.

---

## 🗂️ Folder Structure

```
Personal_AI/
├── app.py                         # Main Streamlit app
├── requirements.txt               # Python dependencies
├── data_extraction.py             # Course data scraping script
├── .env                           # Your credentials (not committed)
├── extracted_data.db              # SQLite DB (optional)
├── Fw_ BP355 enrolment project/   # Raw PDFs (optional)
├── courses_data.json              # Example JSON data
├── cyber_security_program_structure.json # Example JSON data
├── DOCUMENTATION.md               # Technical details
├── README_ENV_SETUP.md            # Env var setup guide
└── readme.md                      # This README
```

---

## 🧰 Quickstart

### 1. Check Python Version

- **Python 3.11** required. Check with:
  ```bash
  python --version
  ```
  Download: [Python 3.11](https://www.python.org/downloads/release/python-3110/)

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:
```
RMIT_USERNAME=your_username_here
RMIT_PASSWORD=your_password_here
```
**Never commit `.env`!**  
(See `README_ENV_SETUP.md` for details.)

### 5. Run the Chatbot

```bash
streamlit run app.py
```

Go to [http://localhost:8501](http://localhost:8501) if a browser does not open automatically.

---

## 📂 Working with Data

- **Upload course data**: Use the UI to upload `courses_data.json`, `cyber_security_program_structure.json`, PDF, CSV, or SQLite files.
- **Convert PDF to JSON**: Use the in-app feature for easier integration.
- **Use database**: Select "Use Database" in the UI to query `extracted_data.db`.

---

## 🛠️ Data Extraction Script

Extract latest course data from the RMIT website:

1. Ensure all dependencies are installed.
2. Run:
```bash
   python data_extraction.py
```
3. The script saves data to `extracted_data.db`.

---

## 💬 Example Interactions

Type questions like:
- “What’s the difference between COSC2626 and INTE2402?”
- “How do I enrol in COSC1111?”

The chatbot provides intelligent answers based on your uploaded data.

---

## 🧑‍💻 Technical Overview

- **Main app (`app.py`)** uses Streamlit for UI, manages authentication (AWS Cognito), and interacts with AWS Bedrock Claude for AI responses.
- **Data extraction (`data_extraction.py`)** scrapes and parses RMIT course data into SQLite using `requests` and `beautifulsoup4`.
- **Data handling:** Supports text extraction from PDFs/images, CSV parsing, and database loading.
- **Libraries:** Streamlit, boto3, pytesseract, pdfplumber, sqlite3, dotenv, requests, beautifulsoup4.

See `DOCUMENTATION.md` for architecture, key functions, and library usage.

---

## ❓ Troubleshooting

| Issue                          | Solution                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `streamlit: command not found` | Activate your virtual environment                             |
| Package install fails          | Ensure Python 3.11 and `pip` are working                      |
| No browser opens               | Visit [http://localhost:8501](http://localhost:8501) manually |
| Data not loaded                | Check file formats and filenames                              |

---
Note: This site uses code template provided by © RMIT COSC1111. 

## 📄 License

MIT License


---

Happy chatting! 🤖