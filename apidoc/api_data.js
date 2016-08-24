define({ "api": [  {    "type": "POST",    "url": "https://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod",    "title": "register_device",    "name": "register_device",    "group": "Device",    "description": "<p>register new device</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "user_id",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "device_token",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "app",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "Object",            "optional": false,            "field": "user_data",            "description": "<p>Optional</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"device_token\": \"a6181119 3c02a69f c689f523 1a86da85 39e7b77c d0504d2a 20fd0c48 8ab8fae8\",\n        \"app\": \"appname-ios-dev\",\n        \"user_id\": \"1\",\n        \"user_data\": {\"gender\": \"Male\"}\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/register_device/lambda.py",    "groupTitle": "Device",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod"      }    ]  },  {    "type": "DELETE",    "url": "https://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod",    "title": "unregister_device",    "name": "unregister_device",    "group": "Device",    "description": "<p>unregister  device</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "device_token",            "description": "<p>Mandatory</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"device_token\": \"a6181119 3c02a69f c689f523 1a86da85 39e7b77c d0504d2a 20fd0c48 8ab8fae8\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/unregister_device/lambda.py",    "groupTitle": "Device",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://4r3r9b19u9.execute-api.us-east-1.amazonaws.com/prod"      }    ]  },  {    "type": "POST",    "url": "https://92yq44217c.execute-api.us-east-1.amazonaws.com/prod/",    "title": "send_notification",    "name": "send_notification",    "group": "Notification",    "description": "<p>send or schedule notification to user or topic</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "user_id",            "description": "<p>Optional</p>"          },          {            "group": "Parameter",            "type": "[String]",            "optional": false,            "field": "topics_names",            "description": "<p>Optional</p>"          },          {            "group": "Parameter",            "type": "Object",            "optional": false,            "field": "query",            "description": "<p>Optional (based on user_data)</p>"          },          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "message",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "Boolean",            "optional": false,            "field": "is_json",            "description": "<p>Optional (default : false)</p>"          },          {            "group": "Parameter",            "type": "Datetime",            "optional": false,            "field": "fire_at",            "description": "<p>Optional ('%Y-%m-%d %H:%M:%S') if not provide notification send instantly</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"message\":\"Notification\",\n        \"user_id\": \"1\",\n        \"is_json\": false,\n        \"query\": {\"gender\": \"Male\"},\n        \"topics_names\": [\"News\"],\n        \"fire_at\": \"2016-08-24 21:42:40\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n          \"n_topic\": 0,\n          \"n_failed\": 0,\n          \"n_devices\": 1\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/send_notification/lambda.py",    "groupTitle": "Notification",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://92yq44217c.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "type": "POST",    "url": "https://v141i5fp0j.execute-api.us-east-1.amazonaws.com/prod/",    "title": "subscribe_topic",    "name": "subscribe_topic",    "group": "Subscription",    "description": "<p>subscribe to topic</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "topic_name",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "user_id",            "description": "<p>Mandatory</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"topic_name\": \"topic_name\",\n        \"user_id\": \"1\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n              subscription_arn {String}\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/subscribe_topic/lambda.py",    "groupTitle": "Subscription",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://v141i5fp0j.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "type": "DELETE",    "url": "https://v141i5fp0j.execute-api.us-east-1.amazonaws.com/prod/",    "title": "unsubscribe_topic",    "name": "unsubscribe_topic",    "group": "Subscription",    "description": "<p>unsubscribe topic</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "topic_name",            "description": "<p>Mandatory</p>"          },          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "user_id",            "description": "<p>Mandatory</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"topic_name\": \"topic_name\",\n        \"user_id\": \"1\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n              subscription_arn {String}\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/unsubscribe_topic/lambda.py",    "groupTitle": "Subscription",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://v141i5fp0j.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "type": "POST",    "url": "https://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/",    "title": "create_topic",    "name": "create_topic",    "group": "Topic",    "description": "<p>create new topic</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "topic_name",            "description": "<p>Mandatory</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"topic_name\": \"topic_name\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n              topic_arn {String}\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/create_topic/lambda.py",    "groupTitle": "Topic",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "type": "DELETE",    "url": "https://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/",    "title": "delete_topic",    "name": "delete_topic",    "group": "Topic",    "description": "<p>delete topic</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "String",            "optional": false,            "field": "topic_name",            "description": "<p>Mandatory</p>"          }        ]      },      "examples": [        {          "title": "Example:",          "content": "{\n    \"payload\":\n    {\n        \"topic_name\": \"topic_name\"\n    }\n}",          "type": "json"        }      ]    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data={\n              topic_arn {String}\n      },\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/delete_topic/lambda.py",    "groupTitle": "Topic",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "type": "GET",    "url": "https://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/",    "title": "get_topics",    "name": "get_topics",    "group": "Topic",    "description": "<p>get topics</p>",    "version": "0.1.0",    "header": {      "fields": {        "Header": [          {            "group": "Header",            "type": "String",            "optional": false,            "field": "x-api-key",            "description": "<p>api-key.</p>"          }        ]      }    },    "success": {      "examples": [        {          "title": "Success-Response:",          "content": "HTTP/1.1 200 OK\n{\n      code='200', message='success',\n      data=[\n            {\n              \"name\": \"News\",\n              \"arn\": \"arn:aws:sns:us-east-1:481790367918:News\"\n            },\n            {\n              \"name\": \"Test\",\n              \"arn\": \"arn:aws:sns:us-east-1:481790367918:Test\"\n            }\n          ],\n      metadata={}\n}",          "type": "json"        }      ]    },    "filename": "userbased-sns-lambda/get_topics/lambda.py",    "groupTitle": "Topic",    "sampleRequest": [      {        "url": "https://www.getpostman.com/collections/cc6d863cc792b3c7d67bhttps://bk3om565e4.execute-api.us-east-1.amazonaws.com/prod/"      }    ]  },  {    "success": {      "fields": {        "Success 200": [          {            "group": "Success 200",            "optional": false,            "field": "varname1",            "description": "<p>No type.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "varname2",            "description": "<p>With type.</p>"          }        ]      }    },    "type": "",    "url": "",    "version": "0.0.0",    "filename": "userbased-sns-lambda/apidoc/main.js",    "group": "_Users_Mindvalley_MV_dev_userbased_sns_lambda_apidoc_main_js",    "groupTitle": "_Users_Mindvalley_MV_dev_userbased_sns_lambda_apidoc_main_js",    "name": ""  }] });
