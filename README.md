# Telegram Dorking Bot

This is a Telegram bot designed to generate Google/DuckDuckGo dorks based on categories or custom input. It supports admin-controlled updates, user favorites, and search engine switching.

## Features

- Category-based dork generation (e.g., Admin Panels, File Leaks, Indexes)
- Custom dork generator (e.g., domain + keyword + filetype)
- Google or DuckDuckGo search engine support
- Save and list favorite dorks
- Admin command to update dork lists

## How to Run

1. **Install dependencies**:
   ```bash
   pip install pyTelegramBotAPI
   ```

2. **Configure bot**:
   - Replace `'YOUR_BOT_TOKEN_HERE'` with your actual Telegram bot token.
   - Replace `admin_id` with your Telegram numeric user ID.

3. **Run the bot**:
   ```bash
   python dork_bot.py
   ```

## Commands

| Command          | Description                           |
|------------------|---------------------------------------|
| /start           | Start interaction and choose dork     |
| /save            | Save last dork to favorites           |
| /mydorks         | Show saved dorks                      |
| /engine duck     | Use DuckDuckGo                        |
| /engine google   | Use Google                            |
| /updatedork      | Admin command to update category dorks|

## Example Custom Dork
```
example.com password txt
```
This generates:
```
site:example.com intext:"password" filetype:txt
```

## License
MIT License