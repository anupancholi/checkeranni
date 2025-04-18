import os
import requests
import streamlit as st

script_dir = os.path.dirname(os.path.abspath(__file__))
wiki_root_dir = os.path.dirname(os.path.dirname(script_dir))

import demo_util
from pages_util import MyArticles, CreateNewArticle
from streamlit_float import *
from streamlit_option_menu import option_menu


# Function to call the LLaMA backend API instead of OpenAI
# def query_llama(prompt):
#     try:
#         response = requests.post(
#             "http://localhost:11434/generate",  # Your backend API
#             json={"prompt": prompt}
#         )
#         if response.status_code == 200:
#             return response.json()["response"]
#         else:
#             return "Error: LLaMA response failed"
#     except Exception as e:
#         return f"Error connecting to LLaMA: {e}"
def query_llama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/generate",
            json={"prompt": prompt}
        )
        return response.json().get("response", "No response")
    except Exception as e:
        return f"Error connecting to LLaMA: {e}"


def main():
    global database
    # st.set_page_config(layout="wide")
    st.set_page_config(
    page_title="WEBpedia",  # <-- Change this to whatever title you want
    layout="wide"
)

    if "first_run" not in st.session_state:
        st.session_state["first_run"] = True

    # Remove OpenAI API setup
    # if st.session_state["first_run"]:
    #     for key, value in st.secrets.items():
    #         if isinstance(value, str):
    #             os.environ[key] = value

    # Initialize session_state
    if "selected_article_index" not in st.session_state:
        st.session_state["selected_article_index"] = 0
    if "selected_page" not in st.session_state:
        st.session_state["selected_page"] = 0
    if st.session_state.get("rerun_requested", False):
        st.session_state["rerun_requested"] = False
        st.rerun()

    st.write(
        "<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True
    )

    menu_container = st.container()
    with menu_container:
        pages = ["My Articles", "Create New Article"]
        styles = {"container": {"padding": "0.2rem 0", "background-color": "#22222200"}}
        menu_selection = option_menu(
            None,
            pages,
            icons=["house", "search"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            manual_select=st.session_state.selected_page,
            styles=styles,
            key="menu_selection",
        )

        if st.session_state.get("manual_selection_override", False):
            menu_selection = pages[st.session_state["selected_page"]]
            st.session_state["manual_selection_override"] = False
            st.session_state["selected_page"] = None

        if menu_selection == "My Articles":
            demo_util.clear_other_page_session_state(page_index=2)
            MyArticles.my_articles_page()
        elif menu_selection == "Create New Article":
            demo_util.clear_other_page_session_state(page_index=3)
            CreateNewArticle.create_new_article_page(query_llama)  # Pass LLaMA function


if __name__ == "__main__":
    main()
