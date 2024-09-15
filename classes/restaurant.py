from .utils import get_restaurants_info


class Restaurant:
    def __init__(self, name, employees=[]):
        self.employees = employees
        self.name = name
        self.id = -1
        self.server_tip_percentage = 0
        self.cook_tip_percentage = 0

        for r in get_restaurants_info():
            if self.name == r["name"]:
                self.server_tip_percentage = r["jobs"]["server"]["tipPool"]
                self.cook_tip_percentage = r["jobs"]["cook"]["tipPool"]
                self.id = r["externalId"]
                break
