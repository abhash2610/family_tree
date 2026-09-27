# 🌳 Family Tree App

An interactive, password-protected family tree visualization application built with Streamlit and Pyvis.

## Features

✨ **Interactive Visualization**
- Drag and move family members around
- Zoom in/out to explore your tree
- Hover to see additional information
- Color-coded by gender (blue for male, pink for female)

🔐 **Password Protected**
- Keep your family data private
- Only share link with trusted family members
- Simple password authentication

📊 **Real-Time Updates**
- Pulls data from Google Sheets
- Updates automatically every 5 minutes
- Edit once, changes appear instantly

📱 **Mobile Friendly**
- Works on phones, tablets, and desktops
- Responsive design
- Full touch support

☁️ **Free Hosting**
- Deploy on Streamlit Cloud for free
- No servers to manage
- Automatic HTTPS

🔗 **Simple Sharing**
- Share a single link with family
- No need to share passwords separately
- Works globally

## Quick Start

### 1️⃣ **Prepare Your Data** (5 minutes)
- Create a Google Sheet with family data
- Use format: Name | ID | Father_ID | Mother_ID | Gender | Birth_Year
- Share with service account

### 2️⃣ **Setup Google API** (10 minutes)
- Enable Google Sheets API
- Create service account
- Download JSON credentials

### 3️⃣ **Configure App** (5 minutes)
- Fill in `secrets.toml`
- Set password
- Test locally

### 4️⃣ **Deploy to Cloud** (5 minutes)
- Push to GitHub
- Deploy to Streamlit Cloud
- Share link with family

**Total time: ~25 minutes**

## Documentation

- 📖 [Setup Guide](SETUP_GUIDE.md) - Complete step-by-step instructions
- ⚡ [Quick Start](QUICK_START.md) - 10-step quick reference
- 📊 [Google Sheet Format](GOOGLE_SHEET_FORMAT.md) - Data format guide with examples

## Project Structure

```
family-tree-app/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   ├── secrets.toml               # Your credentials (DO NOT COMMIT)
│   └── secrets.toml.template      # Template for secrets
├── SETUP_GUIDE.md                 # Complete setup instructions
├── QUICK_START.md                 # 10-step quick guide
├── GOOGLE_SHEET_FORMAT.md         # Data format guide
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## Requirements

- Python 3.7+
- Google Account with Google Cloud access
- GitHub account (for deployment)
- 10-15 minutes for setup

## Installation

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/family-tree-app.git
cd family-tree-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials

# Run locally
streamlit run app.py
```

Visit `http://localhost:8501` and enter your password.

### Deployment to Streamlit Cloud

