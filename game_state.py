from event import Event, Subscriber


class GameState(Subscriber):
    def __init__(self, **kwargs):
        super().__init__()
        self.top_rules = {}
        self.changed = Event()
        self.__dict__.update(kwargs)

    def handle_event(self, *args, **kwargs):
        self.changed()

    def __repr__(self):
        return 'GameState%s' % str(self.__dict__)

    def __getitem__(self, item):
        state = self
        while item:
            key, *item = item
            if key in state.__dict__:
                state = state.__dict__[key]
        return state

    def filter_top_rules(self, *keys):
        if keys:
            start, *keys = keys
            top_rules = self.top_rules[start]
            for key in keys:
                top_rules = filter(lambda r: key in r.keys, top_rules)
            return top_rules
        else:
            top_rules = []
            [top_rules.extend(rules) for rules in self.top_rules.values()]
            return top_rules

    def get_top_rules(self, *keys):
        top_rules = []
        for key in keys:
            if key in self.top_rules:
                for top_rule in self.top_rules[key]:
                    if top_rule not in top_rules:
                        top_rules.append(top_rule)
        return top_rules

    def get_all_rules(self, *keys):
        all_rules = []
        for key in keys:
            if key in self.top_rules:
                for top_rule in self.top_rules[key]:
                    for rule in top_rule.get_piece():
                        if rule not in all_rules:
                            all_rules.append(rule)
        return all_rules

    def add_rules(self, *rules):
        self.subscribe(*[rule.changed for rule in rules])
        for top_rule in rules:
            for key in top_rule.keys:
                if key in self.top_rules:
                    self.top_rules[key].append(top_rule)
                else:
                    self.top_rules.update({key: [top_rule]})
                for rule in top_rule.get_piece():
                    rule.game_state = self
                    rule.subscribe(self.changed)
        self.changed()

    def remove_rules(self, *rules):
        self.unsubscribe(*[rule.changed for rule in rules])
        for rule in rules:
            for key in rule.keys:
                if key in self.top_rules:
                    while rule in self.top_rules[key]:
                        self.top_rules[key].remove(rule)
        self.changed()


if __name__ == "__main__":
    pass