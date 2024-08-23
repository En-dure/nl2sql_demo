from  Vllm import Vllm
from class_chromadb import Chromadb
from config import  vllm_config, chromadb_config, mysql_config
class RAG_SQL(Vllm, Chromadb):
    def __init__(self):
        Chromadb.__init__(self)
        Vllm.__init__(self,vllm_config)