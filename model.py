import sys
from sklearn.preprocessing import MultiLabelBinarizer
from scipy import spatial
import pandas as pd
import numpy as np
import math
import time

input_url = []
i = 1
while(i>0):
    input_url.append(input("Enter the Steam URL of the Game: "))
    item = input("Do you want to add more games? (y/n): ")
    if item == "N" or item == "n":
        break
    i+=1



start_time = time.time()
df = ""
try:
    df = pd.read_csv('steam_games_final_format.csv')
except:
    print("Error: Could not find dataframe")
    sys.exit(1)

print("Dataframe loaded in %s seconds\n" % (time.time() - start_time))

search_item = ''
search_item_idx = []
for i in range(len(input_url)):
    if input_url[i][len(input_url[i])-1] != "/":
        input_url[i] += "/"
    try:
        item = df.loc[df['url'] == input_url[i]]
        search_item = list(item.iloc[0])
        search_item_idx.append(item.index.tolist()[0])
    except:
        print("Error: Could not find input url")
        sys.exit(1)
    print("Selected item: %s\n" % search_item[1])


start_time = time.time()
multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(df['total'])
genre_y = multilabel_binarizer.transform(df['total'])

print("Initialized model in %s seconds\n" % (time.time() - start_time))

start_time = time.time()

result = []
reviewStatus = []

for j in search_item_idx:
    print("Model ready!\n\nRunning model for %s\n" % df.iloc[j][1])
    start_time = time.time()
    idx = 0
    input_item = genre_y[j]
    input_item_review = list(df.iloc[j][4:7])
    
    skipReview = False
    if input_item_review == [0.0, 0.0, 0.0]:
        skipReview = True

    result.append([])
    reviewStatus.append(skipReview)
    n = len(result) - 1
    
    for i in df.iterrows():
        idx += 1
        if idx % 3757 == 0:
            print(str(((idx + 1) / 37578) * 100) + "%")

        reviewRes = 1.0
        if not skipReview:
            reviewRes = float(spatial.distance.euclidean(input_item_review, i[1][4:7]))
        result[n].append({
            "url": i[1][0],
            "data": i,
            "cos_dist": float(spatial.distance.cosine(input_item, genre_y[idx-1])),
            "review_euc_dist": reviewRes
        })
    print("\nModel ran in %s seconds\n" % (time.time() - start_time))
    
outer_idx = 0
squashed = {}
for j in result:
    results_df = pd.DataFrame(j)
    results_df.sort_values(by=['cos_dist', 'review_euc_dist'], inplace=True)
    results_df.drop(index=results_df.index[0], axis=0, inplace=True)
    idx = 0
    
    if reviewStatus[idx]:
        print("Note: review data not used for %s" % df.iloc[search_item_idx[outer_idx]][1])

    for i in results_df.drop(["url", "cos_dist", "review_euc_dist"], axis=1).iterrows():
        if idx == 20:
            break
        if i[1][0][1][1] not in squashed:
            squashed[i[1][0][1][1]] = outer_idx
        idx += 1
    outer_idx += 1


for i in squashed:
    print(i)


