# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import json
# from difflib import get_close_matches

# app = FastAPI()

# # Charger FAQ
# with open("faq.json", "r", encoding="utf-8") as f:
#     faq_data = json.load(f)

# # Endpoint chatbot
# @app.get("/chatbot")
# async def chatbot(question: str):
#     questions_list = [q["question"] for q in faq_data]
#     match = get_close_matches(question, questions_list, n=1, cutoff=0.5)
#     if match:
#         answer = next(item["answer"] for item in faq_data if item["question"] == match[0])
#     else:
#         answer = "Désolé, je ne peux pas répondre à cette question. Veuillez contacter un agent."
#     return JSONResponse({"question": question, "answer": answer})

# # Interface web statique
# app.mount("/static", StaticFiles(directory="templates"), name="static")





# :::::::::::::::::::::::::::::::::::::::::VERSION 2:::::::::::::::::::::::




# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import json
# from difflib import get_close_matches

# app = FastAPI()

# # Charger FAQ catégorisée
# with open("faq.json", "r", encoding="utf-8") as f:
#     faq_data = json.load(f)

# # Créer des listes pour la recherche
# questions_list = [q["question"] for q in faq_data]
# categories_list = list(set([q["category"] for q in faq_data]))

# # Endpoint chatbot
# @app.get("/chatbot")
# async def chatbot(question: str = Query(..., description="Question posée par l'utilisateur"), category: str = None):
#     """
#     Retourne les réponses proches pour une question, optionnellement filtrée par catégorie.
#     """
#     # Filtrer par catégorie si spécifiée
#     if category and category in categories_list:
#         filtered_faq = [q for q in faq_data if q["category"] == category]
#     else:
#         filtered_faq = faq_data

#     # Extraire les questions filtrées
#     filtered_questions = [q["question"] for q in filtered_faq]

#     # Chercher les questions proches
#     matches = get_close_matches(question, filtered_questions, n=3, cutoff=0.5)  # jusqu'à 3 réponses proches

#     if matches:
#         # Construire la liste des réponses
#         responses = []
#         for m in matches:
#             ans = next(item["answer"] for item in filtered_faq if item["question"] == m)
#             responses.append({"question": m, "answer": ans})
#     else:
#         responses = [{"question": None, "answer": "Désolé, je ne peux pas répondre à cette question. Veuillez contacter un agent."}]

#     return JSONResponse({
#         "question_asked": question,
#         "category": category if category else "Toutes catégories",
#         "responses": responses
#     })

# # Interface web statique
# app.mount("/static", StaticFiles(directory="templates"), name="static")




# :::::::::::::::::::::::::::::::::::::::::VERSION 3:::::::::::::::::::::::


# from fastapi import FastAPI, Query
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# import json
# from difflib import get_close_matches

# app = FastAPI(title="Chatbot BDM-SA")

# # Charger la FAQ catégorisée
# with open("faq.json", "r", encoding="utf-8") as f:
#     faq_data = json.load(f)

# # Extraire les catégories disponibles
# categories_list = list(set([q["category"] for q in faq_data]))


# def find_answers(user_question: str, category: str = None):
#     """
#     Recherche les réponses proches d'une question dans la FAQ.
#     - user_question: question posée par l'utilisateur
#     - category: catégorie filtrée (optionnelle)
#     """
#     # Filtrer par catégorie si spécifiée
#     if category and category in categories_list:
#         filtered_faq = [q for q in faq_data if q["category"] == category]
#     else:
#         filtered_faq = faq_data

#     # Extraire les questions
#     questions_list = [q["question"] for q in filtered_faq]

#     # Chercher questions proches
#     matches = get_close_matches(user_question, questions_list, n=3, cutoff=0.5)

#     responses = []
#     if matches:
#         for m in matches:
#             ans = next(item["answer"] for item in filtered_faq if item["question"] == m)
#             responses.append({"question": m, "answer": ans})
#     else:
#         # Aucune correspondance trouvée
#         responses.append({"question": None,
#                           "answer": "Désolé, je ne peux pas répondre à cette question. Veuillez contacter un agent."})
#     return responses


# # Endpoint principal du chatbot
# @app.get("/chatbot")
# async def chatbot(
#     question: str = Query(..., description="Question posée par l'utilisateur"),
#     category: str = Query(None, description="Catégorie de question (optionnelle)")
# ):
#     """
#     Retourne les réponses proches pour une question, optionnellement filtrée par catégorie.
#     """
#     responses = find_answers(question, category)
#     return JSONResponse({
#         "question_asked": question,
#         "category": category if category else "Toutes catégories",
#         "responses": responses
#     })


