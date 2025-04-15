import json
import logging
import sys
import time
import traceback
from enum import Enum
from io import StringIO
from collections.abc import Mapping
from enum import StrEnum
from threading import Lock
from typing import Any, Optional
from httpx import Timeout, post
from pydantic import BaseModel
from yarl import URL

from configs import dify_config
from core.helper.code_executor.javascript.javascript_transformer import NodeJsTemplateTransformer
from core.helper.code_executor.jinja2.jinja2_transformer import Jinja2TemplateTransformer
from core.helper.code_executor.python3.python3_transformer import Python3TemplateTransformer
from core.helper.code_executor.template_transformer import TemplateTransformer

logger = logging.getLogger(__name__)


class CodeExecutionError(Exception):
    pass


class CodeExecutionResponse(BaseModel):
    class Data(BaseModel):
        stdout: Optional[str] = None
        error: Optional[str] = None

    code: int
    message: str
    data: Data


class CodeLanguage(StrEnum):
    PYTHON3 = "python3"
    JINJA2 = "jinja2"
    JAVASCRIPT = "javascript"


class CodeExecutor:
    dependencies_cache: dict[str, str] = {}
    dependencies_cache_lock = Lock()

    code_template_transformers: dict[CodeLanguage, type[TemplateTransformer]] = {
        CodeLanguage.PYTHON3: Python3TemplateTransformer,
        CodeLanguage.JINJA2: Jinja2TemplateTransformer,
        CodeLanguage.JAVASCRIPT: NodeJsTemplateTransformer,
    }

    code_language_to_running_language = {
        CodeLanguage.JAVASCRIPT: "nodejs",
        CodeLanguage.JINJA2: CodeLanguage.PYTHON3,
        CodeLanguage.PYTHON3: CodeLanguage.PYTHON3,
    }

    supported_dependencies_languages: set[CodeLanguage] = {CodeLanguage.PYTHON3}

    @classmethod
    def execute_code(cls, language: CodeLanguage, preload: str, code: str) -> str:
        """
        Execute code
        :param language: code language
        :param preload: the preload script
        :param code: code
        :return:
        """

        def exec_code(code):
            exec_result = {}
            with Capturing() as output:
                exec(code, locals(), locals())
                exec_result = locals().get('main_result')

            observation = ""
            for line in output:
                observation += line
                observation += "\n"

            if exec_result is None:
                exec_result = {}
            exec_result['output'] = observation
            return exec_result

        exec_result = {}
        try:
            exec_result = exec_code(code)
        except Exception as e:
            exec_result['error'] = traceback.format_exc()
            
        json_string = json.dumps(exec_result, indent=4)

        result = f'''<<RESULT>>{json_string}<<RESULT>>'''
        return result
        

    @classmethod
    def execute_workflow_code_template(cls, language: CodeLanguage, code: str, inputs: Mapping[str, Any]):
        """
        Execute code
        :param language: code language
        :param code: code
        :param inputs: inputs
        :return:
        """
        template_transformer = cls.code_template_transformers.get(language)
        if not template_transformer:
            raise CodeExecutionError(f"Unsupported language {language}")

        runner, preload = template_transformer.transform_caller(code, inputs)

        try:
            response = cls.execute_code(language, preload, runner)
        except CodeExecutionError as e:
            raise e

        return template_transformer.transform_response(response)

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
