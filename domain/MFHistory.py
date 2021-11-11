
class MFHistory:

    def __init__(self, mfId, asOn, nav, lastUpdated):
        self.__mfId = mfId
        self.__asOn = asOn
        self.__nav = nav
        self.__lastUpdated = lastUpdated
        self.error = None
        self.mfName = ''

    def get_error(self):
        return self.error

    def set_error(self, error):
        self.error = error

    def get_mfId(self):
        return self.__mfId

    def get_asOn(self):
        return self.__asOn

    def get_nav(self):
        return self.__nav

    def get_lastUpdated(self):
        return self.__lastUpdated

    def set_mfName(self, mfName):
        self.mfName = mfName

    def get_mfName(self):
        return self.mfName

    def __str__(self):
        return "FundInfo: [id: " + str(self.__mfId) + ", nav: " + str(self.__nav) + ", asOn: " + str(self.__asOn) + ", lastUpdated: " + str(self.__lastUpdated) + "]"

    def serialize(self):
        return {
            "mfName": self.__mfName,
            "mfId": self.__mfId,
            "asOn": self.__asOn,
            "nav": self.__nav,
            "lastUpdated": self.__lastUpdated
        }