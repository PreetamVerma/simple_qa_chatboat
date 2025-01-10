from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from nltk.tokenize import sent_tokenize
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np 
import os 
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")





# Load Sentence-Transformers embeddings model
embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')



class Pinecone_Connector():

    def __init__(self, index_name="chatdemo"):
        self.index_name= index_name
        self.connection_obj = self.get_index(self.index_name)


    def chunk_text(self, text:str, chunk_size:int):
        """
        Splits the text into chunks of approximately `chunk_size` characters, 
        ensuring chunks don't split sentences.
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []

        current_length = 0
        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length > chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def get_index(self, index_name:str):
        pc = Pinecone(api_key=PINECONE_API_KEY)
        return  pc.Index(index_name)

    def pdf_to_text(self, pdf_path: str) -> str:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        text = page.extract_text()
        return text

    def save_to_pincone(self, doc_id:str, text: str, metadata):
        chunks = self.chunk_text(text, chunk_size=400)
        vectors = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            embedding = embeddings_model.encode(chunk)
            metadata.update({"document_id": doc_id, "chunk": chunk})
            vectors.append((chunk_id, embedding, metadata))
        self.connection_obj.upsert(vectors)
        return 

    def insert_pdf_data(self, pdf_path: str, doc_id: str, metadata: dict):
        text = self.pdf_to_text(pdf_path)
        self.save_to_pincone(doc_id, text, metadata)


    def search_documents(self, query: str, email_id: str):
        response = ''
        vector  = embeddings_model.encode(query)
        vector = vector.astype(float).tolist()
        results= self.connection_obj.query(vector=vector,top_k=5, include_values=False, include_metadata=True, filter={"email_id": {"$in": [email_id]}})
        results = results.to_dict()['matches']
        response_arr = [result['metadata']['chunk'] for result in results if email_id in result['metadata']['email_id']]
        if response_arr:
           response=  '\n'.join(response_arr)
        return response 
    
if __name__ == "__main__":
    
    obj = Pinecone_Connector()
    # input_file_dir = "/Users/preetamverma/Projects/simple_qa_chatboat/con_chatboat/data"
    # file_access_db = {"adani.pdf":["alice@email.com"], 'hdfcbank.pdf':["bob@email.com"], 'icicibank.pdf':["bob@email.com","charlie@email.com"], 'sbi.pdf':["charlie@email.com"]}



    # for file_name, email_access_users in  file_access_db.items():
    #     file_path = os.path.join(input_file_dir, file_name)
    #     metadata = {"email_id":email_access_users, "company":file_name.split(".pdf")[0]}     
    #     obj.insert_pdf_data(file_path, doc_id=file_name, metadata=metadata)


    # query = "Adani new research."
    # email_id = "alice@email.com"
    # print (obj.search_documents(query, email_id))