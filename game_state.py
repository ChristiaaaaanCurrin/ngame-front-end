from event import Event, Subscriber


class GameState(Subscriber):
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super().__init__()  # initiates self as a Subscriber
        self.top_rules = {}  # dictionary of top_rules in game (keyed by rule.keys).
        # Rules are permitted to be in more than one entry
        self.changed = Event()  # creates event that broadcasts changes to self
        self.__dict__.update(kwargs)  # game_state holds arbitrary attributes to store miscellaneous game information

    def handle_event(self, *args, **kwargs):
        """
        the game_state responds to subscribed events by broadcasting changes
        """
        self.changed(*args, **kwargs)

    def __repr__(self):
        return 'GameState%s' % str(self.__dict__)

    def filter_top_rules(self, *keys):
        """
        :param keys: correspond with keys for self.top_rules
        :return: list of rules that are in all bins keyed by one of keys or all top rules if no keys are given
        """
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
        """
        :param keys: correspond with keys for self.top_rules
        :return: list of rules that are in any bins keyed by one of keys
        """
        top_rules = []
        for key in keys:
            if key in self.top_rules:
                for top_rule in self.top_rules[key]:
                    if top_rule not in top_rules:
                        top_rules.append(top_rule)
        return top_rules

    def get_all_rules(self, *keys):
        """
        :param keys: correspond with keys in self.top_rules
        :return: list of all rules and sub rules of rules in all bins keyed by one of keys
        """
        all_rules = []
        for top_rule in self.filter_top_rules(keys):
            for rule in top_rule.get_piece():
                if rule not in all_rules:
                    all_rules.append(rule)
        return all_rules

    def add_rules(self, *rules):
        """
        appends rules to appropriate entries of self.top_rules according to the rules keys, subscribes to changes from
        rules, subscribes rules to changes in self
        :param rules: rules to be added to self.top_rules
        """
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
        """
        purges rules from self.top_rules, unsubscribes from rules, unsubscribes rules from self
        :param rules:  rules to be removed from self.top_rules
        """
        self.unsubscribe(*[rule.changed for rule in rules])
        for top_rule in rules:
            for key in top_rule.keys:
                if key in self.top_rules:
                    while top_rule in self.top_rules[key]:
                        self.top_rules[key].remove(top_rule)
                        [rule.unsubscribe(self.changed) for rule in top_rule.get_piece()]
        self.changed()


if __name__ == "__main__":
    pass