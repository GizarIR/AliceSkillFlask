from flask import Flask, request
import logging
import json

from state import STATE_REQUEST_KEY, STATE_RESPONSE_KEY
from scenes import SCENES, DEFAULT_SCENE
from request_helpers import Request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["POST"])
def handler():
    print('Входящий запрос: ' + json.dumps(event))
    request = Request(event)
    current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')
    print('Текущая сцена: ' + str(current_scene_id))
    if current_scene_id is None:
        return DEFAULT_SCENE().reply(request)
    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(request)
    if next_scene is not None:
        print(f'Переход из сцены {current_scene.id()} в {next_scene.id()}')
        return next_scene.reply(request)
    else:
        print(f'Ошибка в разборе пользовательского запроса в сцене {current_scene.id()}')
        return current_scene.fallback(request)

# Function need fot test communications with platform Yandex
# @app.route("/", methods=["POST"])
# def handler_test():
#     logging.info("Входящий запрос:" + request.json)
#
#     response = {
#         "version": request.json["version"],
#         "session": request.json["session"],
#         "response": {
#             "end_session": False
#         }
#     }
#
#     req = request.json
#     if req["session"]["new"]:
#         response["response"]["text"] = "Привет! Как твои дела? Как отметил новый год?"
#     else:
#         if req["request"]["original_utterance"].lower() in ["хорошо","отлично"]:
#             response["response"]["text"] = "Супер! Я за вас рада!"
#         elif req["request"]["original_utterance"].lower() in ["плохо", "скучно"]:
#             response["response"]["text"] = "Жаль, думаю со мной было бы лучше!"
#
#     return json.dumps(response)
#
#
# @app.route('/')
# def index():
#     return 'Hello World!!!'

if __name__ == "__main__":
    app.run()
