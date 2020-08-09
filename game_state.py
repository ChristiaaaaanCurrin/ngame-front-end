

class GameState:
    def __init__(self, *rules, **kwargs):
        self._top_rules = []
        self.add_pieces(*rules)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self.__dict__)

    def get_top_rules(self, *players):
        if players:
            return filter(lambda x: x.player in players, self._top_rules)
        else:
            return self._top_rules

    def get_all_rules(self):
        all_rules = []
        for top_rule in self._top_rules:
            all_rules.extend(top_rule.get_piece())
        return all_rules

    def add_rules(self, *rules):
        for rule in rules:
            if rule in self._top_rules:
                self._top_rules.append(rule)

    def add_pieces(self, *top_rules):
        for top_rule in top_rules:
            if top_rule not in self._top_rules:
                self._top_rules.append(top_rule)
                for rule in top_rule.get_piece():
                    rule.game_state = self

    def remove_pieces(self, *top_rules):
        for rule in top_rules:
            while rule in self._top_rules:
                self._top_rules.remove(rule)


