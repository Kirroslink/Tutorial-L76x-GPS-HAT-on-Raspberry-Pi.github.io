# Guide: Hosting a Simple Markdown Wiki on Your Raspberry Pi

This guide will walk you through setting up a lightweight, file-based wiki on your Raspberry Pi. The wiki runs from a single Python script using the Flask framework, making it very easy to manage.

---

### Part 1: Setup and Dependencies

1.  **Open a terminal** on your Raspberry Pi and navigate to the directory where `pi_wiki.py` is located.

2.  **Create a virtual environment.** This creates a folder named `venv` that will hold your project's libraries. You only need to do this once.
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment.** You must do this every time you open a new terminal to work on the project.
    ```bash
    source venv/bin/activate
    ```
    Your prompt will change to show `(venv)`.

4.  **Install the required libraries.** With the environment active, use `pip` to install Flask and Markdown. They will be installed inside the `venv` folder, not globally.
    ```bash
    pip install Flask markdown
    ```

---

### Part 2: The Python Script

The script `pi_wiki.py` has been created for you. It contains everything needed to run the wiki.

*   **How it Works:** The script is a small web server. When you access it from a browser, it reads Markdown files (`.md`) from a folder named `wiki_pages`, converts them to HTML on-the-fly, and displays them. It also provides a web interface for creating and editing these files.
*   **File-Based:** Every page on your wiki is a simple text file in the `wiki_pages` folder. This makes it incredibly easy to backup or manually edit your content.

---

### Part 3: Running the Wiki

1.  **Find Your Pi's IP Address:** You will need this to connect from another computer. Run this command in the terminal:
    ```bash
    hostname -I
    ```
    Your IP address is the first set of numbers that appears (e.g., `192.168.1.35`).

2.  **Run the Script:**
    *   Navigate to the directory where `pi_wiki.py` is saved.
    *   **Activate the environment** (if you haven't already):
        ```bash
        source venv/bin/activate
        ```
    *   Execute the script:
        ```bash
        python pi_wiki.py
        ```

3.  **Access Your Wiki:**
    *   On another computer on the same network, open a web browser.
    *   Go to the following address, replacing `<your_pi_ip>` with the address you found in step 1:
        ```
        http://<your_pi_ip>:8080
        ```
    *   You should see the "Welcome to your Pi Wiki!" homepage.

---

### Part 4: Using Your New Wiki

*   **Editing Pages:** Click the "Edit this page" link. This will open a text box with the raw Markdown content. Make your changes and click "Save Page".
*   **Creating New Pages:** The easiest way to create a new page is to type its name in the browser's address bar. For example, to create a page called "Shopping_List", navigate to:
    ```
    http://<your_pi_ip>:8080/view/Shopping_List
    ```
    Since the page doesn't exist, you will be taken directly to the edit screen. Write your content, save it, and the page will be created.

---

### Part 5: (Recommended) Run the Wiki as a Service

Running the script from the terminal is fine for testing, but if you want your wiki to always be available (even after a reboot), you should run it as a `systemd` service.

1.  **Create a Service File:**
    *   Use `nano` to create a new service file.
        ```bash
        sudo nano /etc/systemd/system/pi-wiki.service
        ```

2.  **Paste the following content.** **You must change the `User` and the paths to match your setup.**
    *   Find your username with `whoami`.
    *   Find your project's absolute path with `pwd` (run this in the same folder as `pi_wiki.py`).

    ```ini
    [Unit]
    Description=Pi Wiki Server
    After=network.target

    [Service]
    User=YOUR_USERNAME
    WorkingDirectory=/home/YOUR_USERNAME/path/to/your/project
    ExecStart=/home/YOUR_USERNAME/path/to/your/project/venv/bin/python /home/YOUR_USERNAME/path/to/your/project/pi_wiki.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    **CRITICAL:** The `ExecStart` path must point to the `python` executable **inside your venv folder**.

3.  **Enable and Start the Service:**
    *   Reload the systemd daemon to recognize the new file:
        ```bash
        sudo systemctl daemon-reload
        ```
    *   Enable the service to start automatically on boot:
        ```bash
        sudo systemctl enable pi-wiki.service
        ```
    *   Start the service immediately:
        ```bash
        sudo systemctl start pi-wiki.service
        ```

Your wiki is now running as a background service. You can check its status anytime with `sudo systemctl status pi-wiki.service`.
