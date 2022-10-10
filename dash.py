import pandas as pd
import streamlit as st
# import matplotlib.dates as mdates
# import matplotlib.pyplot as plt
import altair as alt

df = pd.read_json("output.json", orient="split")
df = df.rename(columns={'date': 'Date', 'pm2.5':'PM 2 5', 'pm10': 'PM 10', 'hum': 'Humidity', 'tem': 'Temperature',
                        'aqi': 'AQI'})
df['Date'] = df['Date'].dt.tz_localize(None)
df['Date'] = df['Date'].dt.tz_localize('Asia/Singapore')
# functions -----------------
@st.cache
def convert_datetime(x):
    if x == '2M':
        x = 60 * 24
    elif x == '1M':
        x = 30 * 24
    elif x == '2W':
        x = 7 * 2 * 24
    elif x == '1W':
        x = 7 * 24
    elif x == '24H':
        x = 24
    return x

@st.cache(allow_output_mutation=True)
def get_data(days, cols):
    dat = df.loc[len(df) - days:, cols]
    return dat

@st.cache(allow_output_mutation=True)
def get_chart(data, measure):
    cols = sorted(data[measure].unique())

    base = alt.Chart(data).encode(
        alt.X('Date:T', title='Date')
    )

    hover = alt.selection_single(
        fields=["Date"],
        nearest=True,
        on="mouseover",
        empty="none",
        clear='mouseout'
    )

    lines = base.mark_line().encode(
              alt.Y("value:Q", title='Value'),
              alt.Color(measure, legend=alt.Legend(
            orient='top',
            legendX=0, legendY=0,
            direction='horizontal',
            titleAnchor='start')
                       )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    rule = base.transform_pivot(
        measure, value='value', groupby=['Date']
    ).mark_rule().encode(
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[alt.Tooltip("Date", title="Date"),
                alt.Tooltip("dayhoursminutes(Date):O", title="Time")] +
                [alt.Tooltip(c, type='quantitative') for c in cols]
    ).add_selection(hover)

    return lines + points + rule
    # tooltips = (
    #     alt.Chart(data)
    #     .mark_rule(color='green')
    #     .encode(
    #         x="date:T",
    #         y="value:Q",
    #         opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
    #         tooltip=[
    #             alt.Tooltip("date", title="Date"),
    #             alt.Tooltip("dayhoursminutes(date):O", title="Time"),
    #             alt.Tooltip(c, type='quantitative') for c in list(data.columns)
    #         ],
    #     )
    #     .add_selection(hover)
    # )
    # return lines + points + tooltips
@st.cache(allow_output_mutation=True)
def get_heatmap(data, measure):
    # color = alt.condition((datum.AQI <= 50), alt.ColorValue('green'), alt.condition(
    #         (datum.AQI <= 100), alt.ColorValue('yellow'), alt.condition(
    #         (datum.AQI <= 200), alt.ColorValue('orange'), alt.condition(
    #         (datum.AQI <= 300), alt.ColorValue('Red'), alt.ColorValue('brown')
    #         ))))

    c = alt.Chart(data).mark_rect().encode(
        alt.X('Date:T', title='Hour'),
        alt.Y('monthdate(Date):O', title='Date'),
        alt.Color(measure+':Q',
        legend=alt.Legend(
            title=' ',
            orient='top',
            legendX=0, legendY=0,
            direction='horizontal',
            titleAnchor='start')),
        tooltip=[alt.Tooltip("Date", title="Date"),
                alt.Tooltip("dayhoursminutes(Date):O", title="Time"),
                alt.Tooltip(measure+':Q', title=measure)]
    )
    return c
# row 0: Title
r0c1, r0c2 = st.columns([5,1])
with r0c1:
    st.markdown('### Weather and Pollution in Subang Jaya, Selangor')
with r0c2:
    st.caption('Last updated: '+str(df.iat[-1,0])[0:-9])

# row 1: current conditions

r1c0, r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([0.5,1,1,1,1,1])
with r1c0:
    st.write('Now: ')
with r1c1:
    st.write("\U0001F321: "+str(df.iloc[len(df)-1, 5].round(1))+" \u2103")

with r1c2:
    st.write("\U0001F4A7: "+str(df.iloc[len(df)-1, 4].round(1))+" %")

with r1c3:
    curr_aqi = round(df.iloc[len(df)-1, 6])
    # curr_aqi = 301
    if curr_aqi <= 50:
        col = "\U0001F7E2" # green
    elif curr_aqi <= 100:
        col = "\U0001F7E1" # yellow
    elif curr_aqi <= 200:
        col = "\U0001F7E0" # orange
    elif curr_aqi <= 300:
        col = "\U0001F534" # red
    else:
        col = "\U0001F7E4" #brown
    st.write("AQI: "+str(curr_aqi)+" "+col)

with r1c4:
    st.write("PM2.5: "+str(round(df.iloc[len(df)-1, 1]))+" \u338D/\u33A5")

with r1c5:
    st.write("PM10: "+str(round(df.iloc[len(df)-1, 2]))+" \u338D/\u33A5")

# row 1.1: select units:

# r0c1, r0c2 = st.columns([6,1])
# with r0c2:
#     st.selectbox(
#         '',
#         ('Metric', 'Imperial'),
#         key=0
#     )

# Row 2: time series graphs and map ---------------
st.write(' \n \n')
st.markdown('##### Historical Data')
# st.markdown('###### Time Series:')
r2c1, r2c3 = st.columns([6,1])
# with r2c1:
#     pm = df.loc[len(df)-24:, ["date","pm2.5","pm10"]]
#     # for key, dat in pm25["date"]:
#     #     pm25.iloc
#
#     # plt.style.use()
#     fig, ax = plt.subplots()
#     locator = mdates.AutoDateLocator(minticks=23, maxticks=24)
#     formatter = mdates.ConciseDateFormatter(locator)
#     # formatter.formats = ['%H:%M']
#     # formatter.zero_formats = ['%d-%b']
#     formatter.offset_formats = ['', '%Y', '%b %Y', '%d %b %Y', '%d %b %Y', '%d %b %Y %H:%M']
#     ax.xaxis.set_major_locator(locator)
#     ax.xaxis.set_major_formatter(formatter)
#     ax.plot(pm["date"], pm["pm2.5"], color="purple", linewidth=2)
#     ax.plot(pm["date"], pm["pm10"], color="blue", linewidth=2)
#     for label in ax.get_xticklabels():
#         label.set_rotation(40)
#         label.set_horizontalalignment('right')
#     ax.legend()
#     # plt.show
#     st.pyplot(fig)
import numpy as np
with r2c1:
    pmopt = st.multiselect(
        'Select data:',
        ['PM 2.5', 'PM 10', 'AQI', 'Temperature', 'Humidity'],
        ['PM 2.5', 'PM 10', 'AQI', 'Temperature', 'Humidity']
        )
# opt = []
# st.write('opt'+str(opt))
for i in range(len(pmopt)):
    if pmopt[i] == 'PM 2.5':
        pmopt[i] = 'PM 2 5'
#     elif pmopt[i] == 'PM10':
#         opt.append('pm10')
#     elif pmopt[i] == 'AQI':
#         opt.append('aqi')
#     elif pmopt[i] == 'Temperature':
#         opt.append('tem')
#     elif pmopt[i] == 'Humidity':
#         opt.append('hum')
# with r2c2:
#     mode = 'Pollution'
#     if st.button(mode):
#         #switch to other
#         mode = 'Weather'
#     else:
#         mode = 'Pollution'
# st.write(opt)
# st.write(pmopt)
with r2c3:
    pmdate = st.selectbox(
        'Select range:',
        ('24H', '1W', '2W', '1M', '2M'),
        key=1
        )
pmopt.append("Date")
pmdat = convert_datetime(pmdate)
pm = get_data(pmdat, pmopt)
pm[pmopt] = pm[pmopt].round()
pm = pm.melt('Date', var_name='Measure', value_name='value')
# st.write(pm)

chart = get_chart(pm, 'Measure')

st.altair_chart(
    chart.interactive(),
    use_container_width=True
)
# row 3 - temp chart
# st.markdown('###### Heatmap')
r3c1, r3c2, r3c3 = st.columns([1.1,5.4,1])
# with r3c1:
#     temopt = st.multiselect(
#         '',
#         ['Temperature', 'Humidity', 'AQI'],
#         ['Temperature', 'Humidity', 'AQI']
#         )
# for i in range(len(temopt)):
#     if temopt[i] == 'Temperature':
#         temopt[i] = 'tem'
#     elif temopt[i] == 'Humidity':
#         temopt[i] = 'hum'
#     elif temopt[i] == 'AQI':
#         temopt[i] = 'aqi'
# # st.write(temopt)
# with r3c3:
#     temdate = st.selectbox(
#         '',
#         ('24H', '1W', '1M', '2M'),
#         key=2
#         )
# temopt.append("date")
#
# temdat = convert_datetime(temdate)
# tem = get_data(temdat, temopt)
# tem[temopt] = tem[temopt].round(1)
# tem = tem.melt('date', var_name='Measure', value_name='value')
#
# c2 = get_chart(tem, "Measure")
# st.altair_chart(c2, use_container_width=True)

# row 3: map
with r3c1:
    hmopt = st.selectbox(
        'Select data:',
        ('AQI', 'PM 2.5', 'PM 10'),
        key=2
    )
if hmopt == 'PM 2.5':
    hmopt = 'PM 2 5'
with r3c3:
    hmdate = st.selectbox(
        'Select range:',
        ('1W', '2W','1M', '2M'),
        key=3)
hmdat = convert_datetime(hmdate)
hm = get_data(hmdat, ['Date', hmopt])
# hm = get_data(hmdat, hmopt)
# st.write(hmdat)
chart2 = get_heatmap(hm, hmopt)
st.altair_chart(
    chart2.interactive(),
    use_container_width=True
)
sen = pd.DataFrame({'lat': [3.06875], 'lon': [101.58338]})
# st.map(sen)
