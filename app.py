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


from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import json
from difflib import get_close_matches

app = FastAPI(title="Chatbot BDM-SA")

# Charger la FAQ catégorisée
with open("faq.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

# Extraire les catégories disponibles
categories_list = list(set([q["category"] for q in faq_data]))


def find_answers(user_question: str, category: str = None):
    """
    Recherche les réponses proches d'une question dans la FAQ.
    - user_question: question posée par l'utilisateur
    - category: catégorie filtrée (optionnelle)
    """
    # Filtrer par catégorie si spécifiée
    if category and category in categories_list:
        filtered_faq = [q for q in faq_data if q["category"] == category]
    else:
        filtered_faq = faq_data

    # Extraire les questions
    questions_list = [q["question"] for q in filtered_faq]

    # Chercher questions proches
    matches = get_close_matches(user_question, questions_list, n=3, cutoff=0.5)

    responses = []
    if matches:
        for m in matches:
            ans = next(item["answer"] for item in filtered_faq if item["question"] == m)
            responses.append({"question": m, "answer": ans})
    else:
        # Aucune correspondance trouvée
        responses.append({"question": None,
                          "answer": "Désolé, je ne peux pas répondre à cette question. Veuillez contacter un agent."})
    return responses


# Endpoint principal du chatbot
@app.get("/chatbot")
async def chatbot(
    question: str = Query(..., description="Question posée par l'utilisateur"),
    category: str = Query(None, description="Catégorie de question (optionnelle)")
):
    """
    Retourne les réponses proches pour une question, optionnellement filtrée par catégorie.
    """
    responses = find_answers(question, category)
    return JSONResponse({
        "question_asked": question,
        "category": category if category else "Toutes catégories",
        "responses": responses
    })


# Serveur des fichiers statiques (index.html)
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Test simple pour vérifier que le serveur fonctionne
@app.get("/")
async def root():
    return {"message": "Chatbot BDM-SA est opérationnel. Accédez à /static/index.html pour l'interface."}
