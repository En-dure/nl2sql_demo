import requests
from base import Base
from openai import OpenAI

class Vllm(Base):
    def __init__(self, config=None):
        super().__init__(config)
        if config is None or "vllm_host" not in config:
            self.host = "http://localhost:8000"
        else:
            self.host = config["vllm_host"]

        if config is None or "model" not in config:
            raise ValueError("check the config for vllm")
        else:
            self.model = config["model"]

        if "auth-key" in config:
            self.auth_key = config["auth-key"]
        else:
            self.auth_key = None

        self.client = OpenAI(
            api_key=config["auth-key"],
            base_url=config["vllm_host"] + "/v1"
        )



    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt, **kwargs) -> str:
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

    def submit_semantic_prompt(self, prompt, **kwargs) -> str:
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

    def submit_thinking_prompt(self, prompt, **kwargs) -> str:
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

    def submit_reflection_prompt(self, prompt, **kwargs) -> str:
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

    def submit_final_prompt(self, prompt):
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

    def submit_confirm_prompt(self, prompt):
        url = f"{self.host}/v1/chat/completions"
        data = {
            "model": self.model,
            "stream": False,
            "messages": prompt,
        }
        if self.auth_key is not None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_key}'
            }
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.post(url, json=data)
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']

if __name__ == "__main__":
    from config import vllm_config, mysql_config
    p = [{'role': 'system', 'content': '\n # 角色：\n 你的回答必须基于给定的上下文，并遵循回答指南和格式说明，否则将对你惩罚。\n ## 工作内容：\n 你将语义分析专家分析的结果转换为自然语言，不需要解释指标含义，提供给用户确认，格式为\n {分析}\n '}, {'role': 'user', 'content': {'意图': '科室概览', '时间': '2023-01-01至2023-11-30', '科室': '骨科', '指标': '出院人数，手术例数，出院患者手术台次数，出院患者手术占比，出院患者四级手术台次数，出院患者四级手术比例，出院患者微创手术台次数，出院患者微创手术占比', '其他信息': ''}}]
    print(type(p))
    a = Vllm(vllm_config)
    b = a.submit_confirm_prompt(str(p))
    print(b)