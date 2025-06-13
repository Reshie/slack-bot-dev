# リクエストスキーマの定義
request_schema = {
    "type": "object",
    "properties": {
        "channel": {
            "type": "string",
            "minLength": 1
        },
        "text": {
            "type": "string",
            "minLength": 1
        },
        "mentions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "buttons": {
            "type": "object",
            "properties": {
                "yes": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "text": {"type": "string"}
                    },
                    "required": ["url", "text"]
                },
                "no": {
                    "type": "object", 
                    "properties": {
                        "url": {"type": "string"},
                        "text": {"type": "string"}
                    },
                    "required": ["url", "text"]
                }
            },
            "required": ["yes", "no"]
        }
    },
    "required": ["channel", "text", "mentions", "buttons"]
} 