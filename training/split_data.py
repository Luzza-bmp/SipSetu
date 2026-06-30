import random
import spacy
from spacy.tokens import DocBin

nlp = spacy.blank("en")

doc_bin = DocBin().from_disk("all_data.spacy")
docs = list(doc_bin.get_docs(nlp.vocab))

random.shuffle(docs)

split = int(len(docs) * 0.8)

train_docs = docs[:split]
dev_docs = docs[split:]

train_bin = DocBin()
dev_bin = DocBin()

for doc in train_docs:
    train_bin.add(doc)

for doc in dev_docs:
    dev_bin.add(doc)

train_bin.to_disk("train.spacy")
dev_bin.to_disk("dev.spacy")

print("Train:", len(train_docs))
print("Dev:", len(dev_docs))
