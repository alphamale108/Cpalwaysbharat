from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_platform_keyboard():
    """Get inline keyboard for platform selection"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Utkarsh", callback_data="platform_utkarsh"),
            InlineKeyboardButton("Appx", callback_data="platform_appx")
        ],
        [
            InlineKeyboardButton("ClassPlus", callback_data="platform_classplus")
        ]
    ])

def get_admin_keyboard():
    """Get inline keyboard for admin commands"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Add User", callback_data="admin_add"),
            InlineKeyboardButton("Remove User", callback_data="admin_remove")
        ],
        [
            InlineKeyboardButton("View Logs", callback_data="admin_logs")
        ]
    ])
