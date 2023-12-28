import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_excel(r"C:\Users\HP\Desktop\SHG_Booking_Data.xlsx")
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

# Create four columns
col3, col4, col5, col6 = st.columns(4)

# Display the calculated values in each column
# Image at the top
col3.markdown(f"<center>Revenue<br><h1><span style='color: {'lightgreen'};'>{total_revenue:.2f} M</h1></center>" , unsafe_allow_html=True)
col4.markdown(f"<center>Profit/Loss<br><h1><span style='color: {'lightblue'};'>{total_profit:.2f} M</span></h2>", unsafe_allow_html=True)
col5.markdown(f"<center>Bookings<br><h1>{total_bookings}</h1></center>" , unsafe_allow_html=True)
col6.markdown(f"<center>Cancellations<br><h1><span style='color: {'gray'};'>{total_cancellations}</h1></center>" , unsafe_allow_html=True)

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

revenue_profit_fig.update_layout(xaxis_title="", yaxis_title="", legend_title="", title_x=0.5, autosize=False, width=700, height=530, plot_bgcolor='rgba(0,0,0,0)', legend=dict(x=0.8, y=0.05, traceorder="normal"))

# Display the figure
st.plotly_chart(revenue_profit_fig)

# Filter the DataFrame
filtered_df = df[df['Distribution Channel'] != 'Undefined']

# Create the pie chart for 'Status'
status_fig = px.pie(filtered_df.groupby("Status").size().reset_index(name='Booking Count'), 
                    names='Status', color='Status', values='Booking Count', 
                    title='Booking Count(Status)', 
                    color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'} )
status_fig.update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', autosize=False, width=700, height=400)

# Display the figure
st.plotly_chart(status_fig)

# Create two columns for the bar charts
col1, col2 = st.columns(2)

# Create the stacked bar chart for 'Customer Type'
cust_fig = px.bar(filtered_df.groupby(["Customer Type", "Status"]).size().reset_index(name='Count').sort_values(by= 'Count', ascending=True), 
         x='Customer Type', y='Count', 
         color='Status',  
         color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'})

cust_fig.update_layout(xaxis_title="Customer Type", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', barmode='stack', showlegend=False, autosize=False, width=380, height=430)

# Display the figure in the first column
col1.plotly_chart(cust_fig)

# Create the stacked bar chart with the color map
dist_fig = px.bar(filtered_df.groupby(["Distribution Channel", "Status"]).size().reset_index(name='Count').sort_values(by= 'Count', ascending=True), 
         x='Distribution Channel', y='Count', 
         color='Status',  
         color_discrete_map={'Check-Out': 'lightgreen', 'Canceled':'gray', 'No-Show':'Salmon'})

dist_fig.update_layout(xaxis_title="Distribution Channel", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', barmode='stack', showlegend=False, autosize=False, width=380, height=430)

# Display the figure in the second column
col2.plotly_chart(dist_fig)


# Create the line chart for 'Cancellations Over Time'
cancelled_fig = px.line(filtered_df.groupby("Booking Date")["Cancelled (0/1)"].sum().reset_index(), 
                        x='Booking Date', y='Cancelled (0/1)',
                        title='Cancellations Over Time')
cancelled_fig.update_traces(line=dict(color='gray'))
cancelled_fig.update_layout(xaxis_title="", yaxis_title="", title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', autosize=False, width=700, height=400)

# Display the figure
st.plotly_chart(cancelled_fig)
 