# Full Tutorial: Tailscale PC & Raspberry Pi Setup with Subnet Routing

This tutorial provides a complete guide to installing Tailscale on a Windows PC and a Raspberry Pi, creating a secure private network, and then configuring the PC as a subnet router to access its entire local network from the Pi.

---

## Part 1: What is Tailscale?

Tailscale is a zero-configuration Virtual Private Network (VPN). It creates a secure, private network (a "tailnet") between your devices, no matter where they are. Each device gets a private `100.x.y.z` IP address, and all traffic between them is encrypted. This is perfect for securely accessing your Raspberry Pi from anywhere or connecting to your home network remotely.

---

## Part 2: Setup on PC (Windows)

1.  **Download:** Go to the [Tailscale Download Page](https://tailscale.com/download/) and get the installer for Windows.
2.  **Install:** Run the downloaded `.exe` file. Follow the simple on-screen prompts.
3.  **Log In:** Once installed, find the Tailscale icon in your system tray (you may need to click the arrow to show hidden icons). Click the icon and select "Log in".
4.  **Authenticate:** Your web browser will open. Log in with a Google, Microsoft, GitHub, or other account. This account will be used to manage all the devices in your tailnet.

Your PC is now connected to your tailnet!

---

## Part 3: Setup on Raspberry Pi

1.  **Add Tailscale's Repository:** Open a terminal on your Raspberry Pi and run the following two commands to add Tailscale's package repository and its security key.
    ```bash
    curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.gpg | sudo apt-key add -
    curl -fsSL https://pkgs.tailscale.com/stable/raspbian/buster.list | sudo tee /etc/apt/sources.list.d/tailscale.list
    ```
2.  **Install Tailscale:** Update your package list and install Tailscale.
    ```bash
    sudo apt update
    sudo apt install tailscale -y
    ```
3.  **Connect and Authenticate:** Start Tailscale with the `up` command.
    ```bash
    sudo tailscale up
    ```
4.  **Log In:** The command will print a URL in your terminal. Copy this URL and paste it into a web browser on any device (your PC or phone). You will be asked to log in to the same Tailscale account you used for your PC. After logging in, approve the connection for the new Raspberry Pi.

Your Raspberry Pi is now connected to your tailnet!

---

## Part 4: Verifying the Basic Connection

1.  **Check the Admin Console:** Open the [Tailscale Admin Console](https://login.tailscale.com/admin/machines) in your browser. You should see both your PC and your Raspberry Pi listed, each with a `100.x.y.z` IP address. Note the IP address of your PC.
2.  **Ping from the Pi:** On your Raspberry Pi terminal, ping your PC using its Tailscale IP address.
    ```bash
    # Replace 100.x.y.z with your PC's Tailscale IP
    ping 100.x.y.z
    ```
If you see replies, your secure network is working perfectly.

---

## Part 5: Configuring the PC as a Subnet Router

This is the advanced part. We will make the PC act as a gateway, allowing the Raspberry Pi to access other devices on the PC's local home network (like a printer, NAS, or another computer).

### Step 5a: Find Your PC's Local Subnet

On your Windows PC, open a **Command Prompt** (not PowerShell for this step) and type `ipconfig`. Look for your main network adapter (usually "Ethernet" or "Wi-Fi"). Note the `IPv4 Address` and `Subnet Mask`.

*   If your IP is `192.168.1.50` and your subnet mask is `255.255.255.0`, your subnet is **`192.168.1.0/24`**.
*   If your IP is `192.168.4.25` and your subnet mask is `255.255.255.0`, your subnet is **`192.168.4.0/24`**.
*   If your IP is `10.0.0.30` and your subnet mask is `255.255.255.0`, your subnet is **`10.0.0.0/24`**.

You will need this subnet address (e.g., `192.168.1.0/24`) for the next steps.

### Step 5b: Enable IP Forwarding on Windows

For your PC to be able to route packets from the Tailscale network to your local LAN, you must enable IP forwarding at the OS level.

1.  **Open PowerShell as Administrator:** Right-click the Start button and select "PowerShell (Admin)".
2.  **Find your Network Adapter Name:** Run this command to see your network interfaces.
    ```powershell
    Get-NetIPInterface | Select-Object InterfaceAlias, Forwarding
    ```
    Note the `InterfaceAlias` for your main network (e.g., "Ethernet" or "Wi-Fi").
3.  **Enable Forwarding:** Run the following command, replacing `<Adapter Name>` with the alias you just found.
    ```powershell
    # Example: Set-NetIPInterface -InterfaceAlias "Ethernet" -Forwarding Enabled
    Set-NetIPInterface -InterfaceAlias "<Adapter Name>" -Forwarding Enabled
    ```

### Step 5c: Advertise the Route from your PC

Now, tell Tailscale that your PC is willing to be a router for your local subnet.

1.  **Open Command Prompt as Administrator.**
2.  Run the `tailscale up` command, adding the `--advertise-routes` flag with the subnet you found in Step 5a.
    ```bash
    # Replace 192.168.1.0/24 with your actual subnet
    tailscale up --advertise-routes=192.168.1.0/24
    ```

### Step 5d: Approve the Route in the Admin Console

For security, you must approve the new subnet route.

1.  Go back to the [Machines page](https://login.tailscale.com/admin/machines) in your Tailscale admin console.
2.  Find your PC in the list. You should see a new badge indicating it's advertising a route.
3.  Click the three-dot menu (`...`) next to your PC and select **"Edit route settings..."**.
4.  A side panel will appear. **Click the switch** to approve your subnet route.

---

## Part 6: Testing the Subnet Route

The final test is to access a device on your PC's local network *from* your Raspberry Pi. A great target is your home router's admin page, which is usually the "Default Gateway" address from the `ipconfig` command (e.g., `192.168.1.1`).

From your Raspberry Pi's terminal, ping your home router's IP address:
```bash
# Replace 192.168.1.1 with your home router's IP address
ping 192.168.1.1
```

If you get replies, it works! Your Raspberry Pi, from anywhere in the world, can now securely access any device on your PC's local network using its private IP address.
