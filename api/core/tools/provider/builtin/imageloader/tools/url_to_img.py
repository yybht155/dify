import base64
import hashlib
import json
import uuid
from io import BytesIO
from mimetypes import guess_type
from os import path
from typing import Any

import requests
from PIL import Image

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.errors import ToolInvokeError
from core.tools.tool.builtin_tool import BuiltinTool
from core.tools.tool_file_manager import ToolFileManager
from extensions.ext_storage import storage
from core.file import FileTransferMethod


class ImageLoaderConvertUrlTool(BuiltinTool):
    """
    
    """

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        url = tool_parameters.get('url')
        # image_bytes = self.download_image(url)
        # image_b64_json = self.image_to_b64_json(image_bytes)
        # decoded_bytes = self.b64_json_to_bytes(image_b64_json)

        result = []

        tenant_id = self.generate_fixed_uuid4("image_files_local_storage")

        image_ext = ""
        filename = url.split('/')[-1]
        if '.' in filename:
            filename, image_ext = path.splitext(filename)

        filename = self.generate_fixed_uuid4(url)

        file_key = f"tools/{tenant_id}/{filename}{image_ext}"
        mime_type, _ = guess_type(file_key)
        size = 0
        if not storage.exists(file_key):
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                storage.save(file_key, response.content)
                size = len(response.content)
            else:
                raise ToolInvokeError(f"Request failed with status code {response.status_code} and {response.text}")

            # sign_url = ToolFileManager.sign_file(file.file_key, image_ext)

        else:
            blob = storage.load_once(file_key)
            size = len(blob)

        _ = ToolFileManager.create_file_by_key(
            id=filename,
            user_id=user_id, 
            tenant_id=tenant_id,
            conversation_id=None,
            file_key=file_key,
            mimetype=mime_type,
            name=filename,
            size=size
        )

        sign_url = ToolFileManager.sign_file(tool_file_id=filename, extension=image_ext)

        url = sign_url

        meta = { 
            "url": url,
            "tool_file_id": filename,
            "transfer_method": FileTransferMethod.REMOTE_URL
        }

        msg = ToolInvokeMessage(type=ToolInvokeMessage.MessageType.IMAGE_LINK,
                                message=url,
                                save_as=filename,
                                meta=meta)
        
        result.append(msg)


        # result = []
        # result.append(self.create_blob_message(blob=decoded_bytes,
        #                                            meta={'mime_type': 'image/png'},
        #                                            save_as=self.VARIABLE_KEY.IMAGE.value))


        

        # ToolFileManager.create_file_by_url(current_user.id, current_user.current_tenant_id, file_url=message.message)
        # extension = guess_extension(file.mimetype) or '.png'
        # sign_url = ToolFileManager.sign_file(file.file_key, extension)

        # meta = { "url": sign_url }
        # msg = ToolInvokeMessage(type=ToolInvokeMessage.MessageType.IMAGE_LINK,
        #                         message=sign_url,
        #                         save_as='',
        #                         meta=meta)
        
        # result = []
        # result.append(msg)
        return result

    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        return response.content

    def image_to_b64_json(self, image_bytes):
        image = Image.open(BytesIO(image_bytes))
        buffered = BytesIO()
        
        # 这里假设要转换为PNG格式
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # 转换为JSON格式
        img_b64_json = json.dumps({"b64_json": img_b64})
        return img_b64_json

    def b64_json_to_bytes(self, b64_json):
        img_b64 = json.loads(b64_json)["b64_json"]
        return base64.b64decode(img_b64)

    def generate_fixed_uuid4(self, input_string):
        # 使用SHA-1哈希函数生成一个哈希值
        hash_object = hashlib.sha1(input_string.encode())
        hash_hex = hash_object.hexdigest()
        
        # 取前16个字节生成UUID
        uuid_hex = hash_hex[:32]
        return str(uuid.UUID(uuid_hex))