# # Serveur des fichiers statiques (index.html)
# app.mount("/static", StaticFiles(directory="templates"), name="static")

# # Test simple pour vérifier que le serveur fonctionne
# @app.get("/")
# async def root():
#     return {"message": "Chatbot BDM-SA est opérationnel. Accédez à /static/index.html pour l'interface."}




# :::::::::::::::::::::::::::::::::::::::::VERSION 3:::::::::::::::::::::::
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
import uuid
import datetime
import os

# =============================
# Initialisation API
# =============================
app = FastAPI(title="Chatbot Bancaire Intelligent BDM-SA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# Fichiers
# =============================
FAQ_FILE = "faq.json"
INTENTS_FILE = "intents.json"
LOG_FILE = "logs.json"

# Créer logs.json s'il n'existe pas
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# =============================
# Chargement données
# =============================
with open(FAQ_FILE, encoding="utf-8") as f:
    faq = json.load(f)

with open(INTENTS_FILE, encoding="utf-8") as f:
    intents = json.load(f)

questions = [item["question"] for item in faq]

# =============================
# Modèle NLP
# =============================
model = SentenceTransformer("all-MiniLM-L6-v2")
faq_embeddings = model.encode(questions, convert_to_tensor=True)

# =============================
# Mémoire conversationnelle
# =============================
sessions = {}

# =============================
# Fonctions utilitaires
# =============================
def detect_intent(text):
    text = text.lower()
    for intent, data in intents.items():
        if any(keyword in text for keyword in data["keywords"]):
            return intent
    return None

def semantic_search(text, threshold=0.45):
    emb = model.encode([text])
    scores = cosine_similarity(emb, faq_embeddings)[0]
    idx = np.argmax(scores)
    if scores[idx] < threshold:
        return None
    return faq[idx]

def log_interaction(session_id, question, intent, status):
    log_entry = {
        "session_id": session_id,
        "question": question,
        "intent": intent,
        "status": status,  # success | clarification | fallback
        "timestamp": datetime.datetime.now().isoformat()
    }

    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)

# =============================
# Endpoint principal Chatbot
# =============================
@app.get("/chatbot")
def chatbot(question: str, session_id: str = None):

    # Création ou récupération session
    if not session_id:
        session_id = str(uuid.uuid4())

    memory = sessions.get(session_id)

    # ===== CAS 1 : clarification en cours =====
    if memory and memory["awaiting"]:
        intent = memory["intent"]
        full_question = intent + " " + question

        result = semantic_search(full_question)
        sessions.pop(session_id)

        if result:
            log_interaction(session_id, question, intent, "success")
            return {
                "session_id": session_id,
                "responses": [{
                    "answer": result["answer"],
                    "suggestions": []
                }]
            }

        log_interaction(session_id, question, intent, "fallback")
        return {
            "session_id": session_id,
            "responses": [{
                "answer": "Merci pour la précision. Un agent BDM-SA peut vous assister.",
                "suggestions": []
            }]
        }

    # ===== CAS 2 : nouvelle intention détectée =====
    intent = detect_intent(question)
    if intent:
        sessions[session_id] = {
            "intent": intent,
            "awaiting": True
        }

        log_interaction(session_id, question, intent, "clarification")

        return {
            "session_id": session_id,
            "responses": [{
                "answer": intents[intent]["clarification"],
                "suggestions": intents[intent]["suggestions"]
            }]
        }

    # ===== CAS 3 : réponse directe =====
    result = semantic_search(question)
    if result:
        log_interaction(session_id, question, None, "success")
        return {
            "session_id": session_id,
            "responses": [{
                "answer": result["answer"],
                "suggestions": []
            }]
        }

    # ===== CAS 4 : fallback =====
    log_interaction(session_id, question, None, "fallback")
    return {
        "session_id": session_id,
        "responses": [{
            "answer": "Je n’ai pas compris votre demande. Souhaitez-vous contacter un agent BDM-SA ?",
            "suggestions": []
        }]
    }

# =============================
# Endpoint Analytics (Dashboard)
# =============================
@app.get("/analytics")
def analytics():
    with open(LOG_FILE, encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    fallback = 0
    intent_stats = {}

    for entry in data:
        if entry["status"] == "fallback":
            fallback += 1
        if entry["intent"]:
            intent_stats[entry["intent"]] = intent_stats.get(entry["intent"], 0) + 1

    return {
        "total_questions": total,
        "fallback_count": fallback,
        "intent_distribution": intent_stats
    }

# =============================
# Health check
# =============================
@app.get("/")
def root():
    return {"status": "Chatbot bancaire BDM-SA opérationnel"}
