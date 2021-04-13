# this file is used to populate the article and event database
import os
from pathlib import Path
from typing import Union

from coref_tool import db
import json
from coref_tool.models import Article, Event, Task
from collections import defaultdict

FILE_PREFIX = "bert-base-cased_"
FILE_SUFFIX = "_auto_nodes"
EASY_TO_READ = "txt_easy_to_read.txt"


def load_articles_from_file(annotation_file: Union[str, os.PathLike]):
    articles = list()
    with open(annotation_file, "r", encoding="utf-8") as f:
        doc_id = 0
        snt_line = False
        event_line = False
        article = ""
        for line in f:
            line = line.strip()
            if not line:
                articles.append(article)
                article = ""
                doc_id += 1
                snt_line = False
                event_line = False
                continue
            elif line == "SNT_LIST":
                snt_line = True
                event_line = False
                continue
            elif line == "EDGE_LIST":
                snt_line = False
                event_line = True
                continue
            else:
                if snt_line:
                    article += line + "\n"
                elif event_line:
                    pass
                else:
                    raise ValueError(f"unknown line: {line}")
    return articles

def load_articles_from_folder(annotation_folder: str):
    for file_name in os.listdir(annotation_folder):
        if file_name.endswith(EASY_TO_READ):
            source = Path(Path(annotation_folder).joinpath(file_name)).stem.split(".")[
                0
            ][len(FILE_PREFIX) :][: -len(FILE_SUFFIX)]
            for doc_id, article in enumerate(
                load_articles_from_file(Path(annotation_folder).joinpath(file_name))
            ):
                article = Article(source=source, doc_id=doc_id, content=article)
                db.session.add(article)
                db.session.commit()
            print(f"populated {source} in article database")

def load_events_from_jsonl(jsonl_file: str):
    with open(jsonl_file, encoding="utf-8") as jsonl_file:
        for i, line in enumerate(jsonl_file):
            item = json.loads(line)
            article = Article.query.filter(
                Article.source == item["query"]["source"],
                Article.doc_id == item["query"]["doc_id"],
            ).first()
            # print(article.content)
            # print(item['query']['sentence'])
            event = Event(
                id=item["query"]["query_id"],
                trigger=item["query"]["trigger"],
                trigger_id=item["query"]["trigger_id"],
                sentence=item["query"]["sentence"],
                article_id=article.id,
                task_id=i,
                annot=0
            )
            db.session.add(event)
            db.session.commit()
            print(f"added {i} events in event database")

def populate_article_database():
    folder_path = '/Users/jinzhao/schoolwork/lab-work/event_search/data/covid_event_for_event_coref'
    load_articles_from_folder(folder_path)

def populate_event_database():
    jsonl_file = "data/coref_candidates.jsonl"
    load_events_from_jsonl(jsonl_file)

def populate_task_database():
    jsonl_file = "data/coref_candidates.jsonl"
    with open(jsonl_file, 'r', encoding='utf-8') as jsonl_file:
        for i, task in enumerate(jsonl_file.readlines()):
            task_dict = json.loads(task)
            task_row = Task(task_id=i, trigger=task_dict['query']['trigger'], candidates=" ".join([candidate['query_id'] for candidate in task_dict['candidates']]))
            db.session.add(task_row)
            db.session.commit()


def output_trigger_tasks():
    input_file = 'data/coref_candidates.jsonl'
    output_file = 'data/trigger_tasks_index.json'
    trigger_tasks = defaultdict(list)
    with open(input_file, 'r', encoding='utf-8') as jsonl_file:
        for i, task in enumerate(jsonl_file.readlines()):
            task_dict = json.loads(task)
            trigger_tasks[task_dict['query']['trigger']].append(i)
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        json.dump(trigger_tasks, jsonl_file)

if __name__ == "__main__":
    populate_task_database()

