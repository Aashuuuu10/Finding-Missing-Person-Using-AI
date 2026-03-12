## 🚀 Project Setup Guide

Follow the steps below to set up and run the project safely using a **Python virtual environment (venv)** so that system packages do not conflict with project dependencies.

---

## 1️⃣ Create and Activate Virtual Environment

### 🐧 Linux / macOS

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

### 🪟 Windows

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Command Prompt (CMD):**

```bash
venv\Scripts\activate
```

**PowerShell:**

```powershell
venv\Scripts\Activate.ps1
```

---

## 2️⃣ Install Project Dependencies

After activating the virtual environment, install the required packages:

```bash
pip install -r requirements.txt
```

---
Install Project Dependencies



## 3️⃣ Run the Applications

### ▶️ Main Web App

```bash
streamlit run Home.py
```

### 📱 Mobile / Public Submission App

```bash
streamlit run mobile_app.py
```

---

## ⚙️ Notes

* The SQLite database (`sqlite_database.db`) will be **automatically created** on first run.
* Uploaded images are stored inside the `resources/` folder.

---

## 🎯 Use Cases

* Law enforcement agencies reviewing large volumes of CCTV footage.
* NGOs and government organizations searching for missing persons or children.
* Public crowdsourced submissions through mobile or web applications.
