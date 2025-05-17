# O. Introduction
This document was used to track my interactions with an AI assitant. 
I used **Cursor** as an IDE which has two assistant functionalities.

1. Cursor Tab: autocomplete and code suggestions.
2. AI panel: one of the panels in the IDE can be used to chat with an AI assistant. I mainly use it to ask questions about code I don't understand or to get suggestions on how to solve certain situations.

Cursor allows you to select and use a bunch of LLM's for it's AI. For this project it used:
- Claude-3.5-sonnet
- Claude-3.7-sonnet-thinking
- Cursor-small
- Gemini-2.5-pro-preview-05-06
- Gpt-4.1
- Gpt-4o
- o3

In section 2 I list all my AI chat prompts: all the questions I asked and the most relevant parts of the answers (as sometimes it writes way to much).

# 1. Reflection
One prompt I often use is this:

> Please suggest some improvements to this code and explain why it's better that way. Think about improving readability, speed and efficiancy of the code I have now.

I use this when I finished a code block and when I'm curious to see if there are some things I can improve on. Depending on the answer, I implement the suggested improvements or not. Sometimes I like the suggestion and use it. I don't use it when it's just rephrasing what I already have or when it overcomplicates things (which it tends to do).

But it has also helped me to learn things I didn't already know. I see it as a learning tool for when I'm curious to see if I can improve what I already have.


# 2. AI Chat Prompts

## 2.1 Getting ratings data

### How can I get end_date as the day before yesterday? It should be in the same format as start_date where months and days shouldn't have leading zeros.

I'll help you get the end_date in the same format as start_date. Here's how you can do it using Python's datetime module:
```
from datetime import datetime, timedelta

# Get the day before yesterday
end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%-m-%-d")
```
However, I should note that the %-m and %-d format codes (which remove leading zeros) only work on Unix-like systems (Linux, macOS).
...

---

### How can i add df_current_day to the df I initialised at the top?

To add df_current_day to your main DataFrame df, you can use pandas' concat function.

```
df = pd.concat([df, df_current_day], ignore_index=True)
```

This will:
1. Use pd.concat() to combine the existing df with the new df_current_day
2. ignore_index=True will reset the index of the resulting DataFrame to be sequential (0, 1, 2, ...)