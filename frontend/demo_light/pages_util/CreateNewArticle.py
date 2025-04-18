import os
import time
import requests
import demo_util
import streamlit as st
from demo_util import (
    DemoFileIOHelper,
    DemoTextProcessingHelper,
    DemoUIHelper,
    truncate_filename,
)
def query_llama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",  # Update with correct API endpoint
            json={"model": "llama3.2:latest", "prompt": prompt}
        )
        if response.status_code == 200:
            return response.json().get("response", "No response from LLaMA")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to LLaMA: {e}"

def handle_not_started():
    if st.session_state["page3_write_article_state"] == "not started":
        _, search_form_column, _ = st.columns([2, 5, 2])
        with search_form_column:
            with st.form(key="search_form"):
                # Text input for the search topic
                DemoUIHelper.st_markdown_adjust_size(
                    content="Enter the topic you want to learn in depth:", font_size=18
                )
                st.session_state["page3_topic"] = st.text_input(
                    label="page3_topic", label_visibility="collapsed"
                )
                pass_appropriateness_check = True

                # Submit button for the form
                submit_button = st.form_submit_button(label="Research")
                # only start new search when button is clicked, not started, or already finished previous one
                if submit_button and st.session_state["page3_write_article_state"] in [
                    "not started",
                    "show results",
                ]:
                    if not st.session_state["page3_topic"].strip():
                        pass_appropriateness_check = False
                        st.session_state["page3_warning_message"] = (
                            "topic could not be empty"
                        )

                    st.session_state["page3_topic_name_cleaned"] = (
                        st.session_state["page3_topic"]
                        .replace(" ", "_")
                        .replace("/", "_")
                    )
                    st.session_state["page3_topic_name_truncated"] = truncate_filename(
                        st.session_state["page3_topic_name_cleaned"]
                    )
                    if not pass_appropriateness_check:
                        st.session_state["page3_write_article_state"] = "not started"
                        alert = st.warning(
                            st.session_state["page3_warning_message"], icon="⚠️"
                        )
                        time.sleep(5)
                        alert.empty()
                    else:
                        st.session_state["page3_write_article_state"] = "initiated"


def handle_initiated():
    if st.session_state["page3_write_article_state"] == "initiated":
        current_working_dir = os.path.join(demo_util.get_demo_dir(), "DEMO_WORKING_DIR")
        if not os.path.exists(current_working_dir):
            os.makedirs(current_working_dir)

        if "runner" not in st.session_state:
            demo_util.set_storm_runner()
        st.session_state["page3_current_working_dir"] = current_working_dir
        st.session_state["page3_write_article_state"] = "pre_writing"


def handle_pre_writing():
    if st.session_state["page3_write_article_state"] == "pre_writing":
        status = st.status(
            "I am brain**STORM**ing now to research the topic. (This may take 2-3 minutes.)"
        )
        with status:
            topic = st.session_state["page3_topic"]
            research_prompt = f"Research and generate an outline for the topic: {topic}"
            
            # Call LLaMA instead of OpenAI
            response = query_llama(research_prompt)

            if "Error" in response:
                st.error(response)
            else:
                st.session_state["page3_outline"] = response  # Store LLaMA output
                st.write("### Generated Outline:")
                st.write(response)  # Show output

            st.session_state["page3_write_article_state"] = "final_writing"
            status.update(label="brain**STORM**ing complete!", state="complete")



def handle_final_writing():
    if st.session_state["page3_write_article_state"] == "final_writing":
        with st.status(
            "Now I will connect the information I found for your reference. (This may take 4-5 minutes.)"
        ) as status:
            st.info(
                "Now I will connect the information I found for your reference. (This may take 4-5 minutes.)"
            )

            # Use LLaMA to generate the full article
            article_prompt = f"Write a detailed article based on the following outline:\n\n{st.session_state['page3_outline']}"
            response = query_llama(article_prompt)

            if "Error" in response:
                st.error(response)
            else:
                st.session_state["page3_article"] = response  # Store LLaMA article
                st.write("### Generated Article:")
                st.write(response)  # Display article

            st.session_state["page3_write_article_state"] = "prepare_to_show_result"
            status.update(label="Information synthesis complete!", state="complete")



def handle_prepare_to_show_result():
    if st.session_state["page3_write_article_state"] == "prepare_to_show_result":
        _, show_result_col, _ = st.columns([4, 3, 4])
        with show_result_col:
            if st.button("show final article"):
                st.session_state["page3_write_article_state"] = "completed"
                st.rerun()


def handle_completed():
    if st.session_state["page3_write_article_state"] == "completed":
        st.title(f"Generated Article: {st.session_state['page3_topic']}")

        # Display the generated article from LLaMA
        if "page3_article" in st.session_state:
            st.write(st.session_state["page3_article"])
        else:
            st.warning("No article generated yet.")


def create_new_article_page(query_llama):
    demo_util.clear_other_page_session_state(page_index=3)

    if "page3_write_article_state" not in st.session_state:
        st.session_state["page3_write_article_state"] = "not started"

    handle_not_started()

    handle_initiated()

    handle_pre_writing()

    handle_final_writing()

    handle_prepare_to_show_result()

    handle_completed()
