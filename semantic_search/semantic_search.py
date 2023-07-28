from sklearn.metrics.pairwise import cosine_similarity
from InstructorEmbedding import INSTRUCTOR
import pickle
from tabulate import tabulate



threshold = 0.81
# read the pickle file
def initialise(filename):
    with open(filename, "rb") as f:
        df = pickle.load(f)


    return(df,INSTRUCTOR("hkunlp/instructor-large"))


# search through the reviews for a specific product
def search(df, query,model,page=1, n=15):
    if(page<1):
        page=1
    product_embedding = model.encode(
        [["represent the sentence for retrieval", query]],
        normalize_embeddings=True,
    )
    df["similarity"] = df.embeddings.apply(
        lambda x: cosine_similarity(product_embedding, x)
    )

    results = df[df.similarity >= threshold]
    pages=(len(results)/n)
    if len(results)-(n*page)<0:
        num_results=len(results)-(n*page)
        lastpage=True
    else:
        num_results=n
        lastpage=False
    print(len(results))
    results = results.sort_values("similarity", ascending=False).head(n*(page)).tail(num_results)
    

    results = results[["job_posting_link", "combined"]]

    if len(results):
        descriptions = (
        results.combined
        .str.replace("job_title: ", "")
        .str.replace("; company_name:", " at ")
        .str.replace("; text:", ":  ")
        .str.replace("; location:", ":::")
        .str.strip()
        .str.replace(":::","\n")
        .tolist()
        )
        links=(results.job_posting_link.str.strip()).tolist()
    else:
        links=[" "]
        descriptions=["no relevant results were found"]

    # for l,d in zip(links,descriptions):
    #     print(l)
    #     print( )
    #     print(d)
    #     print("______________")

        
    return ({"links":links,"descriptions":descriptions,"lastpage":lastpage,"pages":pages})
