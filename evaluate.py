# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# def evaluate_answer(student_answer, correct_answer):
#     documents = [student_answer.lower(), correct_answer.lower()]
#     tfidf = TfidfVectorizer().fit_transform(documents)
#     similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
#     return round(similarity * 1, 2)
# from transformers import BertTokenizer, BertModel
# import torch
# from sklearn.metrics.pairwise import cosine_similarity

# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')

# def get_embedding(text):
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     return outputs.last_hidden_state.mean(dim=1)

# def evaluate_answer(student_answer, correct_answer):
#     student_emb = get_embedding(student_answer)
#     correct_emb = get_embedding(correct_answer)
#     similarity = cosine_similarity(student_emb, correct_emb)[0][0]
#     return round(similarity * 10, 2)  # Score out of 10

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_similarity(student_answer, correct_answer):
    emb1 = model.encode([student_answer])
    emb2 = model.encode([correct_answer])
    return cosine_similarity(emb1, emb2)[0][0]

def keyword_overlap(student_answer, correct_answer):
    vectorizer = TfidfVectorizer().fit([student_answer, correct_answer])
    vecs = vectorizer.transform([student_answer, correct_answer])
    return cosine_similarity(vecs[0:1], vecs[1:2])[0][0]

def evaluate_answer(student_answer, correct_answer):
    sem_sim = semantic_similarity(student_answer, correct_answer)
    key_sim = keyword_overlap(student_answer, correct_answer)
    final_score = (0.7 * sem_sim + 0.3 * key_sim) * 10  # out of 10
    return round(final_score, 2)

