# 4:20 Goal Tracker

A Raspberry Pi-based service that monitors NHL games and notifies your fantasy hockey league whenever a goal is scored at exactly 4:20 remaining in any period.

## Overview

This application runs daily at 10 AM (configurable via cron), checks all NHL games from the previous day, and alerts your league via Telegram whenever a 4:20 goal is detected.

## Features

- Fetches game data from the free NHL public API
- Detects goals scored at exactly 4:20 in any period
- Sends notifications via Telegram (Discord and Email also supported)
- Pluggable notifier architecture - easy to swap notification methods
- Designed to run on Raspberry Pi

## Requirements

- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (or any Linux distribution)
- Python 3.7+
- Internet connection
- Telegram account (for bot creation)

## Quick Start

### 1. Clone or Copy the Project

```bash
mkdir -p ~/hockey-420-tracker
cd ~/hockey-420-tracker
# Copy all project files here
```

### 2. Create Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot` to create a new bot
3. Follow the prompts to name your bot (e.g., "Hockey420Bot")
4. BotFather will give you a token (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. **Save this token** - you'll need it for configuration

### 3. Get Your Telegram Chat ID

1. Add your bot to a Telegram group (your league chat)
2. Send any message to the group
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Look for `"chat":{"id":-XXXXXXXX` in the JSON response
5. The negative number is your group chat ID (include the negative sign!)

### 4. Configure the Application

Create a `.env` file in the project directory:

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your settings:

```bash
# Telegram Configuration (required for Telegram notifications)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=-123456789

# Notifier type: telegram, discord, or email
NOTIFIER_TYPE=telegram

# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

### 5. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 6. Test the Application

```bash
python3 main.py
```

You should receive a Telegram message (or see console output) with the results.

## Switching Notification Methods

### Discord

1. Create a Discord webhook in your server settings
2. Update your `.env` file:

```bash
NOTIFIER_TYPE=discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
```

### Email

1. Update your `.env` file with your SMTP settings:

```bash
NOTIFIER_TYPE=email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=friend1@example.com,friend2@example.com
```

## Setting Up the Daily Cron Job

### Option 1: Using Crontab

```bash
# Edit crontab
crontab -e

# Add this line to run at 10 AM daily:
0 10 * * * cd /home/pi/hockey-420-tracker && /usr/bin/python3 /home/pi/hockey-420-tracker/main.py >> /home/pi/hockey-420-tracker.log 2>&1
```

### Option 2: Using Systemd (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/hockey-420-tracker.service
```

Add the following content:

```ini
[Unit]
Description=4:20 Goal Tracker
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/hockey-420-tracker
ExecStart=/usr/bin/python3 /home/pi/hockey-420-tracker/main.py
StandardOutput=append:/home/pi/hockey-420-tracker.log
StandardError=append:/home/pi/hockey-420-tracker.log

[Install]
WantedBy=multi-user.target
```

Create a timer to run daily at 10 AM:

```bash
sudo nano /etc/systemd/system/hockey-420-tracker.timer
```

Add the following content:

```ini
[Unit]
Description=Run 4:20 Goal Tracker daily at 10 AM

[Timer]
OnCalendar=*-*-* 10:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable hockey-420-tracker.timer
sudo systemctl start hockey-420-tracker.timer
```

Check status:

```bash
sudo systemctl status hockey-420-tracker.timer
```

## Viewing Logs

```bash
# View application logs
cat ~/hockey-420-tracker.log

# Follow logs in real-time
tail -f ~/hockey-420-tracker.log

# View systemd logs (if using systemd)
journalctl -u hockey-420-tracker -f
```

## Troubleshooting

### No games found

- Check that the NHL API is accessible: `curl https://api-web.nhle.com/v1/schedule`
- Verify the date calculation is correct

### Telegram notification not sending

- Verify bot token is correct
- Make sure the bot is added to the group
- Check the chat ID is correct (must be negative for groups)
- Test with: `curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates"`

### Cron job not running

- Check cron is enabled: `sudo systemctl status cron`
- Verify the cron entry: `crontab -l`
- Check system logs: `sudo journalctl -u cron`

## Project Structure

```
hockey-420-tracker/
├── config.py              # Configuration settings
├── nhl_client.py          # NHL API client
├── goal_detector.py       # 4:20 goal detection logic
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Example configuration file
├── README.md              # This file
└── notifiers/
    ├── __init__.py        # Notifier factory
    ├── base.py            # Abstract notifier class
    ├── telegram.py        # Telegram implementation
    ├── discord.py         # Discord implementation
    └── email.py           # Email implementation
```

## NHL API Reference

- Schedule endpoint: `GET https://api-web.nhle.com/v1/schedule/{date}`
- Play-by-play endpoint: `GET https://api-web.nhle.com/v1/game/{game_id}/play-by-play`
- Date format: YYYY-MM-DD

## License

MIT