# Fund Info Details


class ViewHistory:

    def __init__(self):
        self.historyList = []
        self.userFund = None
        self.navDiff = 0

    def get_historyList(self):
        return self.historyList

    def set_historyList(self, historyList):
        self.historyList = historyList

    def get_userFund(self):
        return self.userFund

    def set_userFund(self, userFund):
        self.userFund = userFund

    def get_navDiff(self):
        return self.navDiff

    def set_navDiff(self, navDiff):
        self.navDiff = navDiff

    def __str__(self):
        return "ViewHistory: [historyList: " + str(self.historyList) + "]"
