from config import  mysql_config
from rag_sql import RAG_SQL


def main():
    rag = RAG_SQL()
    question = "1到2月蔡明和倪海键的耗占比"
    rag.example_info = rag.get_similar_examples(question)
    rag.connect_to_mysql(**mysql_config)
    rag.ask(question)

if  __name__  == "__main__":
    main()

