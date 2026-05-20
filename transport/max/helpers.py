"""
MAX-specific message helpers.
Handles message splitting, formatting, and sending utilities.
"""

import logging
from typing import Optional
from maxapi import Bot
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


def set_max_message_length(length: int) -> None:
    global MAX_MESSAGE_LENGTH
    MAX_MESSAGE_LENGTH = length


async def send_long_message(
    bot: Bot,
    user_id: int,
    text: str,
    attachments: Optional[list] = None,
) -> None:
    """Send a message, splitting it into chunks if it exceeds MAX length."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        await bot.send_message(user_id=user_id, text=text, attachments=attachments)
        return

    chunks = _split_text(text, MAX_MESSAGE_LENGTH)
    for i, chunk in enumerate(chunks):
        atts = attachments if i == len(chunks) - 1 else None
        await bot.send_message(user_id=user_id, text=chunk, attachments=atts)


async def send_with_keyboard(
    bot: Bot,
    user_id: int,
    text: str,
    keyboard: InlineKeyboardBuilder,
) -> None:
    """Send a message with an inline keyboard."""
    await bot.send_message(
        user_id=user_id,
        text=text,
        attachments=[keyboard.as_markup()],
    )


def _split_text(text: str, max_length: int) -> list[str]:
    """Split text into chunks at newline boundaries when possible."""
    chunks = []
    while len(text) > max_length:
        split_pos = text.rfind("\n", 0, max_length)
        if split_pos <= 0:
            split_pos = max_length
        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks
