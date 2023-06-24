import requests


def get_repos(username):
    headers = {
        'Authorization': 'Bearer github_pat_11APPCAYA0fhJgZNKgzWnv_LzCFAhBSqqiwKQqsFSXylIBnxOGTpBWKqJXces8JzOt3MOFK7KVvDtMB3h' + 'A',
        'User-Agent': 'Opensource-Recommender',
        'Accept': 'application/vnd.github+json',
    }

    languages_set = set()
    topics_set = set()
    user_details = []
    languages_topics = {}

    try:
        repos = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers)
        repos_data = repos.json()

        for repo in repos_data:
            if not repo['fork'] and (repo['description'] or repo['language'] or len(repo['topics']) > 0):
                languages = requests.get(repo['languages_url'], headers=headers)
                languages_data = languages.json()

                user_repo_details = {
                    'project_name': repo['name'],
                    'description': repo['description'],
                }
                user_details.append(user_repo_details)

                languages_set.update(languages_data.keys())
                topics_set.update(repo['topics'])

        languages_topics = {'languages': list(languages_set), 'topics': list(topics_set)}

    except Exception as e:
        print(e)

    return user_details, languages_topics
