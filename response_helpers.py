import datetime
import sys



# узнаем имя функции для аналитики
def whoami():
    return sys._getframe(1).f_code.co_name


# В данном модуле располагаются вспомогательные функции
def button(title, payload=None, url=None, hide=False):
    button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None:
        button['payload'] = payload
    if url is not None:
        button['url'] = url
    return button


def image_gallery(image_ids):
    items = [{'image_id': image_id} for image_id in image_ids]
    return {
        'type': 'ImageGallery',
        'items': items,
    }


def image_list(image_ids, image_titles=[], image_descriptions=[], footer_text='Footer text'):
    items = [{'image_id': image_id} for image_id in image_ids]
    if len(image_ids) != len(image_titles) or len(image_ids) != len(image_descriptions):
        i = 0
        while i < len(items):
            items[i]['title'] = 'Title ' + str(i)
            items[i]['description'] = 'Description' + str(i)
            i += 1
        else:
            i = 0
            while i < len(items):
                items[i]['title'] = image_titles[i]
                items[i]['description'] = image_descriptions[i]
                i += 1
    return {
        'type': 'ItemsList',
        'items': items,
        "footer": {
            "text": footer_text,
            }
    }


def image_card(image_id, title='Title card', description="Card's description"):
    return {
        'type': 'BigImage',
        'image_id': image_id,
        'title': title,
        'description': description,
    }


def make_events(name, event):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    events={
        'events':[
            {
                "name": name,
                "value": {
                    "user_id": event['session']['user_id'],
                    "user": event['state']['user'],
                    "session_id": event['session']['session_id'],
                    "timestamp": now,
                    "command": event['request']['command'],
                    "application_id": event['session']['application']['application_id'],
                    "application": event['state']['application'],
                    "client_id": event['meta']['client_id'],
                }
            }
        ]
    }
    return events