# Fund Info Details


class ViewHistory:

    def __init__(self):
        self.historyList = []

    def get_historyList(self):
        return self.historyList

    def set_historyList(self, historyList):
        self.historyList = historyList

    def __str__(self):
        return "ViewHistory: [historyList: " + str(self.historyList) + "]"