1. Push code to GitHub (don't commit `secrets.toml`)
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and select your repository
4. Go to Settings → Secrets and paste your secrets
5. Your app is live!

## Configuration

### Environment Variables (in `secrets.toml`)

```toml
FAMILY_TREE_PASSWORD = "your_password_here"
SHEET_NAME = "Family Tree"

[gcp_service_account]
# Copy entire service account JSON here
```

### Google Sheet Format

| Column | Required | Description |
|--------|----------|-------------|
| Name | ✅ | Full name |
| ID | ✅ | Unique identifier |
| Father_ID | ✅ | Reference to father's ID |
| Mother_ID | ✅ | Reference to mother's ID |
| Gender | ✅ | "M" or "F" |
| Birth_Year | ❌ | Year of birth |

See [GOOGLE_SHEET_FORMAT.md](GOOGLE_SHEET_FORMAT.md) for detailed examples.

## Usage

### For End Users

1. Open the app URL
2. Enter the password
3. Interact with the tree:
   - **Drag** nodes to rearrange
   - **Scroll** to zoom in/out
   - **Hover** over names for info
   - Click **"View Family Data"** to see table

### For Administrators

1. Edit the Google Sheet to add/modify family members
2. Click "🔄 Refresh Data" in the app OR wait 5 minutes
3. Changes appear automatically

## Features Explained

### 🎨 Color Coding
- **Blue**: Male
- **Pink**: Female
- **Gray**: Unknown gender

### 🔄 Auto-Refresh
- Data updates every 5 minutes automatically
- Click "Refresh Data" button for immediate update

### 📊 Statistics
- Total family members count
- Gender breakdown
- Root members (ancestors with no parents)

### 📋 Data View
- See all family data in table format
- Sortable columns
- Export-ready format

## Troubleshooting

### Common Issues

**"Password not configured in secrets"**
- Add `FAMILY_TREE_PASSWORD` to `secrets.toml`
- On Streamlit Cloud: Settings → Secrets → Add it there

**"Failed to connect to Google Sheets"**
- Verify service account has Editor access to sheet
- Check `SHEET_NAME` matches your actual sheet
- Ensure JSON credentials are correctly formatted

**"Spreadsheet not found"**
- Copy the exact sheet name from Google Sheets
- Update `SHEET_NAME` in `secrets.toml`
- Avoid using URL instead of name

**"Tree not displaying"**
- Check Gender column has "M" or "F" (not "Male"/"Female")
- Verify Father_ID and Mother_ID reference valid IDs
- Ensure no circular relationships

See [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting section for more help.

## Security

🔐 **Data Privacy**
- Password protection prevents unauthorized access
- Only shared family members get the link
- Data stored in your Google Sheet (you control access)
- No data stored on Streamlit servers

⚠️ **Best Practices**
- Use a strong password
- Don't commit `secrets.toml` to GitHub
- Only share link with trusted family members
- Keep service account key private

## Performance

- **Load Time**: 2-5 seconds initial load
- **Update Frequency**: Every 5 minutes (configurable)
- **Concurrent Users**: Unlimited on Streamlit Cloud
- **Family Size**: Tested up to 500+ members

## Browser Support

✅ Chrome/Edge
✅ Firefox
✅ Safari
✅ Mobile browsers (iOS Safari, Chrome mobile)

## Customization

The app can be customized for:
- Custom colors and themes
- Additional family information
- Photo integration
- Spouse relationships display
- Multiple family trees

Contact the developer for custom modifications.

## Updates

### Version 1.0 (Current)
- Interactive Pyvis visualization
- Password protection
- Google Sheets integration
- Mobile responsive design
- Auto-refresh functionality

### Planned Features
- Photo support
- Extended family relationships
- Export to PDF
- Multi-language support
- Mobile app

## Deployment Options

### Recommended: Streamlit Cloud ⭐
- Free tier
- Auto-deploy from GitHub
- Simple configuration
- Perfect for small-medium projects

### Alternative Options
- Heroku ($5-7/month minimum)
- Railway ($5+/month)
- Fly.io (free tier available)
- DigitalOcean ($5+/month)

See SETUP_GUIDE.md for deployment comparison.

## FAQ

**Q: Is my data safe?**
A: Yes, password-protected and only shared family members can access it.

**Q: How many people can view simultaneously?**
A: Unlimited on Streamlit Cloud free tier.

**Q: How often does it update?**
A: Every 5 minutes automatically, or instantly when you click "Refresh Data".

**Q: Can I add photos?**
A: Not in current version, but can be added with Google Photos integration.

**Q: Can I export the tree?**
A: The interactive visualization can be shared via link; export to PDF can be added.

**Q: What if someone doesn't know their parents?**
A: Leave Father_ID and Mother_ID blank - they'll still appear in the tree.

**Q: Can I use it for non-family relationships?**
A: Yes, the structure can be adapted for any hierarchical relationships.

## Support & Troubleshooting

1. **Quick Issues**: Check [QUICK_START.md](QUICK_START.md)
2. **Setup Problems**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) troubleshooting
3. **Data Format**: Review [GOOGLE_SHEET_FORMAT.md](GOOGLE_SHEET_FORMAT.md)
4. **Still stuck?**: Review the app logs in Streamlit Cloud

## Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Pyvis (network graphs)
- **Backend**: Python
- **Data Source**: Google Sheets API
- **Hosting**: Streamlit Cloud
- **Authentication**: Simple password

## License

This project is provided as-is for personal use.

## Contributing

To contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Changelog

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for version history.

## Contact

For questions or issues, refer to the documentation files included.

---

## Getting Started

**New to this? Start here:**

1. Read [QUICK_START.md](QUICK_START.md) (5 minute overview)
2. Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) step-by-step
3. Reference [GOOGLE_SHEET_FORMAT.md](GOOGLE_SHEET_FORMAT.md) for your data

**Ready to deploy?**

```bash
# Local test
pip install -r requirements.txt
streamlit run app.py

# Push to GitHub and deploy to Streamlit Cloud
```

---

**Made with ❤️ for families**

🌳 *Connect, explore, and celebrate your family tree!*
