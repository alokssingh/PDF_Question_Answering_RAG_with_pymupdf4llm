
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Define the prompt template

custom_prompt = PromptTemplate(
    input_variables=["context", "question"],  # These are the expected variables
    template="""
    Use the following context to answer the question. Be concise and precise.
    Extract the answer to the following question from the provided text. Ensure the response is concise, accurate, and specific to the details mentioned in the text. Guidelines:
    - Provide only the answer. Do not include the question in the answer. If the information is not explicitly mentioned in the text, respond with: "not available". Avoid adding context, explanations, or assumptions. 
    - Keep the answer brief and exact.
    - Do not answer like the address of the datacenter is
    - If it asks for capacity or space, give the number or whatever is explicitly written in the text.
    - Example Question: Give me only the address of the datacenter? Include the complete address as mentioned in the text. If none are mentioned, respond with 'not available otherwise Coriander Avenue, London, E14 2AA, United Kingdom.


    Context: {context}
    Question: {question}
    Answer:
    """
)
"""
# if you want to RecursiveCharacterTextSplitter for chunking

def get_text_chunks(text, chunk_size=500, chunk_overlap=50):
    
    #Splits the input text into manageable chunks for processing.
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators="###", is_separator_regex=False)
    return [Document(page_content=chunk) for chunk in text_splitter.split_text(text)]
"""

"""def get_text_chunks(text, chunk_size=1000, chunk_overlap=20):
    
    #Splits the input text into manageable chunks for processing.
   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [Document(page_content=chunk) for chunk in text_splitter.split_text(text)]
"""
def get_text_chunks(text, chunk_size=1000, chunk_overlap=20):
    
    #Splits the input text into manageable chunks for processing.
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
    markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    md_header_splits = markdown_splitter.split_text(text)
    
    
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return md_header_splits


def format_docs(docs):
    """
    Formats a list of Document objects into a single string.
    """
    return "\n\n".join(doc.page_content for doc in docs)


def get_question_answers(text, questions):
    """
    Processes a list of questions and retrieves answers using a RetrievalQA chain.
    
    Parameters:
        plant_id (str): Identifier for the plant or context.
        text (str): The input text to be processed.
        questions (list): List of questions to be answered.
        openai_api_key (str): OpenAI API key for authentication.

    Returns:
        dict: A dictionary containing answers and their corresponding contexts.
    """
    # Split the text into smaller chunks
    docs = get_text_chunks(text)

    # Generate embeddings and store in a FAISS vector store
    embeddings =  OllamaEmbeddings(model='phi3')
    
    # building vector database using either FAISS or Chroma
    #vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore = Chroma.from_documents(docs, embeddings)


    # Initialize the Chat model
    model = ChatOllama(model='phi3')
    


    # Create a RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
    llm=model,  # Your LLM instance
    chain_type="stuff",  # Chain type
    retriever=vectorstore.as_retriever(),  # Your retriever
    chain_type_kwargs={"prompt": custom_prompt},  # Pass the custom prompt
    return_source_documents=True  # Include source documents
)

    # Containers for storing results
    answers = []
    contexts = []

    # Process each question
    for question in questions:
        try:
            # Use the QA chain to get the answer
            result = qa_chain({"query": question})
            #print(result['result'])

            # Extract and append the results
            #print(result.get('result'))
            #print(question)
            #print(result.get('result', "not available"))
            
            answers.append(result.get('result', "not available"))
            contexts.append(result.get('source_documents', []))
        except Exception as e:
            print(f"Error processing question '{question}': {e}")
            answers.append("error")
            contexts.append([])

    # Prepare the result dictionary
    result_dict = {
        "answers": answers,
        "contexts": contexts
    } 

    return result_dict
