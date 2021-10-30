import sys
from sklearn.preprocessing import MultiLabelBinarizer
from scipy import spatial
import pandas as pd
import numpy as np
import math
import time

if len(sys.argv) == 1:
    print("Usage: python model.py <input_file>")
    sys.exit(1)

start_time = time.time()
df = ""
try:
    df = pd.read_csv('steam_games_final_format.csv')
except:
    print("Error: Could not find dataframe")
    sys.exit(1)

print("Dataframe loaded in %s seconds\n" % (time.time() - start_time))

input_url = sys.argv[1]

if input_url[len(input_url)-1] != "/":
    input_url += "/"

search_item = ""
search_item_idx = ""
try:
    item = df.loc[df['url'] == input_url]
    search_item = list(item.iloc[0])
    search_item_idx = item.index.tolist()[0]
except:
    print("Error: Could not find input url")
    sys.exit(1)

print("Selected item: %s\n" % search_item[1])

start_time = time.time()
multilabel_binarizer = MultiLabelBinarizer()
multilabel_binarizer.fit(df['total'])
genre_y = multilabel_binarizer.transform(df['total'])

print("Initialized model in %s seconds\n" % (time.time() - start_time))
print("Model ready!\n\nRunning model...\n")

start_time = time.time()
input_item = genre_y[search_item_idx]
input_item_review = list(df.iloc[search_item_idx][4:7])

start_time = time.time()
idx = 0
result = []

for i in df.iterrows():
    idx += 1
    if idx % 4032 == 0:
        print(str(((idx + 1) / 40328) * 100) + "%")
    result.append({
        "url": i[1][0],
        "cos_dist": float(spatial.distance.cosine(input_item, genre_y[idx-1])),
        "review_euc_dist": float(spatial.distance.euclidean(input_item_review, i[1][4:7]))
    })

results_df = pd.DataFrame(result)
results_df.sort_values(by=['cos_dist', 'review_euc_dist'], inplace=True)

print("\nModel ran in %s seconds\n" % (time.time() - start_time))

print(results_df.head(20))