# Secure Crypto Chat (NetCipher Suite)

    ![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
    ![Python](https://img.shields.io/badge/python-3.14%2B-brightgreen.svg)
    ![License](https://img.shields.io/badge/license-MIT-orange.svg)

    A comprehensive, multi-threaded client-server chat application designed to demonstrate both classical cryptography and modern secure communication concepts. Featuring a custom Master Control Panel, real-time network sniffing, and a dynamic Vue.js frontend.

    ---

    ## 🌟 Key Features

    * **Master Control Panel (GUI):** A dark-themed, tabbed control panel built with `customtkinter` to manage all microservices centrally without juggling multiple terminal windows.
    * **Multi-Layered Cryptography:**
        * **Classical Modes:** Caesar Cipher and Vigenère Cipher implementations.
        * **Modern Simulation:** SSL/TLS-style communication mode.
    * **Real-Time Network Sniffer:** Intercepts and visualizes local loopback traffic using `scapy`, demonstrating MITM (Man-In-The-Middle) visibility of encrypted vs. unencrypted payloads.
    * **WebSocket Bridge:** Seamless bidirectional communication between the asynchronous Python backend and the Vue.js frontend.
    * **Auto-Discovery Web Server:** A custom multi-threaded HTTP server that dynamically resolves LAN IP addresses and serves the frontend seamlessly without CORS or MIME-type registry issues.

    ---

    ## 🏗️ System Architecture

    The project is built on a robust microservices-inspired architecture, managed entirely by the `launcher_ui.py` core:

    1.  **Server (`server.py`):** The backbone handling TCP connections and encryption routing.
    2.  **Bridge (`bridge.py`):** Translates standard TCP socket data to WebSockets for the browser.
    3.  **Sniffer (`sniffer.py`):** Monitors port 5050 and broadcasts intercepted packet payloads.
    4.  **Web Server (`web_server.py`):** Serves the UI and provides API endpoints for auto-configuration.
    5.  **Frontend (`app.js`):** Reactive Vue 3 interface with Tailwind CSS styling.

    ---

    ## 🚀 Installation & Setup

    ### Prerequisites
    * **Python 3.14** (or compatible 3.x version)
    * Windows OS (Required for specific loopback sniffing configurations)
    * Administrator Privileges (Required for `scapy` network capture)

    ### Step 1: Clone the Repository
    ```bash
    git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
    cd YOUR-REPO-NAME

    ```

    ### Step 2: Install Dependencies

    It is highly recommended to use a virtual environment (`.venv`).

    ```bash
    pip install -r requirements.txt

    ```

    ### Step 3: Launch the Suite

    To ensure the network sniffer functions correctly, you **must** run the launcher with Administrator privileges. Open an elevated terminal (Run as Administrator) and execute:

    ```bash
    python launcher_ui.py

    ```

    ---

    ## 💻 Usage Guide

    1. Once the Master Control Panel opens, click the orange **🚀 START ALL** button.
    2. The system will sequentially boot the Server, Bridge, Sniffer, and Web Server.
    3. Your default web browser will automatically open `http://localhost:8000`.
    4. The server's IP address is auto-discovered and pre-filled. Enter a username, select your desired encryption layer, and connect to the chat room.
    5. Monitor the isolated terminal tabs in the Control Panel for live logging and background processes.
    6. To gracefully shut down and release all network ports, click **🛑 STOP ALL** or close the Control Panel window.

    ---

    ## ⚠️ Disclaimer

    This project was developed for educational purposes, specifically for university assignments regarding data transfer and classical cryptography. The SSL/TLS mode is a simulation for conceptual understanding and should not be used for actual sensitive data transmission.
    