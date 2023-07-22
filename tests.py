import base64
import unittest

import requests

from tim import Message, MsgType, send_msg


class MyTestCase(unittest.TestCase):
    qq_group_name = "神经"
    
    def test_send_text(self):
        test_msg = Message(qq_group_name=self.qq_group_name, data=[{"type": MsgType.TEXT, "data": "hello"}])
        send_msg(test_msg)
    
    def test_http_send_image(self):
        image_base64 = base64.b64encode(
            open("C:\\Users\\linyu\\AppData\\Local\\Temp\\tmpylk7ebta.png", "rb").read()).decode("utf-8")
        requests.post("http://localhost:8088", json={
            "qq_group_name": self.qq_group_name,
            "data": [{
                "type": "Image",
                "data": image_base64
            }]
        })
    
    def test_send_image(self):
        image_base64 = base64.b64encode(
            open("C:\\Users\\linyu\\AppData\\Local\\Temp\\tmpylk7ebta.png", "rb").read()).decode("utf-8")
        test_msg = Message(qq_group_name=self.qq_group_name,
                           data=[
                               {"type": MsgType.TEXT, "data": "hellokitty"},
                               {"type": MsgType.IMAGE, "data": image_base64},
                               {"type": MsgType.TEXT, "data": "hellokitty"},
                           ])
        send_msg(test_msg)
    
    def test_send_long_text(self):
        test_msg = Message(qq_group_name=self.qq_group_name,
                           data=[
                               {"type": MsgType.TEXT, "data": "hellokitty2" * 1003},
                           ])
        send_msg(test_msg)

# if __name__ == '__main__':
#     unittest.main()
