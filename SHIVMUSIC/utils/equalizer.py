"""
🎚 Equalizer / Audio-Effect engine for SHIVMUSIC.

Each preset is a plain ffmpeg audio-filter chain (no spaces!) which is passed
to pytgcalls through MediaStream(ffmpeg_parameters="-af <chain>").
"""

# key: (button name, ffmpeg -af chain)
EQ_PRESETS = {
    "off":      ("ɴᴏʀᴍᴀʟ",      ""),
    "clear":    ("ᴄʟᴇᴀʀ ᴀᴜᴅɪᴏ",  "highpass=f=60,equalizer=f=1000:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1:g=4,dynaudnorm=f=200"),
    "dj":       ("ᴅᴊ ʙᴀss",      "bass=g=12:f=70:w=0.6,treble=g=4,acompressor=ratio=3,dynaudnorm=f=150"),
    "bass":     ("ʙᴀss ʙᴏᴏsᴛ",   "bass=g=9:f=90:w=0.5"),
    "deep":     ("ᴅᴇᴇᴘ ʙᴀss",    "bass=g=15:f=55:w=0.7,lowpass=f=12000"),
    "8d":       ("8ᴅ ᴀᴜᴅɪᴏ",     "apulsator=hz=0.09,stereotools=mlev=0.05,bass=g=4"),
    "lofi":     ("ʟᴏ-ғɪ",        "highpass=f=200,lowpass=f=3500,acompressor=ratio=4,aecho=0.8:0.85:60:0.25"),
    "vocal":    ("ᴠᴏᴄᴀʟ",        "highpass=f=120,equalizer=f=2500:t=q:w=2:g=6,dynaudnorm=f=200"),
    "treble":   ("ᴛʀᴇʙʟᴇ",       "treble=g=10:f=4000"),
    "soft":     ("sᴏғᴛ",         "volume=0.8,lowpass=f=8000"),
    "party":    ("ᴘᴀʀᴛʏ",        "bass=g=8,treble=g=6,extrastereo=m=2.0,dynaudnorm=f=150"),
    "nightcore":("ɴɪɢʜᴛᴄᴏʀᴇ",    "asetrate=48000*1.25,aresample=48000,atempo=1.0"),
    "slowed":   ("sʟᴏᴡᴇᴅ+ʀᴇᴠᴇʀʙ","asetrate=48000*0.85,aresample=48000,aecho=0.8:0.88:60:0.4"),
}

# chat_id -> preset key
EQ_STATE = {}

# chat_id -> volume percentage. 100 is the normal level, 1000 is the
# requested hard ceiling for the in-chat volume controls.
VOLUME_STATE = {}
MIN_VOLUME = 0
DEFAULT_VOLUME = 100
MAX_VOLUME = 1000


def get_eq_filter(preset: str) -> str:
    data = EQ_PRESETS.get(str(preset))
    return data[1] if data else ""


def get_eq_name(preset: str) -> str:
    data = EQ_PRESETS.get(str(preset))
    return data[0] if data else EQ_PRESETS["off"][0]


def get_chat_eq(chat_id) -> str:
    try:
        chat_id = int(chat_id)
    except Exception:
        pass
    return EQ_STATE.get(chat_id, "off")


def get_chat_eq_filter(chat_id) -> str:
    return get_eq_filter(get_chat_eq(chat_id))


def set_chat_eq(chat_id, preset: str):
    try:
        chat_id = int(chat_id)
    except Exception:
        pass
    if str(preset) == "off":
        EQ_STATE.pop(chat_id, None)
    else:
        EQ_STATE[chat_id] = str(preset)


def clear_chat_eq(chat_id):
    set_chat_eq(chat_id, "off")


def get_chat_volume(chat_id) -> int:
    try:
        chat_id = int(chat_id)
    except Exception:
        pass
    try:
        return max(MIN_VOLUME, min(MAX_VOLUME, int(VOLUME_STATE.get(chat_id, DEFAULT_VOLUME))))
    except (TypeError, ValueError):
        return DEFAULT_VOLUME


def set_chat_volume(chat_id, volume: int):
    try:
        chat_id = int(chat_id)
    except Exception:
        pass
    try:
        volume = int(volume)
    except (TypeError, ValueError):
        volume = DEFAULT_VOLUME
    VOLUME_STATE[chat_id] = max(MIN_VOLUME, min(MAX_VOLUME, volume))


def get_chat_volume_filter(chat_id) -> str:
    """Return an ffmpeg scalar volume filter for the current chat level."""
    volume = get_chat_volume(chat_id)
    if volume == DEFAULT_VOLUME:
        return ""
    return f"volume={volume / DEFAULT_VOLUME:.2f}"


def equalizer_markup(_, chat_id):
    """Inline keyboard listing all presets (2 per row)."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    current = get_chat_eq(chat_id)
    rows, row = [], []
    for key, (name, _filter) in EQ_PRESETS.items():
        label = f"✅ {name}" if key == current else name
        row.append(InlineKeyboardButton(text=label, callback_data=f"EqSet {chat_id}|{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [
            InlineKeyboardButton(
                text=f"🔊 ᴠᴏʟᴜᴍᴇ · {get_chat_volume(chat_id)}%",
                callback_data=f"VolumePanel {chat_id}",
            )
        ]
    )
    rows.append([InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")])
    return InlineKeyboardMarkup(rows)


def volume_markup(_, chat_id):
    """Volume controls shown after clicking the volume row in the EQ panel."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    volume = get_chat_volume(chat_id)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔊 ᴠᴏʟ +50",
                    callback_data=f"VolumeSet {chat_id}|up",
                ),
                InlineKeyboardButton(
                    text="🔉 ᴠᴏʟ -25",
                    callback_data=f"VolumeSet {chat_id}|down",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"⚡ ʙᴏᴏsᴛ +500 · {volume}%",
                    callback_data=f"VolumeSet {chat_id}|boost",
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ ʙᴀᴄᴋ ᴛᴏ ᴇǫ",
                    callback_data=f"VolumeBack {chat_id}",
                )
            ],
            [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")],
        ]
    )
