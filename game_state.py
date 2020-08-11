class GameState:
    def __init__(self, **kwargs):
        self.top_rules = {}
        self.__dict__.update(kwargs)

    def __str__(self):
        return str(self.top_rules)

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
                for rule in top_rules:
                    if key not in rule.keys:
                        top_rules.remove(rule)
            return top_rules
        else:
            return self.top_rules

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
        for rule in rules:
            for key in rule.keys:
                if key in self.top_rules:
                    self.top_rules[key].append(rule)
                else:
                    self.top_rules.update({key: [rule]})

    def remove_rules(self, *rules):
        for rule in rules:
            for key in rule.keys:
                if key in self.top_rules:
                    while rule in self.top_rules[key]:
                        self.top_rules[key].remove(rule)
