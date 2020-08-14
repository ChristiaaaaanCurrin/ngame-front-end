class Event(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return 'Event'#%s' % list.__repr__(self)


class Subscriber:
    def __init__(self, *events):
        self.subscriptions = []
        self.update_flag = True
        for event in events:
            self.subscribe(event)

    def handle_event(self, *args, **kwargs):
        self.update_flag = True

    def subscribe(self, *events):
        for event in events:
            if event not in self.subscriptions:
                self.subscriptions.append(event)
                event.append(self.handle_event)

    def unsubscribe(self, *events):
        for event in events:
            while event in self.subscriptions:
                self.subscriptions.remove(event)
            while self.handle_event in event:
                event.remove(self.handle_event)

    def set_subscription(self, *events):
        old = self.subscriptions
        self.unsubscribe(*old)
        self.subscribe(*events)


if __name__ == "__main__":
    test_events = [Event() for n in range(3)]

    test_sub = Subscriber()
    test_sub.set_subscription(test_events[0])
    print(test_sub)
    test_sub.set_subscription(*test_events)
    print(test_sub)