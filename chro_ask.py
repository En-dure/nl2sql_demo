from config import  mysql_config
from rag_sql import RAG_SQL


def main():
    rag = RAG_SQL()
    question = "腰椎手术情况？"
    rag.example_info = rag.get_similar_examples(question)
    rag.connect_to_mysql(**mysql_config)
    rag.ask(question)

if  __name__  == "__main__":
    main()

