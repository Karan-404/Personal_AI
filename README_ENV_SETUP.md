# Environment Variable Setup for RMIT Cyber Security Course Advisor

This document explains how to keep your AWS Cognito credentials secure and out of the source code by using environment variables.

## Steps to Setup

1. Create a file named `.env` in the root directory of the project.

2. Add your credentials to the `.env` file in the following format:

```
RMIT_USERNAME=your_username_here
RMIT_PASSWORD=your_password_here
```

3. Make sure `.env` is included in your `.gitignore` file to prevent it from being committed to version control.

4. The application uses the `python-dotenv` package to load these variables at runtime.

## Running the Application

- Install dependencies if not done already:

```
pip install -r requirements.txt
```

- Run the app:

```
streamlit run app.py
```

The app will use the credentials from your `.env` file for authentication.

## Sharing the Code

- Share the code without the `.env` file.
- Provide a `.env.example` file with placeholder values for others to create their own `.env`.

This approach keeps your credentials hidden while allowing others to run the app with their own credentials.
