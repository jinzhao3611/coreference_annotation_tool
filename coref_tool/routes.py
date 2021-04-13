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
from coref_tool.models import CorefPair, NoneCorefPair, Event, Article, Task
from werkzeug.exceptions import BadRequest
from coref_tool.forms import ChooseForm

# tasks = []
# with open("data/coref_candidates.jsonl", "r") as jsonl_file:
#     for task in jsonl_file.readlines():
#         tasks.append(json.loads(task))


@app.route("/", methods=["GET", "POST"])
def home():
    form = ChooseForm()
    if form.validate_on_submit():
        trigger_word = form.trigger_words.data
        task = Task.query.filter(Task.trigger == trigger_word).first()
        return redirect(url_for('annotate', task_id=task.task_id))
    # task_id = 0
    # if "set_sentence" in request.form:
    #     task_id = int(request.form["sentence_id"])

    return render_template("home.html", form=form)

@app.route("/annotate/<int:task_id>", methods=["GET", "POST"])
def annotate(task_id: int):
    #     save to db
    # if "save_annot" in request.form:
    #     pairs = request.form.getlist("pair")
    #     non_pairs = request.form.getlist("non-pair")
    #     for pair in pairs:
    #         coref_pair = CorefPair(
    #             emq=int(tasks[task_id]["query"]["query_id"]),
    #             emc=int(tasks[task_id]["candidates"][int(pair) - 1]["query_id"]),
    #         )
    #         db.session.add(coref_pair)
    #         db.session.commit()
    #
    #     for non_pair in non_pairs:
    #         non_coref_pair = NoneCorefPair(
    #             emq=int(tasks[task_id]["query"]["query_id"]),
    #             emc=int(tasks[task_id]["candidates"][int(non_pair) - 1]["query_id"]),
    #         )
    #         db.session.add(non_coref_pair)
    #         db.session.commit()

    # show the article containing the sentence
    if request.method == "POST":
        try:
            clicked_article_id = request.get_json(force=True)["clicked_article_id"]
            print(clicked_article_id)
            clicked_article = Article.query.filter(Article.id == clicked_article_id).first()
            return make_response(jsonify({"clicked_article": clicked_article.content, 'clicked_doc_id': clicked_article.doc_id, 'clicked_source': clicked_article.source}), 200)
        except BadRequest:
            print(f"no article!")


    query_info = Event.query.filter(Event.task_id == task_id).first()
    task = Task.query.get_or_404(task_id)
    candidate_query_ids = task.candidates.split()
    candidate_infos = [Event.query.filter(Event.id == query_id).first() for query_id in candidate_query_ids]
    return render_template("annotate.html", task_id=task_id, query_info=query_info, candidate_infos=candidate_infos)

