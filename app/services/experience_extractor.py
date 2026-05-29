import spacy

nlp = spacy.load("en_core_web_sm")

JOB_TITLES = [

    "developer",
    "engineer",
    "intern",
    "manager",
    "analyst"
]


def extract_experience(text):

    doc = nlp(text)

    experiences = []

    for sent in doc.sents:

        sentence = sent.text.strip()

        for title in JOB_TITLES:

            if title.lower() in sentence.lower():

                experiences.append(sentence)

    return list(set(experiences))
