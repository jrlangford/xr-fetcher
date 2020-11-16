class Success:
    def __init__(self, success=True, description=""):
        self.success = success
        self.description = description

class Rate:
    def __init__(self, last_updated, value, status):
        self.last_updated = last_updated
        self.value = value
        self.status = status

class FullRates:
    def __init__(self, dof, fixer, banxico):
        self.dof = dof
        self.fixer = fixer
        self.banxico = banxico

class WrappedRates:
    def __init__(self, rates):
        self.rates = rates
