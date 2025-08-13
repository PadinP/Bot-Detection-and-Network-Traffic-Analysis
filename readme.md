# Bot Detection and Capture Project

![Python](https://img.shields.io/badge/Python-blue) ![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## Description

This repository contains a system for **network traffic capture** and **bot detection** in a controlled environment.  
It includes:

- An API to manage capture and detection.
- A bot developed with Selenium to simulate web browsing.
- Auxiliary scripts to set up the environment and run the bots.

---

## Requirements

- **Python**
- **Wireshark**
- **Docker and Docker Compose**

---

## Installation and Setup

### 1. Install Firefox
```bash
sudo apt update
sudo apt install firefox
```

### 2. Install GeckoDriver (WebDriver for Firefox)
On Ubuntu:
```bash
sudo apt install firefox-geckodriver
```
Or download manually from: [GeckoDriver releases](https://github.com/mozilla/geckodriver/releases)  
and add the folder to your **PATH** so that Selenium can find it.

---

### 3. Create the virtual environment
```bash
python -m venv env
source env/bin/activate   # Linux / Mac
env\Scripts\activate    # Windows
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Start the environment with Docker Compose
```bash
docker-compose up
```

### 6. Configure the network interface
Go to the configuration folder:
```bash
cd app/config/
```
Open the `settings.py` file and edit the line:
```python
NETWORK_INTERFACE = "eth0"  # Change to your current interface (e.g. "wlan0")
```

---

## Running the Bots

The bot developed is very simple, created with the **Selenium** library.  
Its operation:

- Connects to the website generated in `sample-website`.
- Randomly navigates through product category pages.
- Retrieves prices and saves them in a `.json` file.
- Runs indefinitely, with random wait times between requests.

**Files:**

1. **`main.py`**  
   - Local bot, executed directly from the host machine (localhost IP).  
   - Useful for development testing.

2. **`remote-driver.py`**  
   - Bot connected to a **webdriver inside a Docker container**.  
   - Allows using different IPs for requests.

3. **`script.py`**  
   - Master script to run **all bots at once** (local and remote).  
   - Automates the startup of `main.py` and `remote-driver.py`.

**Run all bots at once:**
```bash
python script.py
```

---

## Start the API
Once the environment and bots are ready:
```bash
python main.py
```

---

## Logs

- **Capture:**  
  `capturas/logs/capture_bto_logs.log` → Events recorded during capture.

- **Detection:**  
  `capturas/logs/detection_bto_logs.log` → Events recorded during detection.
