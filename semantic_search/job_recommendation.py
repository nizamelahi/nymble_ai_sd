from sentence_transformers.util import cos_sim
from sentence_transformers import SentenceTransformer
import pandas as pd
import fitz
from semantic_search.semantic_search import search

threshold = 0.81
allowed=[",","."]
garbage=["skills","details","experience"]
progress=0.2
pc=0

def results_from_resume(df_data,model,in_file):
    global progress
    doc = fitz.open(stream=in_file["file"].read(),filetype="pdf")
    pdf = ""
    for page in doc:
       pdf+=page.get_text()
    doc.close()

    sentences=pdf.split("\n")
    for i,sentence in enumerate(sentences):
        words=sentence.split(" ")
        for idx,word in enumerate(words):
            if (len(word) == 1 and word not in allowed) or (word in garbage) :
                words.pop(idx)
        if words: 
            sentences[i]=" ".join(words) 
        else: 
            sentences.pop(i)

    df=pd.DataFrame(sentences,columns =['sentences'])
    df=df.dropna()

    def encfunc(x,model):
        global progress
        global pc
        pc+=1
        progress=(pc/len(sentences))/2
        return  model.encode(x,normalize_embeddings=True)


    df["embeddings"] = df.sentences.apply(encfunc,args=(model,))

    query = model.encode(
        "technologies,softwares,trades,talent,professional skills,hardware",
        normalize_embeddings=True,
    )
    df["similarity"] = df.embeddings.apply(
        lambda x: cos_sim(query, x)
    )

    results = df[df.similarity >= threshold]

    results = results.sort_values("similarity", ascending=False).head(20)

    important=results.sentences.tolist()

    links=[]
    desc=[]
    pc=0
    progress=0
    for i in important:
        pc+=1
        new=(search(df_data, model=model,query=i,n=99999))
        links.extend(new["links"])
        desc.extend(new["descriptions"])
        progress=0.5+((pc/len(important))/2)
    resultdict={}
    for i,link in enumerate(links):
        if link == " ":
            continue
        if(resultdict.get(link)):
            resultdict[link]["count"]+=1
        else:
            resultdict[link]={"description":desc[i],"count":1}
    
    output=[]
    for link in resultdict:
        output.append([link,resultdict[link]["description"],resultdict[link]["count"]])
    
    return {"output":output}