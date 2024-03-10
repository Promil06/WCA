from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import os

extract = URLExtract()

def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    # fetch number of messages
    num_messages = df.shape[0]
    # fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())
    # fetch number of media files share
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    # fetch number of links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    # Exclude rows where the user is 'group_notification' when calculating the most frequent users
    x = df[df['user'] != 'group_notification']['user'].value_counts().head()
    # Exclude rows where the user is 'group_notification' when calculating user counts
    user_counts = df[df['user'] != 'group_notification']['user'].value_counts()
    # Calculate the percentage of messages sent by each user (excluding 'group_notification')
    df = round((user_counts / user_counts.sum()) * 100, 2).reset_index().rename(
        columns={'percent': 'name', 'count': 'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    filtered_message = df[~df['message'].str.contains('Media omitted')]['message']
    text = ' '.join(filtered_message)

    wc = WordCloud(width = 500, height = 500, min_font_size = 10, background_color = 'white')
    df_wc = wc.generate(text)
    return df_wc

def most_common_words(selected_user, df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    words = []

    for message in df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    filtered_words = [word for word in words if
                      word not in ['<media', 'omitted>', ',', '.', '&', '@918595113712', '@916388084649']]

    # Count the occurrences of each filtered word and get the 20 most common words
    most_common_df = pd.DataFrame(Counter(filtered_words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heat_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heat_map = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heat_map