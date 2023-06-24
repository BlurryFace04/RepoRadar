import asyncio
from aiohttp import ClientSession
from datetime import datetime


class Octokit:
    def __init__(self, auth, session):
        self.auth = auth
        self.session = session

    async def request(self, method, url, params=None):
        headers = {
            'Authorization': 'Bearer ' + self.auth + 'A',
            'Accept': 'application/vnd.github+json',
        }

        url = 'https://api.github.com' + url

        while True:
            async with self.session.request(method, url, headers=headers, params=params) as response:
                if response.status == 403:
                    reset_time = datetime.fromtimestamp(int(response.headers["X-RateLimit-Reset"]))
                    sleep_time = (reset_time - datetime.now()).total_seconds() + 5
                    await asyncio.sleep(sleep_time)
                else:
                    response.raise_for_status()
                    return await response.json()


async def search_repositories(octokit, params):
    response = await octokit.request('GET', '/search/repositories', params)
    unique_repos = {}

    while len(response['items']) > 0 and params['page'] <= 10:
        for item in response['items']:
            if item['id'] not in unique_repos:
                unique_repos[item['id']] = {
                    "full_name": item['full_name'],
                    "description": item['description']
                }

        params['page'] += 1
        response = await octokit.request('GET', '/search/repositories', params)

    return unique_repos


async def main(languages_topics):
    unique_repos = {}

    async with ClientSession() as session:
        octokit = Octokit('github_pat_11APPCAYA0fhJgZNKgzWnv_LzCFAhBSqqiwKQqsFSXylIBnxOGTpBWKqJXces8JzOt3MOFK7KVvDtMB3h', session)

        languages = languages_topics['languages']
        topics = languages_topics['topics']

        tasks = []

        for language in languages:
            base_params = {
                'q': f'stars:>=2000 forks:>=500 language:{language} pushed:>=2023-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        for topic in topics:
            base_params = {
                'q': f'stars:>=2000 forks:>=500 topic:{topic} pushed:>=2023-01-01',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100,
                'page': 1,
            }

            help_wanted_params = base_params.copy()
            help_wanted_params['q'] += ' help-wanted-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, help_wanted_params)))

            good_first_issues_params = base_params.copy()
            good_first_issues_params['q'] += ' good-first-issues:>=1'
            tasks.append(asyncio.create_task(search_repositories(octokit, good_first_issues_params)))

        results = await asyncio.gather(*tasks)
        for result in results:
            unique_repos.update(result)

    return unique_repos


async def get_projects(languages_topics):
    return await main(languages_topics)
