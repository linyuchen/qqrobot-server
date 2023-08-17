# 使用键盘模拟的方式控制Tim发送QQ群消息

## API

url: `/:8088`

method: `POST`

content-type: `application/json`

body:
```json
{
    "qq_group_name": "QQ群的名字",
    "data":[
        {
            "type": "Plain", // 文本类型的消息
            "data": "hello" 
        },
        {
            "type": "Image", // 图片类型的消息
            "data": "图片的base64编码"
        },
       {
            "type": "ImageUrl", // 图片类型的消息
            "data": "图片的url"
        },
        {
            "type": "At", // @群成员
            "data": "群成员的QQ号"
        }
    ]
}
```