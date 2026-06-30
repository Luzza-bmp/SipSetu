import json
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

nlp = spacy.blank("en")
doc_bin = DocBin()

with open("annotated_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:

    text = item["data"]["text"]

    doc = nlp.make_doc(text)

    ents = []

    if item.get("annotations"):

        results = item["annotations"][0]["result"]

        for r in results:

            try:
                start = r["value"]["start"]
                end = r["value"]["end"]
                label = r["value"]["labels"][0]

                span = doc.char_span(
                    start,
                    end,
                    label=label,
                    alignment_mode="contract"
                )

                if span:
                    ents.append(span)

            except Exception:
                continue

    ents = filter_spans(ents)

    doc.ents = ents

    doc_bin.add(doc)

doc_bin.to_disk("all_data.spacy")

print("Saved all_data.spacy")
