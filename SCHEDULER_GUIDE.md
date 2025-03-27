# Python Scheduler for Wallet Monitor

This guide explains how to use the Python scheduler to run the wallet monitor script at regular intervals.

## Overview

The Python scheduler (`scheduler.py`) is an alternative to system crontab and provides:

- Continuous operation with configurable intervals
- Built-in logging
- Immediate feedback
- Cross-platform support

## Basic Usage

Run the scheduler with the default 2-hour interval:

```bash
python scheduler.py
```

This will start the scheduler, which will run the wallet monitor every 2 hours.

## Running the Monitor Immediately

To run the wallet monitor immediately and then follow the regular schedule:

```bash
python scheduler.py --run-now
```

## Customizing the Interval

To change the interval from the default 2 hours:

```bash
python scheduler.py --interval 60  # Run every 60 minutes
```

## Running as a Background Service

### On Linux/macOS with systemd

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/wallet-monitor.service
```

2. Add the following content:

```
[Unit]
Description=Wallet Monitor Scheduler
After=network.target

[Service]
User=<your-username>
WorkingDirectory=/full/path/to/wallet-monitoring
ExecStart=/full/path/to/wallet-monitoring/venv/bin/python scheduler.py --run-now
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Replace `<your-username>` and `/full/path/to/wallet-monitoring` with your actual username and path.

4. Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start wallet-monitor
sudo systemctl enable wallet-monitor
```

### On macOS with launchd

1. Create a LaunchAgent plist file:

```bash
nano ~/Library/LaunchAgents/com.user.wallet-monitor.plist
```

2. Add the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.wallet-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/full/path/to/wallet-monitoring/venv/bin/python</string>
        <string>/full/path/to/wallet-monitoring/scheduler.py</string>
        <string>--run-now</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/full/path/to/wallet-monitoring</string>
    <key>StandardErrorPath</key>
    <string>/full/path/to/wallet-monitoring/scheduler-error.log</string>
    <key>StandardOutPath</key>
    <string>/full/path/to/wallet-monitoring/scheduler-output.log</string>
</dict>
</plist>
```

3. Replace `/full/path/to/wallet-monitoring` with your actual path.

4. Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.user.wallet-monitor.plist
```

## Troubleshooting

- Check the `scheduler.log` file for error messages
- Make sure your virtual environment is properly set up
- Verify permissions on the script files
- If using a service, check system logs:
  - `journalctl -u wallet-monitor.service` (for systemd)
  - `cat scheduler-error.log` (for launchd) 