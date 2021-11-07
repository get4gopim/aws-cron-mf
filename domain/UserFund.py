# Fund Info Details


class UserFund:

    def __init__(self, userId, mfId, purchaseValue, purchaseNav, stampPercent, actualValue, units, latestValue, profitLoss, dateCreated, dateModified):
        self.__userId = userId
        self.__mfId = mfId
        self.__purchaseValue = purchaseValue
        self.__purchaseNav = purchaseNav
        self.__stampPercent = stampPercent
        self.__actualValue = actualValue
        self.__units = units
        self.__latestValue = latestValue
        self.__profitLoss = profitLoss
        self.__dateCreated = dateCreated
        self.__dateModified = dateModified
        self.error = None
        self.mfName = ''
        self.nav = ''
        self.asOn = ''

    def get_error(self):
        return self.error

    def set_error(self, error):
        self.error = error

    def get_userId(self):
        return self.__userId

    def get_mfId(self):
        return self.__mfId

    def get_purchaseValue(self):
        return self.__purchaseValue

    def get_purchaseNav(self):
        return self.__purchaseNav

    def get_stampPercent(self):
        return self.__stampPercent

    def get_actualValue(self):
        return self.__actualValue

    def get_units(self):
        return self.__units

    def get_latestValue(self):
        return self.__latestValue

    def get_profitLoss(self):
        return self.__profitLoss

    def get_dateCreated(self):
        return self.__dateCreated

    def get_dateModified(self):
        return self.__dateModified

    def set_mfName(self, mfName):
        self.mfName = mfName

    def get_mfName(self):
        return self.mfName

    def set_nav(self, nav):
        self.nav = nav

    def get_nav(self):
        return self.nav

    def set_asOn(self, asOn):
        self.asOn = asOn

    def get_asOn(self):
        return self.asOn


    def __str__(self):
        return "UserFund: [userId: " + str(self.__userId) + ", mfId: " + str(self.__mfId) \
               + ", purchaseValue: " + str(self.__purchaseValue) + ", purchaseNav: " + str(self.__purchaseNav) \
               + ", stampPercent: " + str(self.__stampPercent) + ", actualValue: " + str(self.__actualValue) \
               + ", units: " + str(self.__units) \
               + ", latestValue: " + str(self.__latestValue) + ", profitLoss: " + str(self.__profitLoss) \
               + ", dateCreated: " + str(self.__dateCreated) + ", dateModified: " + str(self.__dateModified) + "]"

    def serialize(self):
        return {
            "userId": self.__userId,
            "mfId": self.__mfId,
            "purchaseValue": str(self.__purchaseValue),
            "purchaseNav": str(self.__purchaseNav),
            "stampPercent": str(self.__stampPercent),
            "actualValue": str(self.__actualValue),
            "units": str(self.__units),
            "latestValue": str(self.__latestValue),
            "profitLoss": str(self.__profitLoss),
            "mfName": str(self.get_mfName()),
            "nav": str(self.get_nav()),
            "asOn": str(self.get_asOn()),
            "dateCreated": self.__dateCreated,
            "dateModified": self.__dateModified
        }