# AI_ChatBot (Python Version)

**Purpose:** Helps run chatbot on Windows 10/11 or macOS using VS Code.

---

## 🗂️ Preparation

### 📁 Step 0: Download Starter Files

* Download the ZIP package from Canvas: `Personal_AI.zip`
* Unzip the folder to a known location (e.g., Desktop)
* The folder structure looks like this:

```
```
Personal_AI/
├── app.py
├── requirements.txt
├── data_extraction.py
├── .env
├── extracted_data.db 
├── Fw_ BP355 enrolment project/   <- raw PDFs
├── courses_data.json
└── cyber_security_program_structure.json
```

---

## 🧰 Step 1: Check Python Version

### ✅ Requirement: Python 3.11

Open Terminal (macOS) or Command Prompt / PowerShell (Windows), and run:

```bash
python --version
```

If the version is **not 3.11.x**, download and install it from: [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)

---

## 🐍 Step 2: Set Up Virtual Environment (Recommended)

In your terminal, navigate into the unzipped folder:

```bash
cd path/to/Person_AI
```

Create and activate a virtual environment:

### Windows:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 Step 3: Install Dependencies
 

Don't forget to create a `.env` file in the project root directory to securely store your RMIT credentials:

```
RMIT_USERNAME=your_username_here
RMIT_PASSWORD=your_password_here
```

This is a safer alternative to hardcoding your username and password directly in `app.py`.

Once your virtual environment is activated, install all dependencies:
Don't forget to create a `.env` file in the project root directory to securely store your RMIT credentials:


```bash
pip install -r requirements.txt
```

If installation is successful, you’ll return to the prompt without errors.

Sometimes, You might see the warning like 'Import "streamlit" could not be resolvedPylancereportMissingImports' in your VS Code editor. Don't worry — this warning is from the VS Code language server (Pylance) and does not affect code execution as long as streamlit is installed correctly.

This usually happens when:

VS Code is not using the correct Python interpreter (e.g. your virtual environment), or

The language server hasn't picked up the environment changes yet.

✅ If you have already installed the requirements and can run the app using:

streamlit run app.py
then everything is working as expected, and you can safely ignore this warning.


---

## 🚀 Step 4: Run the Chatbot

To launch the chatbot UI:

```bash
streamlit run app.py
```

This will open a browser window with your chatbot interface.


---

## 📂 Step 5: Upload Course Data

In the chatbot UI:

1. Choose upload mode: `Structured JSON` or `PDF`
2. Upload the following (if using JSON mode):

   * `courses_data.json`
   * `cyber_security_program_structure.json`

### Additional Features:

* **Database Mode**: Select "Use Database" to query data directly from `extracted_data.db`
* **Multi-format Support**: Upload PDFs, JSON files, or use the pre-extracted database
* **Real-time Processing**: The chatbot processes uploads instantly and provides immediate feedback
* **Data Validation**: Automatic validation of uploaded files to ensure compatibility
* **Search Capabilities**: Advanced search through course codes, names, and descriptions
* **Export Options**: Download chat history and search results for later reference

### Optional: Convert PDF to JSON

Please refer to [Converting PDF to JSON notebook on Kaggle](https://www.kaggle.com/code/aisuko/converting-pdf-to-json)

You can also upload the original PDFs from the `Fw_ BP355 enrolment project` folder for testing unstructured sources.


## 💬 Step 6: Start Chatting

Type a question such as:

* *"What’s the difference between COSC2626 and INTE2402?"*
* *"How do I enrol in COSC1111?"*

The chatbot will respond based on the uploaded data.

---

## 🛠️ Step 7: Data Extraction Script

A Python script `data_extraction.py` is provided to extract course data directly from the RMIT website sitemap and course pages.

### Purpose:
- Download and parse the RMIT sitemap to find course URLs.
- Download and parse course pages to extract structured course information.
- Save extracted data into a SQLite database file `extracted_data.db`.

### Usage:

1. Ensure you have installed all dependencies including `requests`, `beautifulsoup4`, and `sqlite3` (already included in `requirements.txt`).

2. Run the extraction script from the command line:

```bash
python data_extraction.py
```

3. The script will download course data and save it into `extracted_data.db` in the project directory.

### Integration with Chatbot:

- The chatbot UI (`app.py`) can use the `extracted_data.db` database as a data source.
- In the chatbot UI, select the "Use Database" option to query and interact with the extracted course data.

---

## ❓ Troubleshooting

| Issue                          | Solution                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `streamlit: command not found` | Make sure virtual environment is activated                    |
| Cannot install packages        | Ensure you have Python 3.11 and pip is working                |
| No browser opens               | Visit [http://localhost:8501](http://localhost:8501) manually |
| Data not loaded properly       | Check file formats and filenames                              |

---

## Additional Setup for Environment Variables
Make sure to create a `.env` file containing your environment-specific credentials or add them directly to `app.py`:

---

## ✅ Done!
You're now ready to use the Personal AI ChatBot! The system is designed to help you navigate RMIT course information efficiently. Whether you're uploading JSON files, PDFs, or querying the database directly, the chatbot provides intelligent responses to help with course selection and enrollment questions.

For support or questions about the chatbot functionality, refer to the troubleshooting section above or consult the course materials.

Happy chatting! 🤖
