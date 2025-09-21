# Streamlit Deployment Guide
# Enhanced Resume Relevance System

## 📋 For Streamlit Cloud Deployment

### Main File Path
**Required main file:** `streamlit_app.py`

This is the **entry point** that Streamlit Cloud looks for automatically. No additional configuration needed.

### 🚀 Deployment Steps

#### Option 1: Streamlit Community Cloud (Recommended)
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Streamlit deployment files"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select repository: `vivekkumar2004-coder-code/advanceResumeTracking`
   - **Main file path:** `streamlit_app.py`
   - Click "Deploy"

#### Option 2: Local Testing
```bash
# Install Streamlit requirements
pip install -r requirements_streamlit.txt

# Run locally
streamlit run streamlit_app.py
```

### 📁 Required Files for Deployment

#### ✅ Essential Files (Must be in root directory):
- `streamlit_app.py` - **Main application file**
- `requirements_streamlit.txt` - Dependencies
- `.streamlit/config.toml` - Configuration
- `app/` - Your existing application utilities

#### ✅ Current File Structure:
```
automated-resume-relevance-system/
├── streamlit_app.py              ← MAIN FILE (Entry point)
├── requirements_streamlit.txt     ← Dependencies
├── .streamlit/
│   └── config.toml               ← Configuration
├── app/
│   ├── utils/
│   │   ├── resume_parser.py
│   │   ├── relevance_analyzer.py
│   │   ├── file_handler.py
│   │   └── keyword_extractor.py
│   └── ...
├── uploads/                      ← Will be created automatically
└── ...
```

### ⚙️ Streamlit App Features

#### 🎯 Three Analysis Modes:
1. **Standard Analysis** - Traditional single job + multiple resumes
2. **Dual Upload Analysis** - Multiple jobs × multiple resumes matrix
3. **Batch Processing** - Automatic file categorization and processing

#### 🎨 Professional UI:
- Deep blue (#1e3a8a) primary colors
- Soft gold (#d97706) warning elements
- Emerald green (#059669) success states
- Responsive design
- Interactive progress tracking

#### 📊 Advanced Features:
- Cross-analysis matrix visualization
- Real-time processing progress
- Professional result cards with score badges
- Skill matching with visual tags
- Summary statistics and metrics

### 🔧 Configuration Options

#### Streamlit Cloud Settings:
- **Repository:** `vivekkumar2004-coder-code/advanceResumeTracking`
- **Branch:** `main`
- **Main file path:** `streamlit_app.py`
- **Python version:** 3.11 (recommended)

#### Environment Variables (Optional):
```
# Add these in Streamlit Cloud secrets if needed
UPLOAD_FOLDER = "uploads"
MAX_UPLOAD_SIZE = "200MB"
```

### 🚨 Important Notes

#### File Upload Limits:
- Streamlit Cloud: 200MB per file
- Local development: No specific limit
- Adjust in `.streamlit/config.toml` if needed

#### Dependencies:
- Core features work with minimal dependencies
- ML features gracefully degrade if transformers/torch unavailable
- Automatic fallback to simple keyword matching

#### Data Storage:
- Files stored temporarily during session
- No persistent storage on Streamlit Cloud
- Results displayed immediately and not saved

### 🧪 Testing Your Deployment

#### Local Testing:
```bash
# Test the Streamlit app locally
streamlit run streamlit_app.py

# Check if all imports work
python -c "import streamlit_app; print('All imports successful!')"
```

#### Production Checklist:
- ✅ `streamlit_app.py` in root directory
- ✅ `requirements_streamlit.txt` present
- ✅ `.streamlit/config.toml` configured
- ✅ All utility files in `app/utils/` directory
- ✅ GitHub repository updated
- ✅ No hardcoded file paths

### 📈 Expected Performance

#### Processing Speed:
- Standard mode: 1-2 seconds per resume
- Dual mode: Linear scaling with file count
- Batch mode: Optimized for multiple files

#### Scalability:
- Handles 10+ resumes efficiently
- Cross-analysis up to 5×10 matrix recommended
- Progress tracking for long operations

### 🎯 Deployment URL

Once deployed, your app will be available at:
```
https://[your-app-name].streamlit.app
```

### 📞 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all files are in repository
3. Test locally first with `streamlit run streamlit_app.py`
4. Ensure `streamlit_app.py` is in root directory

---

**🚀 Ready for deployment!** Your enhanced Resume Relevance System is now Streamlit-compatible with all dual upload features preserved.