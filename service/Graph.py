import plotly.express as px
from service import MFHistoryService

historyList = MFHistoryService.get_funds_history('MES016')

nav = []
date = []

for mf_history in historyList:
    nav.append(mf_history.get_nav())
    date.append(mf_history.get_asOn())

# Creating the Figure instance
fig = px.line(x=date, y=nav, title="Nav History", width=800, height=500)

# printing the figure instance
print(fig)
fig.show()


def show():
    historyList = MFHistoryService.get_funds_history('MES016')

    x = []
    y = []

    for mf_history in historyList:
         x.append(mf_history.get_nav())
         y.append(mf_history.get_asOn())

    df = px.data.stocks()
    print (df)
    fig = px.line(df, x='date', y="GOOG")
    fig.show()