from os import getenv
from dotenv import load_dotenv
from flask import Flask, request
from semantic_search.semantic_search import search, initialise
# from semantic_search.job_recommendation import results_from_resume
import semantic_search.job_recommendation

load_dotenv()
# creating a Flask app
app = Flask(__name__)
datafile = getenv("processed_data")

df, model = initialise(datafile)
print("search engine ready")


@app.route("/search", methods=["GET"])
def searchpage():
    return search(df, model=model,query=request.json.get("query"),page=request.json.get("page"))

@app.route("/job_recommendations", methods=["GET"])
def resumeupload():
    return semantic_search.job_recommendation.results_from_resume(df_data=df, model=model,in_file=request.files)

@app.route("/progress", methods=["GET"])
def prg():
    return {"progress":semantic_search.job_recommendation.progress}

# driver function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8365,debug=True)
