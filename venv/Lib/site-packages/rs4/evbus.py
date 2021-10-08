# cloned from: https://github.com/seanpar203/event-bus

import sys
from functools import wraps
from threading import Thread
from collections import defaultdict, Counter
from typing import Iterable, Callable, List, Dict, Any, Set, Union

class EventDoesntExist(Exception):
    pass


class EventBus:
    def __init__(self):
        self._events = defaultdict(set)

    def __repr__(self):
        return "<{}: {} subscribed events>".format(
            self.cls_name,
            self.event_count
        )

    def __str__(self):
        return "{}".format(self.cls_name)

    @property
    def event_count(self):
        return self._subscribed_event_count()

    @property
    def cls_name(self):
        return self.__class__.__name__

    def on(self, event):
        def outer(func):
            self.add_event(func, event)
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return outer

    def add_event(self, func, event):
        self._events[event].add(func)

    def emit(self, event, *args, **kwargs):
        threads = kwargs.pop('threads', None)
        if threads:
            [ Thread (target=f, args=args, kwargs=kwargs).start() for f in self._event_funcs(event) ]
        else:
            [ func(*args, **kwargs) for func in self._event_funcs(event) ]

    def emit_only(self, event, func_names, *args, **kwargs):
        if isinstance(func_names, str):
            func_names = [func_names]
        for func in self._event_funcs(event):
            if func.__name__ in func_names:
                func(*args, **kwargs)

    def emit_after(self, event):
        def outer(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                returned = func(*args, **kwargs)
                self.emit(event)
                return returned
            return wrapper
        return outer

    def remove_event(self, func_name, event):
        event_funcs_copy = self._events[event].copy()
        for func in self._event_funcs(event):
            if func.__name__ == func_name:
                event_funcs_copy.remove(func)

        if self._events[event] == event_funcs_copy:
            err_msg = "function doesn't exist inside event {} ".format(event)
            raise EventDoesntExist(err_msg)
        else:
            self._events[event] = event_funcs_copy

    def _event_funcs(self, event):
        for func in self._events[event]:
            yield func

    def _event_func_names(self, event):
        return [func.__name__ for func in self._events[event]]

    def _subscribed_event_count(self):
        event_counter = Counter()
        for key, values in self._events.items():
            event_counter[key] = len(values)
        return sum(event_counter.values())
