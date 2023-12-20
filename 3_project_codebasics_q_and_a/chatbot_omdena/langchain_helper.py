from langchain.vectorstores import FAISS
from langchain.llms import GooglePalm
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env (especially openai api key)

# Create Google Palm LLM model
llm = GooglePalm(google_api_key=os.environ["GOOGLE_API_KEY"], temperature=0.1)
# # Initialize instructor embeddings using the Hugging Face model
instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
vectordb_file_path = "faiss_index"

def create_vector_db():
    # Load data from FAQ sheet
    loader = CSVLoader(file_path=r'C:\Users\tboyi\Projects\langchain\3_project_codebasics_q_and_a\chatbot_omdena\team_2_final_dataset.csv', source_column="prompt", encoding='ISO-8859-1')
    data = loader.load()

    # Create a FAISS instance for vector database from 'data'
    vectordb = FAISS.from_documents(documents=data,
                                    embedding=instructor_embeddings)

    # Save vector database locally
    vectordb.save_local(vectordb_file_path)


def evaluate_answer():
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(vectordb_file_path, instructor_embeddings)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)

    prompt_template = """given the following question , Evaluate the user-provided answer below based on its alignment with our 'response' column  in our dataset and provide consise feedback:
    context: {question}
    USER ANSWER: {answer}
    
    
   """

    # - Assess the accuracy and relevance of the answer.
    # - Offer brief pointers for improvement or correction if needed.
    # - Indicate if the answer is unrelated or incorrect but avoid providing the exact response from the dataset.
    # - If our dataset lacks a suitable response, simply state 'No data available for a detailed evaluation.'
    
    # Provide feedback in a brief and bullet-pointed format."""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "answer"]
    )

    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": PROMPT})

    return chain

if __name__ == "__main__":
    create_vector_db()
    chain = evaluate_answer()
    print(chain("I had a difficult client, but I couldn't do much about it. It was a tough situation."))