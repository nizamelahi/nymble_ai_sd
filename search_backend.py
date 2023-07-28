from os import getenv
from dotenv import load_dotenv
from flask import Flask, request
from semantic_search.semantic_search import search, initialise

load_dotenv()
# creating a Flask app
app = Flask(__name__)
datafile = getenv("processed_data")

df, model = initialise(datafile)
print("search engine ready")


@app.route("/search", methods=["GET", "POST"])
def searchpage():
    return search(df, model=model,query=request.json.get("query"),page=request.json.get("page"))


# driver function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8365)
