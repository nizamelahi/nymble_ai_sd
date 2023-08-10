from sentence_transformers.util import cos_sim
import pandas as pd
import fitz
from semantic_search.semantic_search import search
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
import string
from semantic_search.garbage import garbage

nltk.download("stopwords")

threshold = 0.75
allowed = [",", "."]

progress = 0.0
pc = 0
experience_synonyms = ["experience","Employment","History"]


def remove_garbage(x):
    if x in ( garbage+stopwords.words("english")):
        return ""
    else:
        return x


def results_from_resume(df_data, model, in_file):
    global progress
    global pc
    progress = 0.0
    pc = 0
    doc = fitz.open(stream=in_file["file"].read(), filetype="pdf")
    pdf = ""
    for page in doc:
        pdf += page.get_text()
    doc.close()

    pdf = " "+pdf.lower()
    start_index=False
    
    for word in experience_synonyms:
        if word in experience_synonyms:
            start_index = pdf.find(word)
            break
    
    if start_index:
        print("alt algo")
        
        pdf = pdf[start_index:]
        pdf=pdf.replace("\n", " ")

        for word in garbage:
            pdf=pdf.replace(word," ")

        links = []
        desc = []
        new = search(df_data, model=model, query=pdf, n=99999)
        links.extend(new["links"])
        desc.extend(new["descriptions"])
        resultdict = {}
        for i, link in enumerate(links):
            if link == " ":
                continue
            if resultdict.get(link):
                resultdict[link]["count"] += 1
            else:
                resultdict[link] = {"description": desc[i], "count": 1}

        output = []
        for link in resultdict:
            output.append(
                [link, resultdict[link]["description"], resultdict[link]["count"]]
            )
        return {"output": output}

    else:
        print("old algo")
        trans_table = str.maketrans("", "", string.digits)

        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([pdf])
        words = vectorizer.get_feature_names_out()
        dense = vectors.todense()
        importance = dense.tolist()
        df = pd.DataFrame(
            list(zip(words, importance[0])), columns=["words", "importance"]
        )
        df["words"] = df.words.str.translate(trans_table)
        df["words"] = df.words.apply(remove_garbage)
        df.drop(df[df.words == ""].index, inplace=True)

        df = df.sort_values("importance", ascending=False)

        words = df.words.tolist()
        sentences = []
        temp = ""
        for i, word in enumerate(words):
            temp = temp + word + " "
            if (i + 1) % 20 == 0:
                sentences.append(temp)
                temp = ""

        df = pd.DataFrame(sentences, columns=["words"])

        # def encfunc(x, model):
        #     global progress
        #     global pc
        #     pc += 1
        #     progress = (pc / len(words)) / 2
        #     return model.encode(x, normalize_embeddings=True)

        # df["embeddings"] = df.words.apply(encfunc, args=(model,))

        # query = model.encode(
        #     "skills specialisations expertise abilities",
        #     normalize_embeddings=True,
        # )
        # df["similarity"] = df.embeddings.apply(lambda x: cos_sim(query, x))

        # results = df[df.similarity >= threshold]

        # results = df.sort_values("similarity", ascending=False).head(20)

        important = df.words.tolist()

        links = []
        desc = []
        pc = 0
        for i in important:
            pc += 1
            new = search(df_data, model=model, query=i, n=99999)
            links.extend(new["links"])
            desc.extend(new["descriptions"])
            progress = 0.5 + ((pc / len(important)) / 2)
        resultdict = {}
        for i, link in enumerate(links):
            if link == " ":
                continue
            if resultdict.get(link):
                resultdict[link]["count"] += 1
            else:
                resultdict[link] = {"description": desc[i], "count": 1}

        output = []
        for link in resultdict:
            output.append(
                [link, resultdict[link]["description"], resultdict[link]["count"]]
            )

        return {"output": output}
