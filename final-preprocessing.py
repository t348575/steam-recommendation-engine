#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


df = pd.read_csv('steam_games.csv')
df = df[df['name'].notna()]
df.drop(["discount_price", "publisher", "developer", "release_date", "desc_snippet", "types", "achievements", "recent_reviews", "mature_content"], axis=1, inplace=True)


# In[3]:


for row in df.iterrows():
    if pd.isna(row[1][3]) and pd.isna(row[1][6]):
        print("deleting: ", row[1][1])
        df.drop(row[0], inplace=True)


# In[4]:


duplicated_items = df[df["name"].duplicated()]["name"].values.tolist()
games = {}
print(df.shape)
for row in df.iterrows():
    if row[1][1] in duplicated_items:
        if row[1][1] in games:
            games[row[1][1]].append(row[1].isna().sum())
        else:
            games[row[1][1]] = [row[1].isna().sum()]
for item in games:
    games[item].sort()
    count = 0
    for row in df.iterrows():
        if row[1][1] == item and (row[1].isnull().sum() == games[item][0]):
            df.drop(row[0], inplace=True)
            count += 1
            print("deleting: ", row[1][1])
        
        if count + 1 == len(games[item]):
            break
print(df.shape)
df.to_csv("steam_games_dup_removed.csv", index=False)


# In[5]:


df = pd.read_csv('steam_games_dup_removed.csv')

all_review_cols = ["all_review_sentiment", "all_review_sentiment_num", "all_review_num"]
temp_df = []
idx = 0
for row in df.iterrows():
    if row[1][2] == None or pd.isna(row[1][2]):
        temp_df.append(["None", 0, 0])
    else:
        try:
            items = row[1][2].split('(')
            sentiment = items[0].lower().strip()[0:-1]
            items = items[1].split(')')
            total = int(items[0].strip().replace(',', ''))
            percent = int(items[1].split('%')[0].strip()[3:]) / 100
            temp_df.append([sentiment, int(total * percent), total])
        except:
            temp_df.append(["None", 0, 0])
    idx += 1
    if idx % 5000 == 0:
        print(((idx + 1) / 40752) * 100, "%")
all_review_df = pd.DataFrame(temp_df, columns=all_review_cols)
df.drop(["all_reviews"], axis=1, inplace=True)
df = pd.concat([df, all_review_df], axis=1)

df['all_review_sentiment'] = df['all_review_sentiment'].astype('category').cat.codes
df['popular_tags'].fillna(df['genre'], inplace=True)

for i in range(len(df)):
    if pd.isna(df.loc[i, 'genre']):
        df.drop(i, inplace=True)
        
df.drop(['minimum_requirements', 'recommended_requirements', 'game_description'], axis=1, inplace=True)
df.to_csv("steam_games_reviews.csv", index=False)

categories = list(df['all_review_sentiment'].astype('category').cat.categories)


# In[6]:


def format_csv(data):
    try:
        return list(set(data.split(',')))
    except:
        return []

df = pd.read_csv('steam_games_reviews.csv')
df['total'] = df['popular_tags'] + df['genre'] + df['game_details']
df['total'] = df['total'].apply(format_csv)
df['languages'] = df['languages'].apply(format_csv)
df.drop(['popular_tags', 'game_details', 'genre'], axis=1, inplace=True)

df.to_csv('steam_games_genres.csv', index=False)


# In[7]:


df = pd.read_csv('steam_games_genres.csv')
df['all_review_sentiment'] =(df['all_review_sentiment']-df['all_review_sentiment'].min())/(df['all_review_sentiment'].max()-df['all_review_sentiment'].min())
df['all_review_sentiment_num'] =(df['all_review_sentiment_num']-df['all_review_sentiment_num'].min())/(df['all_review_sentiment_num'].max()-df['all_review_sentiment_num'].min())
df['all_review_num'] =(df['all_review_num']-df['all_review_num'].min())/(df['all_review_num'].max()-df['all_review_num'].min())

df.to_csv('steam_game_review_normal.csv', index=False)


# In[8]:


df = pd.read_csv('steam_game_review_normal.csv')

def format_price(price):
    price_str = str(price)
    if price_str[0] == "$":
        return float(price_str[1:])
    
    try:
        test = int(price_str[0])
        return float(price_str)
    except:
        return 0

df['original_price'] = df['original_price'].apply(format_price)

df.to_csv('steam_games_final_format.csv', index=False)


# In[9]:


df

