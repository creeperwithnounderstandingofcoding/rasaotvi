# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import logging
from typing import Any, Text, Dict, List
from pathlib import Path

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.exceptions import ActionException
from actions.vi_info_form import ViInfoForm



# 设置日志记录
logger = logging.getLogger(__name__)

class FileNotExistException(Exception):
    pass

class InvalidFilePathException(Exception):
    pass

class ActionProvideInformation(Action):

    def name(self) -> Text:
        return "action_provide_firm_vi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 直接从 tracker 获取插槽值
        company = tracker.get_slot("company")
        year = tracker.get_slot("year")
        department = tracker.get_slot("department")
        position = tracker.get_slot("position")

        try:
            # 构建文件路径
            file_path = self.get_file_path(company, year, department, position)
            # 获取文件内容
            response = self.get_response(file_path)
            # 发送文件内容给用户
            dispatcher.utter_message(text=response)
        except FileNotExistException as e:
            logger.error(f"File not found: {str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"抱歉，找不到所需的文件: {str(e)}")
        except InvalidFilePathException as e:
            logger.error(f"Invalid file path: {str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"抱歉，文件路径无效: {str(e)}")
        except Exception as e:
            logger.error(f"Error while processing the request: {str(e)}", exc_info=True)
            dispatcher.utter_message(text=f"抱歉，处理您的请求时出现了错误: {str(e)}")

        return []  # 不再设置插槽，直接返回空列表
    

    def standardize_company_name(self, company: Text) -> Text:
    # 检查 'company' 是否是有效的字符串
        if not company or not isinstance(company, str):
            logger.warning(f"Invalid company name: {company}")
            return None  # 如果不是，则返回 None
        
        # 创建一个映射表将各种公司名称映射到标准名称
        company_mapping = {
            "高盛": "高盛",
            "gs": "高盛",
            "GS": "高盛",
            "goldman": "高盛",
            "goldman sachs": "高盛",
            "bofa": "美国银行",
            # ... 为其他公司添加更多映射
        }
        return company_mapping.get(company.lower(), company)  # 如果找不到匹配项，则返回原始公司名称

    
    def standardize_year(self, year: Text) -> Text:
        year_mapping = {
            "2023": "2023",
            "23": "2023",
            "二零二三": "2023",
            "2022": "2022",
            "22": "2022",
            "二零二二": "2022",
            "2021": "2021",
            "21": "2021",
            "二零二一": "2021",
        }
        return year_mapping.get(year, year)

    def standardize_department(self, department: Text) -> Text:
        department_mapping = {
            "IBD": "IBD",
            "Investment Banking Division": "IBD",
            "investment banking": "IBD",
            "Sales and Trading": "Sales and Trading",
            "S&T": "Sales and Trading",
            "Research": "Research",
            "ibd": "IBD",
            "ib":"IBD",
            "投行": "IBD",
            "投行部": "IBD",
            # ... add more mappings as needed
        }
        return department_mapping.get(department, department)

    def standardize_position(self, position: Text) -> Text:
        position_mapping = {
            "Summer Analyst": "Summer Analyst",
            "SA": "Summer Analyst",
            "Full-time Analyst": "Full-time Analyst",
            "FTA": "Full-time Analyst",
            "sa": "Summer Analyst",
            "暑期":"Summer Analyst",
            # ... add more mappings as needed
        }
        return position_mapping.get(position, position)

    def get_file_path(self, company: Text, year: Text, department: Text, position: Text) -> Text:
        try:
            # 使用相对路径构建文件路径
            # 假设responses文件夹位于项目的根目录下
            return Path("responses") / company / year / department / f"{position}/vi.txt"
        except Exception as e:
            logger.error(f"Error while constructing file path: {str(e)}", exc_info=True)
            raise InvalidFilePathException(str(e))


    def get_response(self, file_path: Text) -> Text:
        if not file_path or not isinstance(file_path, str):
            error_message = f"Invalid file path: {file_path}"
            logger.error(error_message)
            raise InvalidFilePathException(error_message)

        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            error_message = f"File does not exist: {file_path}"
            logger.error(error_message)
            raise FileNotExistException(error_message)  

        try:
            return file_path_obj.read_text(encoding="utf-8")
        except Exception as e:
            error_message = f"Error reading file {file_path}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise ActionException(error_message)

