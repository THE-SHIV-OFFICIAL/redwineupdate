"""Telegram HTML captions used by the modern welcome screen.

Telegram renders the keyboard separately from the caption.  Keeping the
buttons in an InlineKeyboardMarkup (rather than embedding unsupported custom
HTML button tags) makes this work in current Telegram clients and Bot API
versions.
"""

from html import escape

import config


def build_welcome_html(user_mention: str, bot_mention: str, bot_username: str) -> str:
    support_link = getattr(config, "SUPPORT_CHAT", "https://t.me/theshiv_support")
    update_link = getattr(config, "SUPPORT_CHANNEL", "https://t.me/theshiv_updates")
    username = escape(str(bot_username).lstrip("@"), quote=True)

    return (
        f"💐 <b>Greetings, {user_mention}!</b> 🥀\n\n"
        f"💮 <b>This is {bot_mention} ✨ — your high-quality music streaming companion.</b>\n\n"
        "<b>🎧 Modern music player with inline controls</b>\n"
        "<b>🤖 YouTube, Spotify, Apple Music and Telegram support</b>\n"
        "<b>🎚 EQ presets, volume controls and smooth playback</b>\n\n"
        "<blockquote expandable><b>Bot Information</b>\n\n"
        "<b>Audio</b> · Dolby-style streaming\n"
        "<b>Player</b> · Inline controls\n"
        "<b>Equalizer</b> · 13 presets\n"
        "<b>Active</b> · 24x7</blockquote>\n\n"
        "<blockquote>🎋 Tap Help to see all available commands.</blockquote>\n\n"
        f'<a href="https://t.me/{username}?startgroup=true">➕ ADD ME TO YOUR GROUP</a>\n'
        f'<a href="{escape(str(support_link), quote=True)}">🛟 SUPPORT</a> · '
        f'<a href="{escape(str(update_link), quote=True)}">⭐ UPDATES</a>'
    )