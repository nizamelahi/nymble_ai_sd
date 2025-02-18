import pandas as pd
from sentence_transformers import SentenceTransformer
from datetime import datetime
import pickle

input_datapath = "data/report_large.csv"
old="data/report_old.csv"
outfile_path="data/stored_embeddings_jobs.pkl"

df = pd.read_csv(input_datapath,delimiter=";")
df1 = pd.read_csv(old,delimiter=";")
df=pd.concat([df,df1])

df = df[["job_title", "job_posting_link", "company_name", "short_description", "location"]]
df = df.dropna()
df["combined"] = (
    "job_title: " + df.job_title.str.strip() + "; company_name: " + df.company_name.str.strip() +"; text: " + df.short_description.str.strip() + "; location: " + df.location.str.strip() 
)
model = SentenceTransformer('thenlper/gte-large')
# max_length = 500
# top_n = 1000
# df = df.sort_values("").tail(top_n * 2)

df["n_tokens"] = df.combined.apply(lambda x: len((x.split())))
# df = df[df.n_tokens <= max_length]

starttime = datetime.now()
df["embeddings"] = df.combined.apply(lambda x: model.encode(x,normalize_embeddings=True,show_progress_bar=True))

picklefile = open(outfile_path, 'wb')
#pickle the dataframe
pickle.dump(df, picklefile)
#close file
picklefile.close()

print(f"{len(df)} embeddings calculated in ")
print(f"{(datetime.now()-starttime).total_seconds()} seconds")


# query_embeddings = model.encode(query)
# corpus_embeddings = model.encode(corpus)
# similarities = cosine_similarity(query_embeddings,corpus_embeddings)
# retrieved_doc_id = np.argmax(similarities)
# print(retrieved_doc_id)