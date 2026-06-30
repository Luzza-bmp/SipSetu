import spacy

nlp = spacy.load("output_model/model-best")

text = """
Bachelor of Computer Engineering
Python
PostgreSQL
Machine Learning
Software Engineer
"""

doc = nlp(text)

for ent in doc.ents:
    print(ent.text, "->", ent.label_)
