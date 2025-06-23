# Assignment 3 Chatbot Deployment Guide (Python Version)

**Purpose:** Help students and tutors deploy and run the Assignment 3 chatbot on Windows 10/11 or macOS using VS Code.

---

## 🗂️ Preparation

### 📁 Step 0: Download Starter Files

* Download the ZIP package from Canvas: `Assignment3_Chatbot_Python.zip`
* Unzip the folder to a known location (e.g., Desktop)
* The folder structure looks like this:

```
Assignment3_Chatbot_Python/
├── app.py
├── requirements.txt
├── chatbot_logic.py
├── Fw_ BP355 enrolment project/   <- raw PDFs
├── courses_data.json
├── cyber_security_program_structure.json
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
cd path/to/Assignment3_Chatbot_Python
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

Don't forget to paste your username and password inside to the app.py

```
APP_CLIENT_ID = "3h7m15971bnfah362dldub1u2p"
USERNAME = "" # Replace with your username
PASSWORD = ""    # Replace with your password
```

Once your virtual environment is activated, install all dependencies:

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

### Optional: Convert PDF to JSON

Please refer to [Converting PDF to JSON notebook on Kaggle](https://www.kaggle.com/code/aisuko/converting-pdf-to-json)


You can also upload the original PDFs from the `data/Fw_ BP355 enrolment project` folder for testing unstructured sources.

---

## 💬 Step 6: Start Chatting

Type a question such as:

* *"What’s the difference between COSC2626 and INTE2402?"*
* *"How do I enrol in COSC1111?"*

The chatbot will respond based on the uploaded data.


---

## ❓ Troubleshooting

| Issue                          | Solution                                                      |
| ------------------------------ | ------------------------------------------------------------- |
| `streamlit: command not found` | Make sure virtual environment is activated                    |
| Cannot install packages        | Ensure you have Python 3.11 and pip is working                |
| No browser opens               | Visit [http://localhost:8501](http://localhost:8501) manually |
| Data not loaded properly       | Check file formats and filenames                              |

---

## ✅ Done!

You now have a fully working Assignment 3 chatbot. You can begin answering assignment questions and improving your knowledge base.

For more advanced tasks (prompt tuning, data cleaning, documentation), please refer to the **Course Enrolment Chatbot Handbook**.

---

© RMIT COSC1111 - May 2025
