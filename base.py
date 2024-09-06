import json
from abc import ABC, abstractmethod
from typing import List, Tuple, Union
import logging
from exceptions import DependencyError, ValidationError, ImproperlyConfigured
from config import base_config
import os
import pandas as pd
from decimal import Decimal


class Base(ABC):
    def __init__(self, config=None):
        self.config = base_config
        self.dialect = self.config.get("dialect", "MySQL")
        self.log_dir = self.config.get("log_dir", "log.log")
        self.logger = self.setup_logger(self.log_dir)
        self.prefix_dir = self.config.get("prefix_dir", "")
        self.index_file = self.config.get("index_file", "")
        self.document_file = self.config.get("document_file", "")
        self.example_file = self.config.get("example_file", "")
        self.example_json = self.config.get("example_json", "")
        self.SQL_DDL_file = self.config.get("SQL_DDL_file", "")
        self.run_sql_is_set = False
        self.relation_file = self.config.get("relation_file", "")
        self.get_extra_info()
        self.times = 1
        self.semantic_flag = 1
        self.MAX_TIMES = self.config.get("MAX_TIMES", 10)
        self.MAX_SQL_ATTEMPT = self.config.get("MAX_SQL_ATTEMPT", 3)
        self.AUTO_ADD_EXAMPLES = self.config.get("AUTO_ADD_EXAMPLES", False)

    def get_extra_info(self):
        self.ddl_info = self.get_ddl_info()
        self.index_info = self.get_index_info()
        self.example_info = self.get_example_info()
        self.document_info = self.get_document_info()
        self.relation_info = self.get_relation_info()

    def setup_logger(self, log_file: str, name: str = __name__, level: str = "INFO"):
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.setLevel(level)
            file_handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s ----- %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger

    def log(self, logger, message: str, title: str = "Info"):
        log_method = getattr(logger, title.lower(), logger.info)
        log_method(message)

    def connect_to_mysql(
            self,
            host: str = None,
            dbname: str = None,
            user: str = None,
            password: str = None,
            port: int = None,
            **kwargs
    ):
        try:
            import pymysql.cursors
        except ImportError:
            raise DependencyError(
                "You need to install required dependencies to execute this method,"
                " run command: \npip install PyMySQL"
            )
        if not host:
            host = os.getenv("HOST")

        if not host:
            raise ImproperlyConfigured("Please set your MySQL host")

        if not dbname:
            dbname = os.getenv("DATABASE")

        if not dbname:
            raise ImproperlyConfigured("Please set your MySQL database")

        if not user:
            user = os.getenv("USER")

        if not user:
            raise ImproperlyConfigured("Please set your MySQL user")

        if not password:
            password = os.getenv("PASSWORD")

        if not password:
            raise ImproperlyConfigured("Please set your MySQL password")

        if not port:
            port = os.getenv("PORT")

        if not port:
            raise ImproperlyConfigured("Please set your MySQL port")

        conn = None

        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=dbname,
                port=port,
                cursorclass=pymysql.cursors.DictCursor,
                **kwargs
            )
        except pymysql.Error as e:
            raise ValidationError(e)

        def run_sql_mysql(sql: str):
            if conn:
                try:
                    conn.ping(reconnect=True)
                    cs = conn.cursor()
                    cs.execute(sql)
                    results = cs.fetchall()

                    # Create a pandas dataframe from the results
                    df = pd.DataFrame(
                        results, columns=[desc[0] for desc in cs.description]
                    )
                    return True, df

                except pymysql.Error as e:
                    conn.rollback()
                    # raise ValidationError(e)
                    return False, e
                except Exception as e:
                    conn.rollback()
                    return False, e

        self.run_sql_is_set = True
        self.run_sql = run_sql_mysql

    def get_index_info(self):
        index_file_path = os.path.join(self.prefix_dir, self.index_file)
        if os.path.isfile(index_file_path):
            try:
                with open(index_file_path, "r", encoding="utf-8") as f:
                    index_info = f.read()
            except UnicodeDecodeError as e:
                print(f"解码错误: {e}")
            except Exception as e:
                print(f"读取文件时发生错误: {e}")
        else:
            print(f"文件 {index_file_path} 不存在。")
        return index_info

    def get_document_info(self):
        document_file_path = os.path.join(self.prefix_dir, self.document_file)
        if os.path.isfile(document_file_path):
            try:
                with open(document_file_path, "r", encoding="utf-8") as f:
                    document_info = f.read()
            except UnicodeDecodeError as e:
                print(f"解码错误: {e}")
            except Exception as e:
                print(f"读取文件时发生错误: {e}")
        else:
            print(f"文件 {document_file_path} 不存在。")
        return document_info

    def get_example_info(self):
        example_file_path = os.path.join(self.prefix_dir, self.example_file)
        if os.path.isfile(example_file_path):
            try:
                with open(example_file_path, "r", encoding="utf-8") as f:
                    example_info = f.read()
            except UnicodeDecodeError as e:
                print(f"解码错误: {e}")
            except Exception as e:
                print(f"读取文件时发生错误: {e}")
        else:
            print(f"文件 {example_file_path} 不存在。")
        return example_info

    def get_ddl_info(self):
        ddl_file_path = os.path.join(self.prefix_dir, self.SQL_DDL_file)
        if os.path.isfile(ddl_file_path):
            try:
                with open(ddl_file_path, "r", encoding="utf-8") as f:
                    ddl_info = f.read()
            except UnicodeDecodeError as e:
                print(f"解码错误: {e}")
            except Exception as e:
                print(f"读取文件时发生错误: {e}")
        else:
            print(f"文件 {ddl_file_path} 不存在。")
        return ddl_info

    def get_relation_info(self):
        relation_file_path = os.path.join(self.prefix_dir, self.relation_file)
        if os.path.isfile(relation_file_path):
            try:
                with open(relation_file_path, "r", encoding="utf-8") as f:
                    relation_info = f.read()
            except UnicodeDecodeError as e:
                print(f"解码错误: {e}")
            except Exception as e:
                print(f"读取文件时发生错误: {e}")
        else:
            print(f"文件 {relation_file_path} 不存在。")
        return relation_info

    def get_semantic_prompt(self, question, initial_semantic_prompt: str = None, reget_info: str = ''):
        if initial_semantic_prompt is None:
            initial_semantic_prompt = f'''
            # 角色:意图识别和语义分析专家
                你的回答应该必须基于给定的上下文，并遵循回答指南和格式说明，否则将对你惩罚。
            ## 工作内容：
                1. 你必须从（科室概览，重点病种，单一病种，医师）中准确识别出用户想问的是哪一大类
                2. 根据用户的完整问题，进行语义分析，从中提取出时间，科室，指标，补充四个元素。
            # 关键说明
                1. 时间的格式为yyyy-mm-dd
                2. 如果没提供时间，则默认为2023-01-01至2023-11-30
                3. 如果没提供科室，默认为骨科
                4. 如果没提供指标或用户表述的很模糊，默认为全部指标，根据意图不同，全部指标如下：
                    "科室概览"：出院人数，手术例数，出院患者手术台次数，出院患者手术占比，出院患者四级手术台次数，出院患者四级手术比例，出院患者微创手术台次数，出院患者微创手术占比
                    "单一病种"：主刀医师，例数，均次费，均次药费，药占比，均次卫生材料费，耗占比，去药去耗材占比，平均住院日
                    "重点病种"：病种，主刀医师，例数，均次费，均次药费，药占比，均次卫生材料费，耗占比，去药去耗材占比，平均住院日
                    "医师": 姓名，工号，出院人数，住院均次费用，均次卫生材料费, 均次药费,药占比（住院），耗占比（住院）
            # 流程和格式说明
                1. 如果成功分解，返回格式为{{"Done": "True", "question":"" ,"result": {{"意图":"","时间": "", "科室": "", "指标": "", "其他信息":""}}}}
                    你必将result的结果返回为字符串的形式
                    其中的question，在用户问题的基础上把信息补全；指标根据意图，必须为具体指标
                2. 如果不能够成功分解，则提示用户补充相关信息，将你的提示存入result中，等待用户输入,
                返回格式为{{"Done": "False", "question":"" ,"result": ""}}
                3. 如果问题中的信息有重复，必须以最后出现的信息内容为主。
            # 注意：
                 输出格式必须为str格式，必须可以转化为json格式，不要有非法换行符等内容，否则将对你严重惩罚。
                "{{"意图":"","时间": "", "科室": "", "指标": "", "其他信息":""}}"必须返回为字符串的形式，否则将对你严重惩罚。
            '''
            semantic_prompt = [self.system_message(initial_semantic_prompt), self.user_message(question + reget_info)]
            return semantic_prompt

    def get_confirm_prompt(self, semantic_result, confirm_initial_prompt: str = None):
        if confirm_initial_prompt is None:
            confirm_initial_prompt = f'''
        # 角色：
            你的回答必须基于给定的上下文，并遵循回答指南和格式说明，否则将对你惩罚。
        ## 工作内容：
            你将语义分析专家分析的结果转换为自然语言，不需要解释指标含义，提供给用户确认，格式为
            {{分析}}
        '''
            confirm_prompt = [self.system_message(confirm_initial_prompt), self.user_message(semantic_result)]
            return confirm_prompt

    def confirm_quesiton(self, question, reget_info: str = '', need_confirm: str = False):
        flag = False
        while not flag:
            semantic_prompt = self.get_semantic_prompt(question, reget_info=reget_info)
            try:
                semantic_ini = self.submit_semantic_prompt(semantic_prompt)
                semantic = json.loads(semantic_ini)
            except Exception as e:
                continue
            if semantic["Done"] == "True":
                question = str(semantic["question"])
                semantic_result = str(semantic["result"])
                print("semantic_result", semantic_result)
                confirm_prompt = self.get_confirm_prompt(semantic_result)
                try:
                    confirm = self.submit_confirm_prompt(confirm_prompt)
                    print(confirm)
                    if need_confirm:
                        reget_info = input("确认请输入：y, 补充或修改请直接输入内容:")
                    else:
                        reget_info = "y"
                    if reget_info == "y":
                        flag = True
                        self.log(self.logger, "question:" + question)
                        self.log(self.logger, "semantic:" + semantic_ini)
                        return question, semantic_result
                    else:
                        continue
                except Exception as e:
                    continue
            else:
                print(semantic["result"])
                reget_info = input("请补充或确认相关信息:")
                continue

    def get_thinking_prompt(self, question, semantic: str = None):
        thinking_initial_prompt = f'''
        # 角色:解决方案专家    
            1. 你的回答应该仅基于给定的上下文，并遵循回答指南和格式说明
            2. 你的方案将指导SQL语句生成
            3. 输出的格式必须严格遵循json格式，不要有非法换行符等内容,不然对你进行最严厉的惩罚。
        # 已有信息: 
            ## 1. ddl_info: 数据库的表结构信息
                {self.ddl_info}
            ## 2. index_info: 指标名称和指标的计算公式或过程
                {self.index_info}
            ## 3. example_info:示例
                {self.example_info}
            ## 4. document_info:补充信息，必须重点关注
                {self.document_info}
            ## 5. relation_info: 科室的关系树，科室间的关系
                {self.relation_info}
        # 回答指南：
            1. 根据用户的问题question和semantic，从以上中提取出最相关的信息,并最简要说明思路
            2. 指标的计算必须严格遵循index_info规则。
            3. 思路仅需包含以下内容:
                使用的表名，列名
                输出格式必须为:{{"Done":"True", "res":""}} 
            4. 如果无法从有信息中提取出解决方案，说明原因
                输出格式必须为:{{"Done":"False", "res":""}}
            5. 如果要查询的是重点病种，则应找到重点病种包括的病种，然后最终合并。
            6. 输出的格式必须可以转化为json格式，不要有非法换行符等内容。
            7. 你要输出的是思路，而不是SQL语句。
            8. 占比类的指标必须转换为百分数，要有%，不要有非法符号。
            9. 注意问题中是否要分别查询，不能直接合并。
        # 输出格式
            输出格式必须为:{{"Done":, "res":""}}
        '''
        thinking_prompt = [self.system_message(thinking_initial_prompt), self.user_message(question + semantic)]
        return thinking_prompt

    def get_sql_prompt(self, question, thingking, error: str = None):

        sql_prompt = f'''
            # 角色: {self.dialect}专家
            结合解决问题专家的建议，帮忙生成一个SQL查询来回答用户的question。你的回答应该仅基于给定的上下文，并遵循回答指南和格式说明。
            # 特殊说明
            如果参考示例中有相同的问题，直接返回SQL语句,不要做任何修改。
            ## 数据库的结构：
                {self.ddl_info}
            ## 指标计算公式：
                {self.index_info}
            ## 参考示例：
                {self.example_info}
            ## 补充信息:
                {self.document_info}
            ## 关系树:
                {self.relation_info}
            ## 解决问题专家的建议
                {thingking}
            ## 用户问题：
                {question}
            ##  运行SQL错误信息
                {error}
            # 回答:
                1.必须包含 question中的时间, 科室，指标三个元素
                2.根据以上信息，直接生成回答question的SQL语句, 不要有任何额外信息，必须确保输出的 SQL 符合 {self.dialect} 的规范且可执行，并且没有语法错误。    
                3. 尽量使用简单的SQL语句，需要考虑是否正确使用SUM函数
                4. 如果有错误信息，根据错误信息，重新生成SQL语句
                5. 不要有\n \b等任何非法符号。
                6. 如果要查询的是重点病种，应该查询所有重点病种包括的病种，然后按照病种和主刀医生排序。
                7. 占比类的指标必须转换为百分数，要有%，不要有非法符号。
                
        '''
        thinking_prompt = [self.system_message(sql_prompt), self.user_message(question)]
        return thinking_prompt

    def get_reflection_prompt(self, question: str, thinking: str, SQL: str):

        reflection_prompt = f'''
            # 角色: {self.dialect}顶级专家
            1. 结合解决问题专家的建议和 {self.dialect}专家的回答和用户的question, 检查{self.dialect}专家的SQL回答是否能够解决用户的问题
            2. 你的回答应该仅基于给定的上下文，并遵循回答指南和格式说明。
            ## 数据库的结构：
                {self.ddl_info}
            ## 指标计算公式：
                {self.index_info}
            ## 参考示例：
                {self.example_info}
            ## 补充信息:
                {self.document_info}
            ## 关系树:
                {self.relation_info}
            ## 解决问题专家的建议:
                {thinking}
            ## 用户问题：
                {question}
            ## {self.dialect}专家的回答
                {SQL}
            # 回答
                根据以上信息:
                1. 如果SQL语句没有错误或要修改的内容, 直接返回SQL语句, 不要有任何额外信息，不要有任何非法符号
                2. 如果SQL语句有错误或要修改的内容, 直接返回修改后的SQL语句, 不要有任何额外信息
                3. 必须确保输出的 SQL 符合 {self.dialect} 的规范且可执行，并且没有语法错误。
                4. 必须保证SQL语句中包含了question中的 时间, 指标，科室三个元素
        '''
        thinking_prompt = [self.system_message(reflection_prompt), self.user_message(question)]
        return thinking_prompt

    def get_final_prompt(self, question, result):
        final_prompt = f'''
            # 角色: 数据分析师
             你的回答应该仅基于给定的上下文，并遵循回答指南和格式说明。
            ## 主要工作:
            1. 根据用户的question和最终查询结果，给用户一个简短的回答。
            ## 回答:
            1. 选择合适的数量单位回答,超过十万，用万为单位回答。超过亿，用亿为单位回答。
            2. 涉及到比例的，转换为百分比回答，保留两位小数
            ## 用户问题:
                {question}
            '''
        final_prompt = [self.system_message(final_prompt), self.user_message(result)]
        return final_prompt

    def ask(self, question, save_csv: bool = False):
        while self.times <= self.MAX_TIMES:
            question, semantic_result = self.confirm_quesiton(question)
            thinking = self.get_thinking_prompt(question, semantic_result)
            thinking_result = self.submit_thinking_prompt(thinking)
            self.log(self.logger, "thinking:" + thinking_result)
            try:
                thinking_result = json.loads(thinking_result)
            except Exception as e:
                print(e)
                self.times += 1
                continue
            if thinking_result["Done"] == "False":
                print("thinking_result:", thinking_result["res"])
                self.times += 1
            else:
                thinking_result = thinking_result["res"]
                print("thinking_result:", thinking_result)
            sql_attempt = 1
            error = ''
            while sql_attempt <= self.MAX_SQL_ATTEMPT:
                sql_prompt = self.get_sql_prompt(question, thinking_result, error)
                sql = self.submit_prompt(sql_prompt)
                print("initial_sql:", sql)

                y_or_n, run_sql_result, = self.run_sql(sql)
                if not y_or_n:
                    error = run_sql_result
                    self.log(self.logger, "SQL:" + sql)
                    self.log(self.logger, "SQL error:" + str(error))
                    print(f"第{sql_attempt} 次运行SQL失败， 进行下一次尝试")
                    sql_attempt += 1
                    continue
                break
            if not isinstance(run_sql_result, pd.DataFrame):
                if not run_sql_result:
                    self.times += 1
                    continue
                self.times += 1
                continue

            self.log(self.logger, "sql:" + sql)
            print("result:", run_sql_result)
            if save_csv:
                from datetime import datetime
                time = datetime.now().strftime("%Y%m%d%H%M")
                run_sql_result.to_excel(f"result_{time}.xlsx", index=False)

            sql_result = run_sql_result.to_dict()
            converted_dict = {key: {k: float(v) if isinstance(v, Decimal) else v for k, v in value.items()} for
                              key, value in sql_result.items()}
            sql_result = json.dumps(converted_dict, ensure_ascii=False)
            self.log(self.logger, "sql_result:" + sql_result)
            # final_prompt = self.get_final_prompt(question, sql_result)
            # result = self.submit_final_prompt(final_prompt)
            # self.log(self.logger, "查询结果:" + result)
            # print("查询结果:", result)
            self.times = 1
            self.auto_add_examples(question, sql, auto=self.AUTO_ADD_EXAMPLES)
            # return result
            return sql_result

    def auto_add_examples(self, question, sql, auto=False, front=True):
        if auto:
            self.add_example(question, sql)
            return "Auto Added"
        if front:
            add_or_no = "y"
        else:
            add_or_no = input("是否添加到样例中？, 添加请输入 y，不添加请输入 n\n请输入您的选择：")
            print("您的选择是:", add_or_no)
        if add_or_no == "y":
            self.add_example(question, sql)
        elif add_or_no == "n":
            pass
        else:
            print("无效的输入，请输入 'y' 或 'n'。")

    def add_example(self, question, sql, example_json=None):
        if not example_json:
            example_json = os.path.join(self.prefix_dir, self.example_json)
        new_example = {
            "question": question,
            "SQL": sql
        }
        if not os.path.exists(example_json):
            with open(example_json, 'w', encoding='utf-8') as file:
                file.write("{}")  # 创建一个空的JSON对象
        # 读取现有的 JSON 文件
        with open(example_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # 将新例子追加到 examples 数组
        if 'examples' not in data:
            data['examples'] = []
        data['examples'].append(new_example)
        # 将更新后的数据写回 JSON 文件
        with open(example_json, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @abstractmethod
    def submit_final_prompt(self, final_prompt: List):
        pass

    @abstractmethod
    def submit_confirm_prompt(self, final_prompt: List):
        pass

    @abstractmethod
    def submit_semantic_prompt(self, semantic_prompt: List):
        pass

    @abstractmethod
    def submit_thinking_prompt(self, thinking: List):
        pass

    @abstractmethod
    def submit_prompt(self, prompt: List):
        pass

    @abstractmethod
    def submit_reflection_prompt(self, question: List, ):
        pass

    @abstractmethod
    def system_message(self, message: str) -> any:
        pass

    @abstractmethod
    def user_message(self, message: str) -> any:
        pass

    @abstractmethod
    def assistant_message(self, message: str) -> any:
        pass
