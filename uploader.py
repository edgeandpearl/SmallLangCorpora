from elasticsearch import Elasticsearch
import os
import mastresk2

es = Elasticsearch()


def loader(path="."):
    for root, dirs, files in os.walk(path):
        for fil in files:
            if fil.endswith(".xml"):
                for sents, doc in mastresk2.main(os.path.join(root, fil)):
                    sent_ids = []
                    for sent in sents:
                        sent_info = es.index(index='smallangs', doc_type='sentence', body=sent)
                        sent_ids.append(sent_info['_index']) # ПРОВЕРЬ ЧТО ЗДЕСЬ ТОТ КЛЮЧ
                    doc['document']['phrases'] = sent_ids
                    res = es.index(index='smallangs', doc_type='text', body=doc)
                    print(res)
                    print("__________")

# res = es.get(index='smalllangs', doc_type="text")


if __name__ == '__main__':
    loader()
