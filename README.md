# 🏷️ Used Item Price Predictor (FR/AR)

An intelligent, bilingual web application that helps users quickly estimate the resale price of various used items—such as cars, phones, computers, watches, and cameras—in **Moroccan Dirhams (MAD)**.

---

## 🎯 Objective

The primary objective of this project is to provide a fast, accessible, and user-friendly tool to estimate the second-hand market value of everyday items. Whether you are buying or selling, this app gives you a pedagogical estimation based on the item's age, condition, brand, and category.

## ✨ What Makes It Special?

- **🧠 AI-Powered Estimations:** Integrates with Hugging Face's API (using the `Qwen2.5-72B-Instruct` model) to act as a Moroccan market expert and deliver realistic pricing based on item specifics.
- **📉 Smart Fallback System:** If the AI is unavailable, the app smoothly falls back to a custom heuristic depreciation model tailored to each item category.
- **🌍 Bilingual Interface:** The app natively supports both **French** and **Arabic**, making it widely accessible to users in Morocco and beyond.
- **🌗 Custom UI Themes:** Features a clean, CSS-based **Dark and Light mode** that users can toggle.
- **⚡ Lightweight:** Built purely on Python (Flask) and HTML/CSS. No complex JavaScript dependencies are required for the core experience.

---

## 🚀 How to Use the App

1. **Access the Application**: Open your web browser and go to the local URL (usually `http://127.0.0.1:5000`).
2. **Set Preferences**: At the top of the page, choose your preferred Language (Français / العربية) and Theme (Dark / Light), then click "Appliquer" (Apply).
3. **Select a Category**: Choose the type of item you want to evaluate (e.g., Car, Phone, Computer, Watch, Camera, or Other).
4. **Enter Details**: Fill in the form with the item's details:
   - **Brand** & **Model**
   - **Year** of purchase/manufacture
   - **Condition** (e.g., "Comme neuf", "Bon état", "Abîmé")
5. **Get Estimation**: Submit the form. The app will calculate and display the estimated price in **MAD**, along with a detailed summary.

> ⚠️ **Disclaimer:** This tool provides a rough, pedagogical estimation. It is not a professional appraisal.

---

## 🛠️ How to Make It (Installation & Setup)

### Prerequisites

- **Python 3.10+** installed on your system.
- **Git** (optional, for cloning the repository).
- A **Hugging Face API Key** (for the AI pricing feature).

### 1. Clone or Download the Project

Navigate to your desired folder and clone the repository:

```bash
git clone <repository_url>
cd app
```

*(If you don't use Git, simply download and extract the project files into a folder named `app`.)*

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages (Flask, huggingface_hub, etc.):

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

To enable the LLM AI pricing predictions, set your Hugging Face API key as an environment variable in your terminal:

**Windows (Command Prompt):**
```cmd
set HF_API_KEY=your_huggingface_token_here
```

**Windows (PowerShell):**
```powershell
$env:HF_API_KEY="your_huggingface_token_here"
```

**Linux / macOS:**
```bash
export HF_API_KEY="your_huggingface_token_here"
```

### 5. Run the Application

Start the Flask development server:

```bash
python app.py
```

The application will now be running at `http://127.0.0.1:5000`. 
To stop the server, press `Ctrl + C` in your terminal.

---

## 📂 Project Structure

```text
app/
├── app.py              # Backend Flask server, LLM integration & heuristic logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main HTML template (handles FR/AR UI & forms)
└── static/
    └── styles.css      # Custom CSS styles (Layout, Dark/Light mode)
```

## 🔧 Future Improvements

- Fully replace heuristics with fine-tuned ML models trained on real Moroccan classified ads.
- Add browser cookies/local storage to remember user language and theme preferences.
- Scrape or connect to live e-commerce APIs to fetch real-time market averages.
