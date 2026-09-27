# ⚡ Quick Start - 10 Steps

## Step 1: Create Google Sheet
- Go to [Google Sheets](https://sheets.google.com)
- Create sheet named "Family Tree"
- Add headers: `Name | Generation | Gender | Date_of_Birth | Father_Name | Mother_Name | Spouse_Name | Date_of_Death`

## Step 2: Add Family Data
Copy this template and fill in:
```
Name,Generation,Gender,Date_of_Birth,Father_Name,Mother_Name,Spouse_Name,Date_of_Death
Grandpa,1,M,15/05/1930,,,Grandma,
Grandma,1,F,20/03/1935,,,Grandpa,
Dad,2,M,10/07/1960,Grandpa,Grandma,Mom,
Mom,2,F,12/08/1962,,,Dad,
You,3,M,15/02/1990,Dad,Mom,,
```

**Rules:**
- NO ID needed - app generates it!
- Gender: "M" or "F" only
- Dates: DD/MM/YYYY format
- Age: Auto-calculated from dates!
- Leave parent names blank if unknown

## Step 3: Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project "Family Tree App"
3. Go to APIs & Services → Library
4. Search & enable "Google Sheets API"

## Step 4: Create Service Account
1. APIs & Services → Credentials
2. Create Credentials → Service Account
3. Name: `family-tree-app`
4. Skip optional fields → Done

## Step 5: Download JSON Key
1. Click on the service account you created
2. Go to "Keys" tab
3. Add Key → Create New Key → JSON
4. Save the file

## Step 6: Share Sheet with Service Account
1. Open the JSON file
2. Copy the `client_email` value
3. Open your Google Sheet
4. Click Share → Paste email → Give Editor access

## Step 7: Setup Local Files
Create these files:
```
project/
├── app.py (provided)
├── requirements.txt (provided)
├── .streamlit/
│   └── secrets.toml (create this)
```

## Step 8: Fill secrets.toml
Create `.streamlit/secrets.toml`:
```toml
FAMILY_TREE_PASSWORD = "your_password"
SHEET_NAME = "Family Tree"

[gcp_service_account]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_KEY_ID"
private_key = "YOUR_PRIVATE_KEY"
client_email = "YOUR_SERVICE_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
```

Copy values from your downloaded JSON file.

## Step 9: Test Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Open http://localhost:8501
# Login with your password
```

## Step 10: Deploy to Streamlit Cloud
1. Push code to GitHub (don't push secrets.toml!)
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your GitHub repo and main file
5. Go to Settings → Secrets
6. Paste your secrets.toml content
7. Done! Share the URL with family

---

## 🎉 You're Done!

Your app is live at: `https://YOUR_USERNAME-family-tree-app.streamlit.app`

### To Update Family Tree:
- Edit Google Sheet
- Click "Refresh Data" in app OR wait 5 minutes

### Troubleshooting:
- **"Password not configured"**: Add FAMILY_TREE_PASSWORD to secrets
- **"Sheet not found"**: Check SHEET_NAME matches your Google Sheet name exactly
- **"Failed to connect"**: Verify service account has Editor access to sheet

---

## Key Points:

✅ **Password**: Only you set this  
✅ **Data Private**: Only people with link + password can see  
✅ **Auto Updates**: Changes to sheet appear in 5 minutes  
✅ **Free Forever**: Streamlit Cloud free tier  
✅ **Mobile Friendly**: Works on phones  

---

## Support:

- Full setup guide: See `SETUP_GUIDE.md`
- Sheet format examples: See `GOOGLE_SHEET_FORMAT.md`
- Issues? Check SETUP_GUIDE.md troubleshooting section

**Happy family tree building! 🌳**