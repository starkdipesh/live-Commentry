# 🔧 Simple Laptop Setup Guide (Saarthika)

**One Script. One Command. Your Strategic Shadow.**

---

## 🚀 Installation (Do this once)

1.  **Copy this folder** to your new laptop.
2.  **Run the automated setup:**
    ```bash
    chmod +x setup_complete.sh
    ./setup_complete.sh
    ```
3.  **Add your API Key:**
    ```bash
    nano .env
    # Paste: GROQ_API_KEY=your_key_here
    # Save: Ctrl+X, Y, Enter
    ```

---

## ⚡ START COMMAND (Use this daily)

```bash
./venv/bin/python3 main.py
```

**That's it.**

*   🎧 **Listens** via Microphone
*   📺 **Watches** Screen + Camera (Hidden)
*   🧠 **Thinks** via Groq Cloud
*   🗣️ **Speaks** via Neural Voice
*   💾 **Saves Data** to `training_data/gold_dataset/`

---

## 🛠️ Folder Structure (Cleaned Up)

*   `main.py` -> **The Heart.** Runs everything.
*   `src/core/` -> The Brain Logic.
*   `training_data/` -> Your collected RL Logs.
*   `.env` -> Your Secret Key.
*   `requirements.txt` -> Dependencies.

---

## ❓ Troubleshooting

*   **"Vision Error"**: If screen is black, switch Ubuntu to **Xorg** mode at login screen.
*   **"Mic Error"**: ensure `portaudio19-dev` is installed (`sudo apt install portaudio19-dev python3-pyaudio`).
*   **"No Response"**: Check internet validation in `diagnose.py`.

---

**Boss, the system is now simplified. Validated. And ready for deployment.** 🕉️


