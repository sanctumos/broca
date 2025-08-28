"""
Web Chat Plugin for Broca2

This plugin polls a PHP-based web chat API and processes messages through the Broca2 agent system.
It follows the pull-based architecture where the plugin polls for new messages and posts responses back.
"""

from plugins.web_chat.plugin import WebChatPlugin
from plugins.web_chat.settings import WebChatSettings

__all__ = ['WebChatPlugin', 'WebChatSettings'] 