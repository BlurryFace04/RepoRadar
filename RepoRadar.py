import asyncio
import streamlit as st
from User import get_repos
from Opensource import get_projects
from Chroma import recommend
from linkpreview import link_preview


def get_link_preview(url):
    preview = link_preview(url)
    return preview.title, preview.description, preview.image


st.title('🦜🔗 RepoRadar')
prompt = st.text_input('Enter your GitHub username')

with st.expander("Enter your OpenAI API key for better recommendations"):
    api_key = st.text_input("API Key", type="password")

if prompt:
    status_placeholder = st.empty()

    status_placeholder.text('Crawling your repositories...')
    user_details, languages_topics = get_repos(prompt)

    status_placeholder.text('Crawling open source projects...')
    unique_repos = asyncio.run(get_projects(languages_topics))

    status_placeholder.text('Generating recommendations...')

    if api_key:
        urls = recommend(user_details, unique_repos, api_key)
    else:
        urls = recommend(user_details, unique_repos)

    status_placeholder.empty()

    with st.expander("Recommended Projects"):
        for url in urls:
            if url:
                title, description, image = get_link_preview(url)

                if image:
                    st.markdown(f'[<img src="{image}" width="300" align="center"/>]({url})', unsafe_allow_html=True)
                else:
                    st.markdown(f'[{title}]({url})', unsafe_allow_html=True)
