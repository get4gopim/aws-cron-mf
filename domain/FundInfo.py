# Fund Info Details


class FundInfo:

    def __init__(self, mfId, mfUrl, mfName, asOn, nav, lastUpdated):
        self.__mfId = mfId
        self.__mfName = mfName
        self.__mfUrl = mfUrl
        self.__asOn = asOn
        self.__nav = nav
        self.__lastUpdated = lastUpdated
        self.error = None

    def get_error(self):
        return self.error

    def set_error(self, error):
        self.error = error

    def get_mfId(self):
        return self.__mfId

    def get_mfUrl(self):
        return self.__mfUrl

    def get_mfName(self):
        return self.__mfName

    def get_asOn(self):
        return self.__asOn

    def get_nav(self):
        return self.__nav

    def get_lastUpdated(self):
        return self.__lastUpdated

    def __str__(self):
        return "FundInfo: [id: " + str(self.__mfId) + ", uri: " + str(self.__mfUrl) + ", fundName: " + str(self.__mfName) + ", asOn: " + str(self.__asOn) + ", lastUpdated: " + str(self.__lastUpdated) + "]"

    def serialize(self):
        return {
            "mfId": self.__mfId,
            "mfUrl": self.__mfUrl,
            "mfName": self.__mfName,
            "asOn": self.__asOn,
            "nav": self.__nav,
            "lastUpdated": self.__lastUpdated
        }