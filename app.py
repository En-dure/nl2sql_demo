from Vllm import Vllm
from config import vllm_config, mysql_config
import streamlit as st
import json
import pandas as pd


vllm = Vllm(vllm_config)
vllm.connect_to_mysql(**mysql_config)

def init_state():
    # Initialize session state variables
    if 'question' not in st.session_state:   #问题
        st.session_state.question = ""
    if 'reget_info' not in st.session_state:   #补充信息
        st.session_state.reget_info = ""
    if "semantic_prompt" not in st.session_state:
        st.session_state.semantic_prompt = ''
    if "semantic_result" not in st.session_state:
        st.session_state.semantic_result = ''
    if "semantic_false_result" not in st.session_state:
        st.session_state.semantic_false_result = ''
    if "messages" not in st.session_state:   #历史信息
        st.session_state.messages = []
    if "fault" not in st.session_state:    #语义分解错误
        st.session_state.fault = False
    if "confirm" not in st.session_state:  #用户确认
        st.session_state.confirm = False
    if "sql_error" not in st.session_state:
        st.session_state.sql_error = False
    if "thinking_result" not in st.session_state:
        st.session_state.thinking_result = ''
    if "times" not in st.session_state:   #意图识别次数
        st.session_state.times = 0
    if "thinking_end" not in st.session_state:
        st.session_state.thinking_end = False
    if "sql_attemp" not in st.session_state:
        st.session_state.sql_attemp = 0
    if "sql_df" not in st.session_state:
        st.session_state.sql_df = pd.DataFrame()
    if "sql_end" not in st.session_state:
        st.session_state.sql_end = False
    if "sql" not in st.session_state:
        st.session_state.sql = None
def process_input(question):
    """Process the user input and update the session state accordingly."""
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    if not st.session_state.question and not st.session_state.reget_info:
        st.session_state.question = question
    elif st.session_state.question and (not st.session_state.reget_info):
        st.session_state.reget_info = question
    semantic_prompt = vllm.get_semantic_prompt(st.session_state.question, reget_info=st.session_state.reget_info)
    st.session_state.semantic_prompt = semantic_prompt
    text = vllm.submit_semantic_prompt(semantic_prompt)
    try:
        text_json = json.loads(text)
        if text_json["Done"] == "True":
            st.session_state.question = text_json["question"]
            with st.chat_message("assistant"):
                st.session_state.messages.append({"role": "assistant", "content": text_json["result"]})
            st.session_state.semantic_result = text_json["result"]
            st.session_state.fault = False  # Reset fault flag if successful
        else:
            st.session_state.semantic_false_result = text_json["result"]
            with st.chat_message("assistant"):
                st.session_state.messages.append({"role": "assistant", "content": text_json["result"]})
            st.session_state.fault = True  # Set fault flag to True if needs re-input
    except Exception as e:
        with st.chat_message("assistant"):
            st.markdown("发生错误，请重新输入您的问题。")
            st.markdown(str(e))
        st.session_state.fault = True  # Set fault flag to True if an exception occurs

def thinking(question, semantic_result):
    thinking_prompt = vllm.get_thinking_prompt(question, semantic_result)
    thinking_result = vllm.submit_thinking_prompt(thinking_prompt)
    try:
        thinking_result = json.loads(thinking_result)
        if thinking_result["Done"] == "False":
            st.markdown(thinking_result["res"])
            return
        else:
            thinking_result = thinking_result["res"]
            st.markdown(thinking_result)
            st.session_state.thinking_end = True
            st.session_state.thinking_result = thinking_result
    except Exception as e:
        return

def sql(question, think_result, error):
    sql_prompt = vllm.get_sql_prompt(question, think_result, error)
    sql =vllm.submit_prompt(sql_prompt)
    st.session_state.sql = sql
    y_or_n, run_sql_result = vllm.run_sql(sql)
    if not y_or_n:
        st.session_state.sql_error = run_sql_result
        return
    if not isinstance(run_sql_result, pd.DataFrame):
        if not run_sql_result:
            return
    st.session_state.sql_df = run_sql_result
    st.session_state.sql_end = True
    return

def clear_st_state():
    st.session_state.question = ""
    st.session_state.reget_info = ""
    st.session_state.semantic_prompt = ''
    st.session_state.semantic_result = ''
    st.session_state.semantic_false_result = ''
    st.session_state.messages = []
    st.session_state.fault = False
    st.session_state.confirm = False
    st.session_state.sql_erroe = False
    st.session_state.thinking_result = ''
    st.session_state.sql = None
    st.session_state.times = 0
    st.session_state.thinking_end = False
    st.session_state.sql_attemp = 0
    st.session_state.sql_df = pd.DataFrame()
    st.session_state.sql_end = False
    st.session_state.sql = None

def main():
    init_state()
    if question := st.chat_input("请输入"):
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        # 处理输入的问题
        process_input(question)
        st.session_state.times += 1
        # 如果输入次数达到2次，清空状态
        if st.session_state.times == 2:
            st.session_state.messages = []
            st.session_state.question = ''
            st.session_state.reget_info = ''
            st.session_state.times = 0
        # 如果没有语义分解错误
        if st.session_state.fault == False:
            confirm_prompt = vllm.get_confirm_prompt(st.session_state.semantic_result)
            confirm_result = vllm.submit_confirm_prompt(confirm_prompt)

            # 执行思考过程直到完成
            while not st.session_state.thinking_end:
                thinking(st.session_state.question, st.session_state.semantic_result)
            with st.chat_message("assistant"):
                st.markdown(st.session_state.thinking_result)
            # 尝试执行 SQL 查询，最多重试 3 次
            while st.session_state.sql_attemp <= 3:
                sql(st.session_state.question, st.session_state.thinking_result, st.session_state.sql_error)
                if st.session_state.sql_end:
                    break
                else:
                    st.session_state.sql_attemp += 1
            with st.chat_message("assistant"):
                st.markdown(st.session_state.sql)
            # 显示 SQL 查询结果
            st.dataframe(st.session_state.sql_df)
            clear_st_state()
main()