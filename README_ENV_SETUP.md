# Environment Variable Setup

This document explains how to keep your credentials secure and out of the source code by using environment variables.

---

## Steps to Setup

1. **Create a `.env` File**

   Create a file named `.env` in the root directory of your project.

2. **Add Your Credentials**

   Add your credentials to the `.env` file in the following format:
   ```
   RMIT_USERNAME=your_username_here
   RMIT_PASSWORD=your_password_here
   ```

3. **.gitignore**

   Ensure `.env` is included in your `.gitignore` file to prevent it from being committed to version control.

4. **How Variables are Loaded**

   The application uses the `python-dotenv` package to load these variables at runtime. You do not need to manually load them in your code—just ensure the `.env` file exists.

---

## Running the Application

- **Install dependencies (if not already done):**
  ```bash
  pip install -r requirements.txt
  ```

- **Run the Streamlit app:**
  ```bash
  streamlit run app.py
  ```

  The app will use the credentials from your `.env` file for authentication.

---

## Running the Data Extraction Script

You can use the included `data_extraction.py` script to fetch and update course data from the RMIT website.

### How to Run

1. **Ensure all dependencies are installed (see above).**
2. **Run the script:**
   ```bash
   python data_extraction.py
   ```
3. The script will download and parse course data, saving it into `extracted_data.db` in the project directory.

### Changing Filters

- The script filters which URLs/courses to scrape based on specific keywords or logic in the source.
- To change which courses or data are extracted, **edit the filter logic** in the `data_extraction.py` file (look for sections that filter URLs or course types).
- Example: To include/exclude certain programs or keywords, adjust the list of keywords or modify the filtering conditions in the script.
- **Note:** Be cautious when modifying the script, as incorrect filtering can lead to incomplete or incorrect data

---

## Sharing the Code

- **Never share your `.env` file.**
- Instead, provide a `.env.example` file with placeholder values so others can create their own `.env`.

Example `.env.example`:
```
RMIT_USERNAME=your_username_here
RMIT_PASSWORD=your_password_here
```

---

**This approach keeps your credentials hidden while allowing others to run the app with their own credentials.**