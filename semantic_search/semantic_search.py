from sklearn.metrics.pairwise import cosine_similarity
from InstructorEmbedding import INSTRUCTOR
import pickle
from tabulate import tabulate



threshold = 0.8
# read the pickle file
def initialise(filename):
    with open(filename, "rb") as f:
        df = pickle.load(f)


    return(df,INSTRUCTOR("hkunlp/instructor-large"))


# search through the reviews for a specific product
def search(df, product_description,model, n=15):
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
        .str.replace("; company_name:", " at ")
        .str.replace("; text:", ":  ")
        .str.replace("; location:", ".  ")
        .str.strip()
        .tolist()
        )
        links=(results.job_posting_link.str.strip()).tolist()
    else:
        links=[" "]
        descriptions=["no relevant results were found"]

    print(tabulate(results))
    return ({"links":links,"descriptions":descriptions})
