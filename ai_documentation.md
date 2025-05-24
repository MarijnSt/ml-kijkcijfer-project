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

> How can I get end_date as the day before yesterday? It should be in the same format as start_date where months and days shouldn't have leading zeros.

I'll help you get the end_date in the same format as start_date. Here's how you can do it using Python's datetime module:
```
from datetime import datetime, timedelta

# Get the day before yesterday
end_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%-m-%-d")
```
However, I should note that the %-m and %-d format codes (which remove leading zeros) only work on Unix-like systems (Linux, macOS).
...

---

> How can i add df_current_day to the df I initialised at the top?

To add df_current_day to your main DataFrame df, you can use pandas' concat function.

```
df = pd.concat([df, df_current_day], ignore_index=True)
```

This will:
1. Use pd.concat() to combine the existing df with the new df_current_day
2. ignore_index=True will reset the index of the resulting DataFrame to be sequential (0, 1, 2, ...)

---

> Error fetching data: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
>
> Would this point to a rate limiting issue?

Yes, this error message suggests a rate limiting issue. The "Remote end closed connection without response" typically occurs when the server actively closes the connection, which is a common way for APIs to implement rate limiting.
Looking at your code, you're making requests for each day in sequence without any delay between requests. This could trigger the API's rate limiting protection. Here's how you can modify your code to handle this:

```
...
while current_date <= end:
    try:
        # Format date back to string
        date_str = current_date.strftime("%Y-%-m-%-d")
        print(date_str)

        # Get data
        df_current_day = get_cim_tv_data(date_str)

        # Add to df
        if not df_current_day.empty:
            df = pd.concat([df, df_current_day], ignore_index=True)
        else:
            print(f"No data for date: {date_str}")

        # Add a delay between requests to avoid rate limiting
        time.sleep(1)

        # Move to next day
        current_date += timedelta(days=1)
    
    except Exception as e:
        print(f"Error processing date {date_str}: {str(e)}")
        time.sleep(5)  # Wait 5 seconds after an error
        continue
```

You might need to adjust the sleep times (1 second and 5 seconds) depending on the API's rate limits. If you're still getting rate limit errors, you could:
1. Increase the delay between requests
2. Implement exponential backoff (increase wait time after each error)
3. Check if the API has a documented rate limit and adjust accordingly

## 2.2 Preparing ratings data
* I selected the code block with the issue to add it as context to the chat window and pasted the error I got when running it*
> invalid literal for int() with base 10: '971420,70'

Ah, I see the issue. When you try to convert the string to an integer, it's failing because of the comma. We need to handle the decimal numbers properly. Here's how we can fix it:
```
# First remove dots and replace commas with dots for proper decimal handling
ratings_df['Kijkers'] = ratings_df['Kijkers'].str.replace('.', '').str.replace(',', '.')

# Convert to float first (to handle decimal numbers)
ratings_df['Kijkers'] = pd.to_numeric(ratings_df['Kijkers'], errors='coerce')

# Then convert to integer (this will round the decimal numbers)
ratings_df['Kijkers'] = ratings_df['Kijkers'].astype(int)
```
This will:
1. Remove the dots (thousand separators)
2. Replace commas with dots (to handle decimal numbers properly)
3. Convert to float first (which can handle decimal numbers)
4. Finally convert to integer (which will round the decimal numbers)

So numbers like:
- "971.420,70" will become 971420.70 (float) and then 971421 (integer)
- "836.931,30" will become 836931.30 (float) and then 836931 (integer)

This should handle all the numeric values correctly, including those with decimal places. The errors='coerce' parameter will convert any non-numeric values to NaN, which you can then handle separately if needed.
