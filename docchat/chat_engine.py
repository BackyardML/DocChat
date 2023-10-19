import logging
from pathlib import Path

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ChatEngine:
    def __init__(self, docs):
        chatbot = ChatOpenAI(temperature=0)
        embeddings = OpenAIEmbeddings()

        documents = self.load_documents(docs if len(docs) > 1 else [docs])

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=40)
        documents = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 2}
        )
        self.qa = ConversationalRetrievalChain.from_llm(chatbot, retriever)

    @staticmethod
    def load_documents(docs):
        pdf_loaders = [
            DirectoryLoader(str(Path(doc.name).parent), glob="**/*.pdf") for doc in docs
        ]
        txt_loaders = [
            DirectoryLoader(str(Path(doc.name).parent), glob="**/*.txt") for doc in docs
        ]

        documents = []
        for loader in pdf_loaders:
            documents.extend(loader.load())
        for loader in txt_loaders:
            documents.extend(loader.load())

        num_docs = len(documents)
        num_chars = sum([len(document.page_content) for document in documents])

        LOGGER.debug(f"You have {num_docs} document(s) in your document(s)")
        LOGGER.debug(f"There are {num_chars} characters in your document(s)")

        return documents

    def run(self, query, chat_history):
        result = self.qa({"question": query, "chat_history": chat_history})
        return result["answer"]
