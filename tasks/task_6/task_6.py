import sys
import os
import tempfile
import uuid

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader

sys.path.append(os.path.abspath('../../'))

from tasks.task_3.task_3 import DocumentProcessor
from tasks.task_4.task_4 import EmbeddingClient
from tasks.task_5.task_5 import ChromaCollectionCreator

f"""
Task: Build a Quiz Builder with Streamlit and LangChain

Overview:
In this task, you will leverage your skills acquired from previous tasks to create a "Quiz Builder" application utilizing Streamlit. This interactive application enables users to upload documents, designate a quiz topic, select a number of questions, and subsequently generate a quiz based on the uploaded document contents.

Components to Integrate:
- DocumentProcessor: A class developed in Task 3 for processing uploaded PDF documents.
- EmbeddingClient: A class from Task 4 dedicated to embedding queries.
- ChromaCollectionCreator: A class from Task 5 responsible for creating a Chroma collection derived from the processed documents.

Step-by-Step Instructions:
1. Begin by initializing an instance of the `DocumentProcessor` and invoke the `ingest_documents()` method to process the uploaded PDF documents.

2. Configure and initialize the `EmbeddingClient` with the specified model, project, and location details as provided in the `embed_config`.

3. Instantiate the `ChromaCollectionCreator` using the previously initialized `DocumentProcessor` and `EmbeddingClient`.

4. Utilize Streamlit to construct a form. This form should prompt users to input the quiz's topic and select the desired number of questions via a slider component.

5. Following the form submission, employ the `ChromaCollectionCreator` to forge a Chroma collection from the documents processed earlier.

6. Enable users to input a query pertinent to the quiz topic. Utilize the generated Chroma collection to extract relevant information corresponding to the query, which aids in quiz question generation.

Implementation Guidance:
- Deploy Streamlit's widgets such as `st.header`, `st.subheader`, `st.text_input`, and `st.slider` to craft an engaging form. This form should accurately capture the user's inputs for both the quiz topic and the number of questions desired.

- Post form submission, verify that the documents have been processed and that a Chroma collection has been successfully created. The build-in methods will communicate the outcome of these operations to the user through appropriate feedback.

- Lastly, introduce a query input field post-Chroma collection creation. This field will gather user queries for generating quiz questions, showcasing the utility of the Chroma collection in sourcing information relevant to the quiz topic.

"""

if __name__ == "__main__":
    st.header("Quizzify")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "PROJECT-ID-HERE",
        "location": "REGION"
    }
    processor = DocumentProcessor()  # Initialize from Task 3

    embed_client = EmbeddingClient(**embed_config)  # Initialize from Task 4

    chroma_creator = ChromaCollectionCreator(processor, embed_client)  # Initialize the ChromaCreator from Task 5

    with st.form("Load Data to Chroma"):
        st.subheader("Quiz Builder")
        st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

        uploaded_files = st.file_uploader(
            label="Upload multiple PDF files.",
            type=['pdf'],
            accept_multiple_files=True
        )
        # Topic input
        topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")

        # Number of questions slider
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

        submitted = st.form_submit_button("Generate a Quiz!")
        if submitted:
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    try:
                        # Generate a unique identifier to append to the file's original name
                        unique_id = uuid.uuid4().hex
                        original_name, file_extension = os.path.splitext(uploaded_file.name)
                        temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                        temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                        # Write the uploaded PDF to a temporary file
                        with open(temp_file_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())

                        # Step 2: Process the temporary file
                        loader = PyPDFLoader(temp_file_path)
                        document = loader.load()

                        # Step 3: Then, Add the extracted pages to the 'pages' list.
                        for page in document:
                            processor.pages.append(page.page_content)

                        # Clean up by deleting the temporary file.
                        os.unlink(temp_file_path)
                    except Exception as e:
                        st.error(f"Error processing file {uploaded_file.name}: {e}")

                st.write(f"Total pages processed: {len(processor.pages)}")

                # Create the Chroma collection
                chroma_creator.create_chroma_collection()
                if chroma_creator.db:
                    # st.success("Successfully created Chroma Collection!", icon="✅")

                    # Query the Chroma collection for the topic input
                    document = chroma_creator.query_chroma_collection(topic_input)

                    # Display the result if a document is found
                    if document:
                        st.success("Successfully created Chroma Collection!", icon="✅")
                        st.empty()
                        st.header("Query Chroma for Topic, Top Document: ")
                        st.write(document)
                    else:
                        st.error("No document found for the given topic.", icon="🚨")
                else:
                    st.error("Failed to create Chroma Collection!", icon="🚨")

            else:
                st.error("Please upload at least one PDF file.", icon="🚨")
# document = None
# if chroma_creator.db:
#     document = chroma_creator.query_chroma_collection(topic_input)
#
# if document:
#     st.empty()
#     st.header("Query Chroma for Topic, Top Document: ")
#     st.write(document)
