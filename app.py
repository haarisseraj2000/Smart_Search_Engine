import streamlit as st
from free_course import FreeCourse  
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("pymilvus").setLevel(logging.WARNING)

# Initialize the FreeCourse class
free_course = FreeCourse()

# Streamlit UI
st.title("Free Course Search")

# Search bar
query = st.text_input("Enter your search query:")

# Search button
if st.button("Search"):
    if query:
        # Call the search function
        results = free_course.search(query)
        
        # Display the results
        if results:
            for result in results:
                title = result.get('title', 'No Title')
                description = result.get('description', 'No Description')
                url = result.get('url', '#')
                
                # Display each result as a card
                st.markdown(f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px;">
                        <h3><a href="{url}" target="_blank">{title}</a></h3>
                        <p>{description}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No results found.")
    else:
        st.write("Please enter a query.")