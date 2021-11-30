import datetime

class MFHistory:

    def __init__(self, mfId, asOn, nav, lastUpdated):
        self.__mfId = mfId
        self.__asOn = asOn
        self.__nav = float(nav)
        self.__lastUpdated = lastUpdated
        self.error = None
        self.mfName = ''
        self.asOnValue = 0
        self.diffPrevAsOnValue = 0

        date = datetime.datetime.strptime(asOn, "%d-%b-%Y")
        self.navdate = date
        self.asonday = int(date.day)
        self.asonmonth = int(date.month) - 1
        self.asonyear = int(date.year)

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

    def set_asOnValue(self, asOnValue):
        self.asOnValue = asOnValue

    def get_asOnValue(self):
        return self.asOnValue

    def __str__(self):
        return "MFHistory: [id: " + str(self.__mfId) + ", nav: " + str(self.__nav) + ", asOn: " + str(self.__asOn) + ", lastUpdated: " + str(self.__lastUpdated)  + ", navdate: " + str(self.navdate)  + "]"

    def serialize(self):
        return {
            "mfName": self.mfName,
            "mfId": self.__mfId,
            "asOn": self.__asOn,
            "nav": self.__nav,
            "lastUpdated": self.__lastUpdated
        }