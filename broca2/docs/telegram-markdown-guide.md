# ⚠️ REPOSITORY MOVED ⚠️

**This repository has moved to: [http://github.com/sanctumos/broca](http://github.com/sanctumos/broca)**

Please update your git remotes and use the new repository location for all future development and contributions.

---

# Telegram Markdown Formatting Guide

## Overview

Telegram supports two types of text formatting:
1. **MarkdownV2** - The newer, more robust formatting system
2. **HTML** - Traditional HTML tags
3. **Plain text** - No formatting (current default in Broca)

This guide focuses on **MarkdownV2** as it's the recommended approach for modern Telegram bots and clients.

## MarkdownV2 Formatting

### Basic Text Formatting

| Format | Syntax | Example | Result |
|--------|--------|---------|--------|
| **Bold** | `*text*` | `*Hello World*` | **Hello World** |
| *Italic* | `_text_` | `_Hello World_` | *Hello World* |
| ~~Strikethrough~~ | `~text~` | `~Hello World~` | ~~Hello World~~ |
| `Monospace` | `` `text` `` | `` `Hello World` `` | `Monospace` |
| **Bold + Italic** | `*_text_*` | `*_Hello World_*` | **_Hello World_** |

### Special Characters Escaping

In MarkdownV2, the following characters must be escaped with a backslash (`\`):
```
_ * [ ] ( ) ~ ` > # + - = | { } . !
```

**Example:**
```markdown
# This will break: Hello *World*!
# This works: Hello \*World\!\*
```

### Links

| Type | Syntax | Example |
|------|--------|---------|
| **URL** | `[text](url)` | `[Visit Google](https://google.com)` |
| **User Mention** | `[text](tg://user?id=123456789)` | `[Contact Admin](tg://user?id=123456789)` |

### Code Blocks

| Type | Syntax | Example |
|------|--------|---------|
| **Inline Code** | `` `code` `` | `` `print("Hello")` `` |
| **Code Block** | ```` ```language\ncode\n``` ```` | ```` ```python\nprint("Hello")\n``` ```` |

### Lists

**Unordered Lists:**
```markdown
• Item 1
• Item 2
  • Subitem 2\.1
  • Subitem 2\.2
• Item 3
```

**Ordered Lists:**
```markdown
1\. First item
2\. Second item
3\. Third item
```

### Headers

Telegram doesn't support traditional markdown headers (`# ## ###`), but you can create visual headers:

```markdown
**Header 1**
*Header 2*
`Header 3`
```

### Blockquotes

```markdown
> This is a blockquote
> It can span multiple lines
> 
> And have paragraphs
```

### Tables

Telegram doesn't support markdown tables, but you can create table-like structures:

```markdown
**Name** | **Age** | **City**
John | 25 | New York
Jane | 30 | London
```

## Implementation in Broca

### Current Issue

The current `format_response()` method in `broca2/plugins/telegram/message_handler.py` calls `sanitize_text()` which removes all newlines and formatting:

```python
def format_response(self, response: str) -> str:
    """Format a response for Telegram."""
    # For now, just sanitize and return the response
    # In the future, we can add Telegram-specific formatting here
    return self.sanitize_text(response)  # ← This flattens markdown
```

### Recommended Solution

Replace the current `format_response()` method with a markdown-aware formatter:

```python
def format_response(self, response: str) -> str:
    """Format a response for Telegram with markdown support."""
    # Preserve markdown formatting instead of sanitizing
    return self.preserve_markdown(response)

def preserve_markdown(self, text: str) -> str:
    """Preserve markdown formatting while cleaning only problematic characters."""
    # Keep newlines and basic formatting
    # Only remove truly problematic characters
    return text
```

### Telegram Client Integration

To enable markdown formatting, the `send_message()` call needs to specify the parse mode:

```python
await self.client.send_message(
    telegram_user_id,
    formatted,
    parse_mode='MarkdownV2'  # Enable markdown parsing
)
```

## Markdown Conversion Examples

### From Letta/Broca Response to Telegram

**Input (from Letta):**
```markdown
# Welcome to the System

Here's what you can do:
- **Feature 1**: Description
- **Feature 2**: Description

Let me know if you need help!
```

**Current Output (flattened):**
```
# Welcome to the System Here's what you can do: - **Feature 1**: Description - **Feature 2**: Description Let me know if you need help!
```

**Desired Output (with markdown):**
```markdown
**Welcome to the System**

Here's what you can do:
• **Feature 1**: Description
• **Feature 2**: Description

Let me know if you need help\!
```

### Common Conversions

| Letta Format | Telegram MarkdownV2 |
|--------------|---------------------|
| `# Header` | `**Header**` |
| `## Header` | `*Header*` |
| `**Bold**` | `*Bold*` |
| `*Italic*` | `_Italic_` |
| `- Item` | `• Item` |
| `1. Item` | `1\. Item` |
| `[Link](url)` | `[Link](url)` |
| `\n\n` | `\n\n` (preserved) |

## Error Handling

### Invalid Markdown

If markdown parsing fails, Telegram will send the message as plain text. Always implement fallback:

```python
try:
    await self.client.send_message(
        telegram_user_id,
        formatted,
        parse_mode='MarkdownV2'
    )
except Exception as e:
    # Fallback to plain text
    await self.client.send_message(
        telegram_user_id,
        self.strip_markdown(formatted)
    )
```

### Character Limits

- **Message length**: 4096 characters
- **Caption length**: 1024 characters
- **Long messages**: Split into multiple messages

## Best Practices

### 1. Progressive Enhancement
- Start with basic formatting (bold, italic)
- Gradually add more complex features
- Always provide plain text fallback

### 2. User Experience
- Keep formatting consistent
- Don't over-format (less is more)
- Use formatting to improve readability, not decoration

### 3. Performance
- Cache formatted messages when possible
- Validate markdown before sending
- Handle errors gracefully

### 4. Accessibility
- Ensure content is readable without formatting
- Use formatting to enhance, not replace, meaning
- Test with screen readers when possible

## Implementation Checklist

- [ ] Replace `sanitize_text()` with `preserve_markdown()`
- [ ] Add `parse_mode='MarkdownV2'` to `send_message()` calls
- [ ] Implement markdown validation
- [ ] Add plain text fallback
- [ ] Test with various markdown inputs
- [ ] Handle character limits
- [ ] Add error logging for formatting failures

## References

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api#formatting-options)
- [MarkdownV2 Specification](https://core.telegram.org/bots/api#markdownv2-style)
- [Telethon Documentation](https://docs.telethon.dev/en/latest/modules/client.html#telethon.client.messages.MessageMethods.send_message) 