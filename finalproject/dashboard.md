# DX Analysis Dashbord

The [dashboard server](http://dx.jxqz.org) uses the [Streamlit](https://streamlit.io) framework. This particular framework was chosen because it is relatively simple, written in Python, and supports some nice geospatial visualization through the [pydeck library](https://deckgl.readthedocs.io/en/latest).

The deployment is via docker container running on a Debian Linux virtual machine at the Vultr cloud provider. An Nginx proxy provides a gateway to the container from the priveleged port 80 so the site can be accessed from the standard http port.

## Dashboard Feature Pages

The dashboard consists of 6 individual pages providing a particular feature or set of features. The DX spot data is queried over the HTTP REST API from [api.jxqz.org:8080](http://api.jxqz.org:8080). Solar weather data and dashboard user info are queried directly via SQL at present.

### User login page

This page allows the user to create a profile and then log in to the site. The profile stores some
basic information such as name an location as well as settings for the automated SMS alerting function. The user login info is stored directly in the *dashboard_users* via a database abstraction class and ultimately the [psycopg library](https://www.psycopg.org). It also allows the user to set their local timezone which is important to me because I am trying to monitor real-time activity and often dealing with timestamps in UTC which are hard to interpret at a glance.

### Main page

Shows a summary of current conditions starting with the latest solar indices stored in the *wwv_announcements* table by the [solar data fetcher](../homework5/fetch_solar_data.py) run four times a day from cron.

The real time spot analysis section includes two custom metrics: maximum observed frequency and 10m FM band status. These were prototyped in the Grafana monitoring dashboard and then implemented here. The gas gauge style metric is imported from the [Plotly library](https://plotly.com) extension to Streamlit. This section is a starting point for the development of future custom metrics relating to HF propagation conditions. These metrics are over the last 30 minutes and considered real-time for my purposes.

The band by band conditions is a red/yellow/green set of metrics. Red is no reports. Yellow is CW/Digital activity reports only -- marginal conditions. Green indicates two or more reports of voice signals, meaning band is in good condition for communications. These are also on a 30 minute period, which I consider real-time.

The final two charts are conditions on the 15,12, and 10 meter bands which are the prime mobile operating bands that achieve best results from my car. The time period for analysis is selectable 1-12 hours. The first chart is a fairly standard histogram. The second is a custom creation. It shows the frequency of the reported station plotted low to high with the scale normalized for the width of the band in kilohertz. It is designed to emulate a [waterfall plot](https://en.wikipedia.org/wiki/Waterfall_plot) that is common in ham radio. It allows me to see at a glance where the activity is in the band and how intense it is.

### Active Station Map

This page shows a world map with dots for active stations. Time period is selectable from 1-24 hours in steps and a specific band can be selected or all bands. This visualization uses the Pydeck scatterplotlayer. Hovering over a point shows callsign and frequency so you can tune your radio and talk to them right now! The raw data in tabular format is display in a drop down below the map as well.

### Great Circle Map

Also a mapping visualization, but it uses the Pydeck GreatCircleLayer and connects the two end points of the radio communication with an arc of the shortest path between them. This is my preferred visualization because it shows distance. Communication distance on a particular frequency can vary greatly over time due to changing solar conditions. The time period and band controls are on the left pop-out. This is different that the other pages. I am experimenting with the dashboard on the mobile (cell phone browser) to see which interface layout works best. 

### Latest Spots

This is a simple tabular display of reports. This can be filtered by time and band, and exported to CSV. The table widget is a [Streamlit dataframe](https://docs.streamlit.io/develop/api-reference/data/st.dataframe) interactive table, so you can hide columns, sort or do various useful things. Sometimes a list of stations is all I need and this fits the bill.

### Propagation Forecast

I enjoyed experimenting with various ML models such as sequential and RNN and I think they could be a good pathway for developing predictive models for radio propagation that have accuracy and rigor. The question for me was how much time it would take to achieve those results. As the project progressed, deployment and stability issues in other system components constrained my remaining time. I decided to go a slightly alternate route and use an LLM with extracted historical summary data to create a prediction for the next 24-72 hours, which is user selectable. Summary data are extracted from the REST API and then the data an a prompt are passed to an LLM via the [OpenAI API](https://openai.com/api) at a cost of about $.01 per prediction. Predictions are valid for a period of hours and are cached locally in the server to reduce the number of requests.

## Deployment Notes

I need to get an SSL cert for this site and configure the server with it.

### Future Development

I would like to be able to use this dashboard in some way via Android Auto in my car.