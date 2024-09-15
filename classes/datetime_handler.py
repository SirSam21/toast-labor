import jsonpickle
from datetime import datetime


class CustomDatetimeHandler(jsonpickle.handlers.DatetimeHandler):
    def flatten(self, obj, data):
        pickler = self.context
        if not pickler.unpicklable:
            return str(obj)
        cls, args = obj.__reduce__()
        flatten = pickler.flatten
        payload = obj.isoformat()
        args = [payload] + [flatten(i, reset=False) for i in args[1:]]
        data['__reduce__'] = (flatten(cls, reset=False), args)
        return data

    def restore(self, data):
        cls, args = data['__reduce__']
        unpickler = self.context
        restore = unpickler.restore
        cls = restore(cls, reset=False)
        value = datetime.fromisoformat(args[0])
        return value
