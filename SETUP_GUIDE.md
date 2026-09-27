# 🌳 Family Tree App - Complete Setup Guide

## Overview
This is a password-protected, interactive family tree application built with Streamlit that pulls data from a Google Sheet and displays it as an interactive visualization.

---

## 📋 Table of Contents
1. [Google Sheets Setup](#google-sheets-setup)
2. [Google API Configuration](#google-api-configuration)
3. [Local Setup & Testing](#local-setup--testing)
4. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
5. [How to Use](#how-to-use)

---

## 🔧 Google Sheets Setup

### Step 1: Create the Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet named **"Family Tree"** (or any name you prefer)

### Step 2: Add Column Headers

In the first row, add these headers (exact names matter):

```
Name | ID | Father_ID | Mother_ID | Gender | Birth_Year | Spouse_ID
```

### Step 3: Sample Data Format

Here's an example of how to structure your family data:

| Name | ID | Father_ID | Mother_ID | Gender | Birth_Year | Spouse_ID |
|------|----|-----------|-----------|-|------------|-----------|
| Grandpa John | 1 | | | M | 1940 | 2 |
| Grandma Jane | 2 | | | F | 1942 | 1 |
| Uncle Bob | 3 | 1 | 2 | M | 1962 | 4 |
| Aunt Mary | 4 | | | F | 1965 | 3 |
| Your Dad | 5 | 1 | 2 | M | 1965 | 6 |
| Your Mom | 6 | | | F | 1968 | 5 |
| You | 7 | 5 | 6 | M | 1990 | |
| Your Sister | 8 | 5 | 6 | F | 1993 | |
| Your Brother | 9 | 5 | 6 | M | 1995 | |

### Important Rules:

- **ID**: Unique identifier for each person (can be number or text)
- **Father_ID**: The ID of the father (leave blank if unknown)
- **Mother_ID**: The ID of the mother (leave blank if unknown)
- **Gender**: "M" for Male or "F" for Female
- **Birth_Year**: Year of birth (optional, but helpful)
- **Spouse_ID**: Optional - not used in visualization yet
- **Name**: Full name of the person

### Example with Complete Family Tree:

```
Name,ID,Father_ID,Mother_ID,Gender,Birth_Year,Spouse_ID
Grandpa Jack,1,,M,1935,
Grandma Susan,2,,F,1938,
Dad Robert,3,1,2,M,1960,4
Mom Patricia,4,,F,1962,3
You,5,3,4,M,1985,
Your Sister,6,3,4,F,1987,
```

---

## 🔐 Google API Configuration

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Name it "Family Tree App"
4. Click "Create"
5. Wait for the project to be created

### Step 2: Enable Google Sheets API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

### Step 3: Create a Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the form:
   - Service Account Name: `family-tree-app`
   - Click "Create and Continue"
4. Skip the optional steps and click "Done"

### Step 4: Generate JSON Key

1. Under "Service Accounts", click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" and click "Create"
5. A JSON file will download - **Keep this safe!**

### Step 5: Share the Sheet with the Service Account

1. Open the JSON file with a text editor
2. Copy the value of `"client_email"` (looks like: `family-tree-app@...iam.gserviceaccount.com`)
3. Open your Family Tree Google Sheet
4. Click "Share" in the top right
5. Paste the email and give it "Editor" access
6. Uncheck "Notify people" and click "Share"

---

## 💻 Local Setup & Testing

### Step 1: Clone or Download Project Files

You should have these files:
```
project/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── secrets.toml
└── SETUP_GUIDE.md
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Create Secrets File

Create a `.streamlit` folder in your project directory (if it doesn't exist):

```bash
mkdir .streamlit
```

Create a file called `secrets.toml` inside `.streamlit/`:

```toml
FAMILY_TREE_PASSWORD = "your_password_here"
SHEET_NAME = "Family Tree"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account-email@iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

**To fill this out:**
1. Open the JSON file you downloaded from Google Cloud
2. Copy the entire content
3. Paste it in the `[gcp_service_account]` section (replace the placeholder)
4. Change `FAMILY_TREE_PASSWORD` to your desired password

### Step 4: Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

**To test:**
- Enter your password
- You should see the family tree visualization
- Check the "View Family Data" section to see the data

---

## 🚀 Streamlit Cloud Deployment

### Step 1: Prepare GitHub Repository

1. Create a GitHub account if you don't have one
2. Create a new public repository named `family-tree-app`
3. Push your files to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/family-tree-app.git
git push -u origin main
```

**Important**: Do NOT push `.streamlit/secrets.toml` to GitHub!

Add a `.gitignore` file:
```
.streamlit/secrets.toml
*.pyc
__pycache__/
.DS_Store
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `YOUR_USERNAME/family-tree-app`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

### Step 3: Add Secrets to Streamlit Cloud

1. Once deployed, click on your app in Streamlit Cloud
2. Click "Settings" in the top right
3. Go to "Secrets"
4. Paste your `secrets.toml` content (or just the gcp_service_account and password parts)

```toml
FAMILY_TREE_PASSWORD = "your_password_here"
SHEET_NAME = "Family Tree"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

5. Click "Save"

### Step 4: Share Your App

Your app is now live at:
```
https://YOUR_USERNAME-family-tree-app.streamlit.app
```

Share this link with your family!

---

## 📖 How to Use

### For End Users (Your Family):

1. Open the app link
2. Enter the password (which you set)
3. View the interactive family tree
4. **Hover over names** to see more info
5. **Drag to move** nodes around
6. **Scroll to zoom** in/out
7. Click "View Family Data" to see the table

### Color Coding:
- 🔵 **Blue** = Male
- 🔴 **Pink** = Female
- **Gray** = Unknown Gender

### Updating the Tree:

To add or modify family members:
1. Edit your Google Sheet
2. Click "Refresh Data" in the app (or wait 5 minutes for auto-refresh)
3. The tree updates automatically!

---

## 🔄 Updating Family Data

The app fetches data from Google Sheets every 5 minutes automatically. To force an immediate refresh:

1. Click the **"🔄 Refresh Data"** button in the app
2. Or edit the Google Sheet and the changes will appear within 5 minutes

### Adding New Family Members:

1. Open your Google Sheet
2. Add a new row with:
   - Unique ID
   - Name
   - Father_ID (if applicable)
   - Mother_ID (if applicable)
   - Gender (M or F)
   - Birth_Year (optional)
3. The app will show the update within 5 minutes

---

## 🐛 Troubleshooting

### "Password not configured in secrets"
- Add `FAMILY_TREE_PASSWORD` to your secrets.toml file
- On Streamlit Cloud, add it in Settings → Secrets

### "Failed to connect to Google Sheets"
- Check that the service account email has access to your Google Sheet
- Verify the `SHEET_NAME` matches your actual sheet name
- Ensure the JSON credentials are correctly copied

### Sheet not loading / Empty sheet
- Make sure your Google Sheet has headers in the first row
- Check that IDs are unique
- Ensure Father_ID and Mother_ID reference valid IDs

### Tree not displaying correctly
- Verify that Gender column has "M" or "F" values
- Check for typos in Father_ID or Mother_ID references
- Ensure IDs are exact matches (no extra spaces)

### "Spreadsheet not found"
- Open your Google Sheet and copy the name exactly
- Update `SHEET_NAME` in your secrets.toml
- Make sure you're using the correct sheet name (not the URL)

---

## 🔐 Security Notes

1. **Keep your password safe** - Don't share it publicly
2. **Don't commit secrets.toml to GitHub** - Use .gitignore
3. **The service account key** should be kept private
4. **Use a strong password** for the app
5. **Only share the app link** with trusted family members

---

## 📱 Access from Mobile

The app is fully responsive and works on:
- ✅ Phones (iOS/Android)
- ✅ Tablets
- ✅ Desktop browsers

---

## ❓ FAQ

**Q: Can multiple people view at the same time?**
A: Yes! Streamlit Cloud supports concurrent users.

**Q: How often does it update?**
A: Every 5 minutes automatically, or immediately when you click "Refresh Data".

**Q: Can I customize the appearance?**
A: Yes, contact the developer to modify colors, fonts, or layout.

**Q: Is the data private?**
A: Yes, password protection ensures only authorized family members can view it.

**Q: Can I add photos?**
A: Currently not, but this can be added with Google Photos integration.

---

## 📞 Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the app logs on Streamlit Cloud
3. Verify your Google Sheet format matches the examples

---

**Version**: 1.0  
**Last Updated**: 2026  
**Made with ❤️ for families**
