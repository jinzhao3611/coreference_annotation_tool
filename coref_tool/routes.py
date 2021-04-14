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

@app.route("/", methods=["GET", "POST"])
def home():
    form = ChooseForm()
    if form.validate_on_submit():
        trigger_word = form.trigger_words.data
        task = Task.query.filter(Task.trigger == trigger_word).first()
        return redirect(url_for('annotate', task_id=task.task_id))
    return render_template("home.html", form=form)

@app.route("/annotate/<int:task_id>", methods=["GET", "POST"])
def annotate(task_id: int):
    if request.method == "POST":
        if "set_sentence" in request.form:
            task_id = int(request.form["sentence_id"])
            return redirect(url_for('annotate', task_id=task_id))

        # show the article containing the sentence
        try:
            clicked_article_id = request.get_json(force=True)["clicked_article_id"]
            print(clicked_article_id)
            clicked_article = Article.query.filter(Article.id == clicked_article_id).first()
            return make_response(jsonify({"clicked_article": clicked_article.content, 'clicked_doc_id': clicked_article.doc_id, 'clicked_source': clicked_article.source}), 200)
        except BadRequest:
            print(f"no article!")

    # get the tasks to display (query and candidates)
    query_info = Event.query.filter(Event.task_id == task_id).first()
    task = Task.query.get_or_404(task_id)
    candidate_query_ids = task.candidates.split()
    candidate_infos = [Event.query.filter(Event.id == query_id).first() for query_id in candidate_query_ids]

    #  save to db
    if "save_annot" in request.form:
        pairs = request.form.getlist("pair")
        non_pairs = request.form.getlist("non-pair")
        print(pairs)
        print(non_pairs)
        try:
            for pair in pairs:
                if query_info.id != int(candidate_query_ids[int(pair) - 1]):# if the query and candidate are not the same (in our data, query are got from the data, so the first coreferenced candidate is usually the query itself)
                    existing_pair1 = CorefPair.query.filter(CorefPair.emq==query_info.id, CorefPair.emc==int(candidate_query_ids[int(pair)-1])).first()
                    existing_pair2 = CorefPair.query.filter(CorefPair.emq==int(candidate_query_ids[int(pair)-1]), CorefPair.emc==query_info.id).first()
                    if not existing_pair1 and not existing_pair2: #there could be duplicate, the position of query and candidate could be reversed
                        coref_pair = CorefPair(
                            emq=query_info.id,
                            emc=int(candidate_query_ids[int(pair) - 1]),
                        )
                        db.session.add(coref_pair)

            for non_pair in non_pairs:
                if query_info.id != int(candidate_query_ids[int(non_pair) - 1]):# if the query and candidate are not the same (in our data, query are got from the data, so the first coreferenced candidate is usually the query itself)
                    existing_non_pair1 = NoneCorefPair.query.filter(NoneCorefPair.emq == query_info.id, NoneCorefPair.emc == int(candidate_query_ids[int(non_pair) - 1])).first()
                    existing_non_pair2 = NoneCorefPair.query.filter(NoneCorefPair.emq == int(candidate_query_ids[int(non_pair) - 1]), NoneCorefPair.emc == query_info.id).first()
                    if not existing_non_pair1 and not existing_non_pair2:  # there could be duplicate, the position of query and candidate could be reversed
                        non_coref_pair = NoneCorefPair(
                            emq=query_info.id,
                            emc=int(candidate_query_ids[int(non_pair) - 1]),
                        )
                        db.session.add(non_coref_pair)
                    db.session.commit()
        except:
            print('Failed: pairs are not added in database')
    return render_template("annotate.html", task_id=task_id, query_info=query_info, candidate_infos=candidate_infos)

@app.route("/display", methods=["GET", "POST"])
def display():
    coref_pairs = [] # [(Event, Event), ...]
    # show the article containing the sentence
    if request.method == "POST":
        try:
            clicked_article_id = request.get_json(force=True)["clicked_article_id"]
            print(clicked_article_id)
            clicked_article = Article.query.filter(Article.id == clicked_article_id).first()
            return make_response(jsonify(
                {"clicked_article": clicked_article.content, 'clicked_doc_id': clicked_article.doc_id,
                 'clicked_source': clicked_article.source}), 200)
        except BadRequest:
            print(f"no article!")

    # get the annotated data to display (query and candidates)
    for entry in CorefPair.query.all():
        coref_pairs.append((Event.query.filter(Event.id == entry.emq).first(), Event.query.filter(Event.id == entry.emc).first()))

    print(coref_pairs)
    return render_template("display.html", coref_pairs=coref_pairs)
