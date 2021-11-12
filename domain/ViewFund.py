# Fund Info Details


class ViewFund:

    def __init__(self):
        self.fundList = []
        self.totalInvestment = 0
        self.totalProfit = 0
        self.totalPercentile = 0
        self.eqInvestment = 0
        self.eqProfit = 0
        self.eqPercentile = 0

    def get_fundList(self):
        return self.fundList

    def set_fundList(self, fundList):
        self.fundList = fundList

    def get_totalInvestment(self):
        return self.totalInvestment

    def set_totalInvestment(self, totalInvestment):
        self.totalInvestment = totalInvestment

    def get_totalProfit(self):
        return self.totalProfit

    def set_totalProfit(self, totalProfit):
        self.totalProfit = totalProfit

    def get_totalPercentile(self):
        return self.totalPercentile

    def set_totalPercentile(self, totalPercentile):
        self.totalPercentile = totalPercentile

    # ----------

    def get_eqInvestment(self):
        return self.eqInvestment

    def set_eqInvestment(self, eqInvestment):
        self.eqInvestment = eqInvestment

    def get_eqProfit(self):
        return self.eqProfit

    def set_eqProfit(self, eqProfit):
        self.eqProfit = eqProfit

    def get_eqPercentile(self):
        return self.eqPercentile

    def set_eqPercentile(self, eqPercentile):
        self.eqPercentile = eqPercentile

    def __str__(self):
        return "UserFund: [totalInvestment: " + str(self.totalInvestment) + ", totalProfit: " + str(self.totalProfit) \
               + ", totalPercentile: " + str(self.totalPercentile) + "]"

