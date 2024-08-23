from config import  mysql_config
from rag_sql import RAG_SQL


def main():
    rag = RAG_SQL()
    question = "2024年上半年骨科门急诊收入是多少？"
    rag.index_info = rag.get_similar_index(question)
    rag.document_info = rag.get_similar_document(question)
    rag.example_info = rag.get_similar_examples(question)
    rag.connect_to_mysql(**mysql_config)
    rag.ask(question)

if  __name__  == "__main__":
    main()

