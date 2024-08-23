import streamlit as st
from config import mysql_config
from rag_sql import RAG_SQL


def main():
    rag = RAG_SQL()
    question = st.text_input("请输入问题：")
    if question:
        rag.index_info = rag.get_similar_index(question)
        rag.document_info = rag.get_similar_document(question)
        rag.example_info = rag.get_similar_examples(question)
        rag.connect_to_mysql(**mysql_config)
        result = rag.ask(question)
        st.sidebar.title("导航")
        st.write(result)
if __name__ == "__main__":
    main()

