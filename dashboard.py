import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Load the logo image
logo = Image.open('./assets/images/data_skool_logo.png')  # Make sure the path is correct
st.sidebar.image(logo, width=300)  # Adjust width as you like

# Set page config: title + emoji icon + layout
st.set_page_config(
    page_title="UdTracker: Udemy Courses Dashboard (dataskool-challenge)",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_data():
    return pd.read_csv("./assets/data/courses.csv", parse_dates=['published_datetime'])

df = load_data()

# Sidebar navigation with icons
st.sidebar.title("Navigation")

pages = {
    "📊 Overview": "overview",
    "📈 Publishing Trends": "publishing",
    "💰 Pricing & Revenue": "pricing",
    "🎥 Content & Engagement": "content",
    "📚 Subject Analysis": "subject",
    "🔍 Explore Data": "explore"
}

selection = st.sidebar.radio("Go to", list(pages.keys()))
page = pages[selection]
st.sidebar.title("Follow Me!")
st.sidebar.markdown("""
    [![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/@xwsein)
    [![GitHub](https://img.shields.io/badge/GitHub-000000?style=flat-square&logo=github&logoColor=white)](https://github.com/xwsein)
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/xwsain/)
""")
# ========== Pages ==========

if page == "overview":
    st.title("Courses Overview")
    total_courses = len(df)
    total_students = df['students'].sum()
    total_reviews = df['reviews'].sum()
    paid_count = df['is_paid'].value_counts().get('Paid', 0)
    free_count = df['is_paid'].value_counts().get('Free', 0)
    avg_price = df['price'][df['is_paid'] == 'Paid'].mean()
    avg_duration = df['content_duration_hr'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Courses", total_courses)
    col2.metric("Total Students", f"{total_students:,}")
    col3.metric("Total Reviews", f"{total_reviews:,}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Paid Courses", paid_count)
    col2.metric("Free Courses", free_count)
    col3.metric("Avg Course Price (Paid)", f"${avg_price:.2f}")

    st.metric("Avg Course Duration (hours)", f"{avg_duration:.2f}")

    pie_data = df['is_paid'].value_counts().reset_index()
    pie_data.columns = ['Type', 'Count']
    fig = px.pie(pie_data, names='Type', values='Count', title="Paid vs Free Courses")
    st.plotly_chart(fig)

    level_counts = df['level'].value_counts().reset_index()
    level_counts.columns = ['Level', 'Count']
    fig2 = px.bar(level_counts, x='Level', y='Count', title="Course Levels Distribution")
    st.plotly_chart(fig2)

elif page == "publishing":
    st.title("Publishing Trends")

    df['published_year'] = df['published_datetime'].dt.year
    yearly_courses = df.groupby('published_year').size().reset_index(name='Courses Published')
    fig = px.line(yearly_courses, x='published_year', y='Courses Published', markers=True, title="Courses Published Over Years")
    st.plotly_chart(fig)

    subject_year = df.groupby(['published_year', 'subject']).size().reset_index(name='Count')
    fig2 = px.area(subject_year, x='published_year', y='Count', color='subject', title="Courses Published by Subject Over Time")
    st.plotly_chart(fig2)

elif page == "pricing":
    st.title("Pricing & Revenue Insights")

    # Price distribution (for paid courses only)
    fig = px.histogram(df[df['is_paid'] == 'Paid'], x='price', nbins=30, title="Price Distribution of Paid Courses")
    st.plotly_chart(fig)

    # Average price by subject (for paid courses only)
    avg_price_subj = df[df['is_paid'] == 'Paid'].groupby('subject')['price'].mean().reset_index()
    fig2 = px.bar(avg_price_subj, x='subject', y='price', title="Average Price by Subject")
    st.plotly_chart(fig2)

    # Simplified estimated revenue for paid courses only (37% of revenue for all paid courses)
    df['estimated_revenue'] = df.apply(
        lambda row: row['price'] * row['students'] * 0.37 if row['is_paid'] == 'Paid' else 0,
        axis=1
    )

    # Top 10 Courses by Estimated Revenue
    top_revenue = df[df['is_paid'] == 'Paid'].sort_values('estimated_revenue', ascending=False).head(10)
    st.subheader("Top 10 Courses by Estimated Revenue")
    st.dataframe(top_revenue[['course_title', 'subject', 'price', 'students', 'estimated_revenue']])

    # Display a bar chart for Top 10 Courses by Estimated Revenue
    fig3 = px.bar(top_revenue, x='course_title', y='estimated_revenue', title="Top 10 Courses by Estimated Revenue",
                  labels={'course_title': 'Course Title', 'estimated_revenue': 'Estimated Revenue ($)'})
    st.plotly_chart(fig3)

elif page == "content":
    st.title("Content & Engagement Analysis")

    avg_duration_level = df.groupby('level')['content_duration_hr'].mean().reset_index()
    fig = px.bar(avg_duration_level, x='level', y='content_duration_hr', title="Average Content Duration by Level")
    st.plotly_chart(fig)

    fig2 = px.scatter(df, x='num_lectures', y='content_duration_hr', title="Number of Lectures vs Content Duration", hover_data=['course_title'])
    st.plotly_chart(fig2)

    fig3 = px.scatter(df, x='reviews', y='students', title="Reviews vs Students", hover_data=['course_title'])
    st.plotly_chart(fig3)

    st.subheader("Top 10 Courses by Students")
    top_students = df.sort_values('students', ascending=False).head(10)
    st.table(top_students[['course_title', 'students', 'reviews', 'price']])

elif page == "subject":
    st.title("Subject-wise Deep Dive")

    subj_metrics = df.groupby('subject').agg(
        avg_price=('price', 'mean'),
        avg_reviews=('reviews', 'mean'),
        avg_students=('students', 'mean'),
        course_count=('course_id', 'count')
    ).reset_index()

    fig = px.bar(subj_metrics, x='subject', y=['avg_price', 'avg_reviews', 'avg_students'], barmode='group', title="Average Price, Reviews & Students by Subject")
    st.plotly_chart(fig)

    level_subject = df.groupby(['subject', 'level']).size().reset_index(name='count')
    fig2 = px.bar(level_subject, x='subject', y='count', color='level', barmode='stack', title="Distribution of Course Levels by Subject")
    st.plotly_chart(fig2)

elif page == "explore":
    st.title("Explore Dataset")

    paid_filter = st.multiselect("Filter by Paid/Free", options=df['is_paid'].unique(), default=df['is_paid'].unique())
    level_filter = st.multiselect("Filter by Level", options=df['level'].unique(), default=df['level'].unique())
    subject_filter = st.multiselect("Filter by Subject", options=df['subject'].unique(), default=df['subject'].unique())
    date_range = st.date_input("Filter by Published Date Range", value=(df['published_datetime'].min(), df['published_datetime'].max()))

    filtered_df = df[
        (df['is_paid'].isin(paid_filter)) &
        (df['level'].isin(level_filter)) &
        (df['subject'].isin(subject_filter)) &
        (df['published_datetime'] >= pd.to_datetime(date_range[0])) &
        (df['published_datetime'] <= pd.to_datetime(date_range[1]))
    ]

    search_title = st.text_input("Search by Course Title")
    if search_title:
        filtered_df = filtered_df[filtered_df['course_title'].str.contains(search_title, case=False)]

    st.write(f"Showing {len(filtered_df)} courses")
    st.dataframe(filtered_df)
