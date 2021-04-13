from coref_tool import db


class CorefPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emq = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    emc = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    coref_pair_q = db.relationship(
        "Event", backref="eventq", lazy=True, foreign_keys=[emq]
    )
    coref_pair_e = db.relationship(
        "Event", backref="eventc", lazy=True, foreign_keys=[emc]
    )

    def __repr__(self):
        return f"CorefPairs('{self.emq}', '{self.emc}')"


class NoneCorefPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emq = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    emc = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    none_coref_pair_q = db.relationship(
        "Event", backref="none_eventq", lazy=True, foreign_keys=[emq]
    )
    none_coref_pair_e = db.relationship(
        "Event", backref="none_eventc", lazy=True, foreign_keys=[emc]
    )

    def __repr__(self):
        return f"NonCorefPairs('{self.emq}', '{self.emc}')"


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, nullable=False)
    source = db.Column(db.TEXT, nullable=False)
    content = db.Column(db.TEXT, nullable=False)

    events = db.relationship("Event", backref="article", lazy=True)


class Event(db.Model):
    id = db.Column(
        db.Integer, nullable=False, primary_key=True
    )  # this is the unique query id
    trigger = db.Column(db.TEXT, nullable=False)
    trigger_id = db.Column(db.TEXT, nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    sentence = db.Column(db.TEXT, nullable=False)
    task_id = db.Column(db.Integer, nullable=False, unique=True)
    annot = db.Column(db.Integer, nullable=False)

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True) #task_id of query event
    trigger = db.Column(db.TEXT, nullable=False)
    candidates = db.Column(db.TEXT, nullable=False) #joined query_id of the candidates
