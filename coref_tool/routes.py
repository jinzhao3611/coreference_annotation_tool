from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    make_response,
    jsonify,
)
from coref_tool import app, db
import json
from coref_tool.models import CorefPair, NoneCorefPair, Event, Article
from werkzeug.exceptions import BadRequest

tasks = []
with open("data/coref_candidates.jsonl", "r") as jsonl_file:
    for task in jsonl_file.readlines():
        tasks.append(json.loads(task))


@app.route("/", methods=["GET", "POST"])
def home():
    task_id = 0
    if "set_sentence" in request.form:
        task_id = int(request.form["sentence_id"])

    if "save_annot" in request.form:
        pairs = request.form.getlist("pair")
        non_pairs = request.form.getlist("non-pair")
        #     save to db
        for pair in pairs:
            coref_pair = CorefPair(
                emq=int(tasks[task_id]["query"]["query_id"]),
                emc=int(tasks[task_id]["candidates"][int(pair) - 1]["query_id"]),
            )
            db.session.add(coref_pair)
            db.session.commit()

        for non_pair in non_pairs:
            non_coref_pair = NoneCorefPair(
                emq=int(tasks[task_id]["query"]["query_id"]),
                emc=int(tasks[task_id]["candidates"][int(non_pair) - 1]["query_id"]),
            )
            db.session.add(non_coref_pair)
            db.session.commit()
    if request.method == "POST":
        try:
            clicked_source = request.get_json(force=True)["clicked_source"]
            clicked_doc_id = request.get_json(force=True)["clicked_doc_id"]
            clicked_article = Article.query.filter(
                Article.source == clicked_source, Article.doc_id == clicked_doc_id
            ).first()
            return make_response(
                jsonify({"clicked_article": clicked_article.content}), 200
            )
        except BadRequest:
            print(f"no article!")

    return render_template("home.html", task_id=task_id, task=tasks[task_id])
