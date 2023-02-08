from state import STATE_REQUEST_KEY


class Request:
    def __init__(self, request_body):
        self.request_body = request_body

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def state(self):
        return self.request_body['state'].get(STATE_REQUEST_KEY, {}).get('scene', {})

    @property
    def prev_state(self):
        return self.request_body['state'].get(STATE_REQUEST_KEY, {}).get('prev_scene', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')

    @property
    def session(self):
        return self.request_body['session']