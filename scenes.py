import enum
import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional
import json

import intents
from request_helpers import Request
from response_helpers import (
    button,
    image_gallery,
)
from state import STATE_REQUEST_KEY, STATE_RESPONSE_KEY, STATE_USER_UPDATE_KEY


class Prof(enum.Enum):
    UNKNOWN = 1
    ANALYST = 2
    TESTER = 3
    # состояния ниже и их обработка  введены для возможности получения помощи и перехода в начало теста
    WELCOMETEST = 4
    HELPME = 5

    @classmethod
    def from_request(cls, request: Request, intent_name: str):
        slots = request.intents
        slot = request.intents.get(intent_name, {})
        print(f'СЛОТЫ Тип: {type(slots)}, Значение: {slots}, Один слот: {slot} ')
        if slot != {}:
            slot = request.intents[intent_name]['slots']['prof']['value']
        elif intents.START_TOUR_TEST in request.intents:
            return cls.WELCOMETEST
        elif intents.HELP_ME in request.intents:
            return cls.HELPME
        if slot == 'analyst':
            return cls.ANALYST
        elif slot == 'tester':
            return cls.TESTER
        else:
            return cls.UNKNOWN


def move_to_prof_scene(request: Request, intent_name: str):
    prof = Prof.from_request(request, intent_name)
    if prof == Prof.ANALYST:
        return Analyst()
    elif prof == Prof.TESTER:
        return Tester()
    elif prof == Prof.WELCOMETEST:
        return WelcomeTest()
    elif prof == Prof.HELPME:
        return HelpMe()
    else:
        return UnknownProf()


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    """Генерация ответа сцены"""

    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """Проверка перехода к новой сцене"""

    def move(self, request: Request):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        text = ('Извините, я вас не поняла. Пожалуйста, попробуйте переформулировать.')
        # state=request.state
        # events=make_events(str(whoami()), event),
        return self.make_response(
            text,
            # state,
        )

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None,
                      state_user_update=None):
        response = {
            'text': text,
            'tts': tts if tts is not None else text,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        if state_user_update is not None:
            webhook_response[STATE_USER_UPDATE_KEY] = state_user_update
        return webhook_response


class TestTourScene(Scene):

    def handle_global_intents(self, request):
        if intents.START_TOUR_TEST in request.intents:
            return WelcomeTest()
        elif intents.START_TOUR in request.intents:
            return StartTour()
        elif intents.HELP_ME in request.intents:
            return HelpMe()


class HelpMe(TestTourScene):
    def reply(self, request: Request):
        text = ('Я вам помогу. Я могу запустить тест или разссказать о профессиях. Продолжим?')
        # state=request.state
        print(f'ПОМОЩЬ: {request.state}')
        add_state = {'prev_scene': request.state}
        return self.make_response(
            text,
            state=add_state,
        )

    def handle_local_intents(self, request: Request):
        if intents.WILL_CONTINUE in request.intents:
            print(f'ОБРАБОТКА ПОМОЩИ: {request.prev_state}')
            next_scene = SCENES.get(request.prev_state, DEFAULT_SCENE)()
            print(f'ОБРАБОТКА ПОМОЩИ СЛЕД СЦЕНА: {next_scene}')
            return next_scene
        elif intents.REPEAT_ME in request.intents:
            return HelpMe()
        # по умолчанию если не условие то уйдет в fallback


class WelcomeTest(TestTourScene):
    def reply(self, request: Request):
        # scenes = str(SCENES)
        text = ('Привет, дорогой друг! ' 
                'Я могу помочь Вам определиться с профессией при помощи короткого '
                'и занимательного теста. Или, если Вы уже работаете в АйТи - найти '
                'другие свои сильные стороны. Кстати, сама я в АйТи не работаю, '
                'поэтому не обижайся, если профессию подберу неправильно. '
                'Ну что, хотите пройти небольшой тест?')
        # тестирование сохранения параметров пользователя между сессиями
        # state_user_update = {'value': '42'} - записать
        # state_user_update={'value': None} - стереть
        return self.make_response(
            text,
            buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ],
            # state_user_update = state_user_update, # добавлен параметр в функцию
        )

    def handle_local_intents(self, request: Request):
        if intents.U_YES in request.intents:
            return Query_1()
        elif intents.REPEAT_ME in request.intents:
            return WelcomeTest()
        # по умолчанию если не условие то уйдет в fallback

    def fallback(self, request: Request):
        text = ('Извините, я вас не поняла. Мы таки идем в тест? ')
        # state=request.state
        # events=make_events(str(whoami()), event),
        return self.make_response(
            text,
            # state=state,
            buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ],
        )


class Query_1(TestTourScene):
    def reply(self, request: Request):
        text = ('Поздравляем вы прошли тест. Хотите поговорить о профессиях?')
        # тестирование сохранения параметров пользователя между сессиями
        return self.make_response(
            text,
            buttons=[
                button('Да', hide=True),
                button('Нет', hide=True),
            ],
        )

    def handle_local_intents(self, request: Request):
        if intents.U_YES in request.intents:
            return StartTour()


class StartTour(TestTourScene):
    def reply(self, request: Request):
        text = 'Отлично! Давайте поговорим о профессиях? О какой бы Вы хотели?'
        return self.make_response(
            text,
            state={
                'screen': 'start_tour'
            },
            buttons=[
                button('Аналитик'),
                button('Тестировщик'),
            ]
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR_WITH_PROF_SHORT:
            return move_to_prof_scene(request, intents.START_TOUR_WITH_PROF_SHORT)


class Analyst(TestTourScene):
    def reply(self, request: Request):
        return self.make_response(
            text='В будущем здесь появится рассказ об Аналитике. О ком еще рассказать?',
            state={
                'screen': 'start_tour'
            },
            buttons=[
                button('Аналитик'),
                button('Тестировщик'),
            ]
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR_WITH_PROF_SHORT:
            return move_to_prof_scene(request, intents.START_TOUR_WITH_PROF_SHORT)


class Tester(TestTourScene):
    def reply(self, request: Request):
        return self.make_response(
            text='В будущем здесь появится рассказ об Тестеровщике. О ком еще рассказать?',
            state={
                'screen': 'start_tour'
            },
            buttons=[
                button('Аналитик'),
                button('Тестировщик'),
            ]
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR_WITH_PROF_SHORT:
            return move_to_prof_scene(request, intents.START_TOUR_WITH_PROF_SHORT)


class UnknownProf(TestTourScene):
    def reply(self, request: Request):
        return self.make_response(
            text='Я такой профессии не знаю. О ком еще рассказать?',
            state={
                'screen': 'start_tour'
            },
            buttons=[
                button('Аналитик'),
                button('Тестировщик'),
            ]
        )

    def handle_local_intents(self, request: Request):
        if intents.START_TOUR_WITH_PROF_SHORT:
            return move_to_prof_scene(request, intents.START_TOUR_WITH_PROF_SHORT)


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}

DEFAULT_SCENE = WelcomeTest