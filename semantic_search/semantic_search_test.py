from ast import literal_eval
from sklearn.metrics.pairwise import cosine_similarity
from InstructorEmbedding import INSTRUCTOR
import pickle
from tabulate import tabulate

datafile = "data/stored_embeddings_jobs.pkl"
threshold = 0.8
# read the pickle file
with open(datafile, "rb") as f:
    df = pickle.load(f)


model = INSTRUCTOR("hkunlp/instructor-large")


# search through the reviews for a specific product
def search_reviews(df, product_description, n=3, pprint=True):
    product_embedding = model.encode(
        [["represent the sentence for retrieval", product_description]],
        normalize_embeddings=True,
    )
    df["similarity"] = df.embeddings.apply(
        lambda x: cosine_similarity(product_embedding, x)
    )

    results = df[df.similarity >= threshold]
    results = results.sort_values("similarity", ascending=False).head(n)

    results = results[["job_posting_link", "combined"]]

    if len(results):
        descriptions = (
        results.combined
        .str.replace("job_title: ", "")
        .str.replace("; company_name:", "at ")
        .str.replace("; text:", ":  ")
        .str.replace("; location:", ".  ")
        .str.strip()
        ).tolist()
        links=(results.job_posting_link.str.strip()).tolist()
    else:
        links=[" "]
        descriptions=["no relevant results were found"]
    return ({"links":links,"descriptions":descriptions})


jobs= search_reviews(df, "google", n=15)
links=jobs["links"]
descriptions=jobs["descriptions"]
for l,d in zip(links,descriptions):
    print(l)
    print(d)
    print( )
