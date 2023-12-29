import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_excel(r"SHG_Booking_Data.xlsx")
    df['Booking Year'] = df['Booking Date'].dt.year
    df['Booking Month'] = df['Booking Date'].dt.strftime('%B')
    df['Profit/Loss'] = df['Revenue'] + df['Revenue Loss']
    return df

df = load_data()

# Add a title to your app
st.sidebar.markdown("<h3 style='text-align: center; color: black; font-size: 60px;'>SHG</h3> \n " , unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: black; font-size: 30px;'>Executive Overview</h3>"
                    "<h1 style='text-align: center; color: black; font-size: 30px;'>Dashboard</h1>", unsafe_allow_html=True)
# Create widgets for selecting year, month, hotel, and deposit type
year = st.sidebar.selectbox("Year", ['Total'] + sorted(df['Booking Year'].unique()), index=0)
month = st.sidebar.selectbox("Month", ['Total'] + sorted(df['Booking Month'].unique()), index=0)
hotel = st.sidebar.selectbox("Hotel", ['Total'] + sorted(df['Hotel'].unique()), index=0)
deposit_type = st.sidebar.selectbox('Deposit Type', ['Total'] + sorted(df['Deposit Type'].unique()), index=0)

# Apply filters
if year != 'Total':
    df = df[df['Booking Year'] == year]
if month != 'Total':
    df = df[df['Booking Month'] == month]
if hotel != 'Total':
    df = df[df['Hotel'] == hotel]
if deposit_type != 'Total':
    df = df[df['Deposit Type'] == deposit_type]

# Calculate total revenue, total bookings, and total cancellations
total_revenue = df['Revenue'].sum()/1e6
total_profit = df['Profit/Loss'].sum()/1e6
total_bookings = len(df)
total_cancellations = df['Cancelled (0/1)'].sum()

# Display the calculated values in each column
col1, col2 = st.columns([1,1])
# Image at the top
col1.markdown(f"<center>Revenue<br><h3><span style='color: {'lightgreen'};'>{total_revenue:.2f} M</h3></center>" , unsafe_allow_html=True)
col2.markdown(f"<center>Profit/Loss<br><h3><span style='color: {'lightblue'};'>{total_profit:.2f} M</span></h3>", unsafe_allow_html=True)


# Melt the DataFrame to have 'Revenue' and 'Profit' in the same column
melted_df = df.melt(id_vars='Country', value_vars=['Revenue', 'Profit/Loss'], var_name='Type', value_name='Amount')

# Create a DataFrame with the sum of 'Revenue' and 'Profit' for each country
grouped_df = melted_df.groupby(['Country', 'Type'])['Amount'].sum().reset_index()

# Filter the DataFrame to include only the top 10 countries by 'Revenue'
top_countries = grouped_df[grouped_df['Type'] == 'Revenue'].nlargest(10, 'Amount')['Country']

# Create your grouped bar plot with title
revenue_profit_fig = px.bar(grouped_df[grouped_df['Country'].isin(top_countries)].sort_values(by= 'Amount', ascending=True), 
                            y='Country', x='Amount', 
                            color='Type', barmode='group', 
                            title='Revenue and Profit by Country', 
                            color_discrete_map={'Revenue':'lightgreen', 'Profit/Loss':'lightblue'})

revenue_profit_fig.update_layout(xaxis_title="", yaxis_title="", legend_title="",  autosize=False, width=380, height=400, plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=0.8, y=0.05, traceorder="normal"))
revenue_profit_fig.update_xaxes(fixedrange=True)
revenue_profit_fig.update_yaxes(fixedrange=True)
# Display the figure
st.plotly_chart(revenue_profit_fig)

# Display the calculated values in each column
col1, col2 = st.columns([1,1])
col1.markdown(f"<center>Bookings<br><h3>{total_bookings}</h3></center>" , unsafe_allow_html=True)
col2.markdown(f"<center>Cancellations<br><h3><span style='color: {'gray'};'>{total_cancellations}</h3></center>" , unsafe_allow_html=True)

# Group the data by 'Booking Date' and calculate the sum of 'Cancelled (0/1)' and total bookings for each date
grouped_df =  df.groupby("Booking Date").agg({'Cancelled (0/1)': 'sum', 'Booking Date': 'count'}).rename(columns={'Booking Date': 'Total Bookings'}).reset_index()

# Create a line chart
fig = go.Figure()

# Add a line for cancelled bookings
fig.add_trace(go.Scatter(x=grouped_df['Booking Date'], y=grouped_df['Cancelled (0/1)'], mode='lines', name='Cancelled', line=dict(color='gray')))

# Add a line for total bookings
fig.add_trace(go.Scatter(x=grouped_df['Booking Date'], y=grouped_df['Total Bookings'], mode='lines', name='Total', line=dict(color='white')))

# Update the layout of the chart
fig.update_layout(xaxis_title="", yaxis_title="Bookingw ", title='Booking Count by Date',plot_bgcolor='rgba(0,0,0,0)', autosize=False, width=380, height=400, legend=dict(x=0.7, y=1, traceorder="normal"))
fig.update_xaxes(fixedrange=True)
fig.update_yaxes(fixedrange=True)

# Display the chart
st.plotly_chart(fig)

# Filter the DataFrame
filtered_df = df[df['Distribution Channel'] != 'Undefined']

# Create the pie chart for 'Status'
status_fig = px.pie(filtered_df.groupby("Status").size().reset_index(name='Booking Count'), 
                    names='Status', color='Status', values='Booking Count', 
                    title='Booking Count(Status)', 
                    color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'} )
status_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', autosize=False, width=380, height=400)
status_fig.update_xaxes(fixedrange=True)
status_fig.update_yaxes(fixedrange=True)
# Display the figure
st.plotly_chart(status_fig)
 
# Create the stacked bar chart for 'Customer Type'
cust_fig = px.bar(filtered_df.groupby(["Customer Type", "Status"]).size().reset_index(name='Count').sort_values(by= 'Count', ascending=True), 
         x='Customer Type', y='Count', 
         color='Status',  
         color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'})

cust_fig.update_layout(xaxis_title="Customer Type", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', barmode='stack', showlegend=False, autosize=False, width=380, height=430)
cust_fig.update_xaxes(fixedrange=True)
cust_fig.update_yaxes(fixedrange=True)
# Display the figure in the first column
st.plotly_chart(cust_fig)

# Create the stacked bar chart with the color map
dist_fig = px.bar(filtered_df.groupby(["Distribution Channel", "Status"]).size().reset_index(name='Count').sort_values(by= 'Count', ascending=True), 
         x='Distribution Channel', y='Count', 
         color='Status',  
         color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'})

dist_fig.update_layout(xaxis_title="Distribution Channel", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', barmode='stack', showlegend=False, autosize=False, width=380, height=430)
dist_fig.update_xaxes(fixedrange=True)
dist_fig.update_yaxes(fixedrange=True)
# Display the figure in the second column
st.plotly_chart(dist_fig)

 
