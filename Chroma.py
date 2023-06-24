import chromadb
import random
from chromadb.utils import embedding_functions


def recommend(user_details, unique_repos, api_key=None):
    recommendations = []

    client = chromadb.Client()

    if api_key:
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-ada-002"
        )
        collection = client.create_collection("project_collection", embedding_function=openai_ef)
    else:
        collection = client.create_collection("project_collection")

    projects = list(unique_repos.values())

    for project in projects:
        document = f"{project['full_name']}: {project['description']}"
        collection.add(
            documents=[document],
            ids=[project['full_name']],
        )

    for user_project in user_details:
        document = f"{user_project['project_name']}: {user_project['description']}"
        results = collection.query(
            query_texts=[document],
            n_results=5,
        )
        try:
            recommended_project_id = random.choice(results['ids'][0])
            recommendations.append(f"https://www.github.com/{recommended_project_id}")
        except IndexError:
            print(f"No recommendations found for project {user_project['project_name']}. Continuing with next project.")
            continue

    return recommendations
