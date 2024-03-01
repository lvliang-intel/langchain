import torch
import requests
import argparse
import intel_extension_for_pytorch as ipex
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Redis
from intel_extension_for_transformers.langchain.embeddings import HuggingFaceBgeEmbeddings
from intel_extension_for_transformers.langchain.vectorstores import Chroma
from intel_extension_for_transformers.neural_chat.pipeline.plugins.retrieval.parser.parser import DocumentParser
from config import EMBED_MODEL, INDEX_NAME, INDEX_SCHEMA, REDIS_URL, REDIS_SCHEMA


def download_doc(url, file_path):
    response = requests.get(url)

    if response.status_code == 200:
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"File downloaded successfully as {file_path}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")


def construct_chroma_db(file_path):
    document_parser = DocumentParser()
    data_collection=document_parser.load(input=file_path)
    documents = []
    for data, meta in data_collection:
        doc = Document(page_content=data, metadata={"source":meta})
        documents.append(doc)

    embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-base-en-v1.5")
    embeddings.client= ipex.optimize(embeddings.client.eval(), dtype=torch.bfloat16)
    knowledge_base = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory='./output')


def construct_redis_db(file_path):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=100, add_start_index=True
    )
    loader = UnstructuredFileLoader(file_path, mode="single", strategy="fast")
    chunks = loader.load_and_split(text_splitter)
    print("Done preprocessing. Created", len(chunks), "chunks of the original pdf")  # noqa: T201
    
    embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    rds = Redis.from_texts(
        texts=[f"Company: Intel. " + chunk.page_content for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embedding=embedder,
        index_name=INDEX_NAME,
        redis_url=REDIS_URL,
    )
    print(f"docs: {rds}")
    rds.write_schema(REDIS_SCHEMA)
    print(f"Redis db created.")


if __name__ == "__main__":
    url = "https://d1io3yog0oux5.cloudfront.net/_897efe2d574a132883f198f2b119aa39/intel/db/888/8941/file/412439%281%29_12_Intel_AR_WR.pdf"
    file_path = "./Intel_AR_WR.pdf"
    download_doc(url, file_path)

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default="chroma", help='The vector db you choose, must be in [chroma, redis].')
    args = parser.parse_args()
    print(f"Using vectordb [{args.db}]")

    if args.db.lower() == "chroma":
        construct_chroma_db(file_path)
    elif args.db.lower() == "redis":
        construct_redis_db(file_path)
