class FeedbackManager:
    def __init__(self, templates: dict, language: str = "en"):
        self.templates = templates
        self.lang = language
        self.total_points = 0

    def get_message(self, condition: str, hit: bool, points: int) -> str:
        status = "hit" if hit else "miss"
        template = self.templates[self.lang][condition][status]
        return template.format(points=points)

    def update_points(self, condition: str, hit: bool) -> int:
        if condition == "win":
            delta = 10 if hit else 0
        elif condition == "lose":
            delta = 0 if hit else -10
        else:
            delta = 0
        self.total_points += delta
        return delta



