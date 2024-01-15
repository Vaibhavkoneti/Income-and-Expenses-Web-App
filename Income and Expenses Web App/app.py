import calendar
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from neo4jdb import  insert_data, fetch_all_periods, get_period_data, get_graph



def main():
# -----settings----
    incomes = ["Salary", "Other Income"]
    expenses = ["Rent", "Utensils", "Groceries", "Car", "Other Expenses", "Savings"]
    currency = "EUR"
    page_title = "Income and Expense Tracker"
    page_icon = "💸"  # Replace with a valid Emoji code for your desired icon
    layout = "centered"

    st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    st.title(f"{page_title} {page_icon}")

    years = [datetime.today().year,datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)


    selected = option_menu(menu_title=None,options=["Data Entry","Data Visualization"],icons=["pencil-fill","bar-chart-fill"],orientation="horizontal")

    if selected == "Data Entry":
        st.header(f"Data Entry in {currency}")

        with st.form(" entry_form",clear_on_submit=True):
            col1,col2 = st.columns(2)
            col1.selectbox("Select Month:",months,key = "months")
            col2.selectbox("Select Year:",years,key = "year")

            "---"

            with st.expander("Income"):
                for income in incomes:
                    st.number_input(f"{income}:",min_value=0,format="%i",step=10,key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:",min_value=0,format="%i",step=10,key=expense)
            with st.expander("Comment"):
                    st.text_area("",placeholder="Enter a comment here ....")
            
            "---"

            

            submitted = st.form_submit_button("Save Data")
            if submitted:
                period = str(st.session_state["year"]) +"_ "+str(st.session_state["month"])
                incomes = {income : st.session_state[income] for income in incomes}
                expenses = {expense : st.session_state[expense] for expense in expense}
                
                graph = get_graph()
                insert_data(graph, period, incomes, expenses, st.session_state['comment'])

    if selected == "Data Visualization":
        st.header("Data Visualization")
        with st.form("saved_periods"):
            graph = get_graph()
            periods = fetch_all_periods(graph)
            period = st.selectbox("Select Period:", periods)
            submitted = st.form_submit_button("Plot Period")
            if submitted:
                # Get data from database
                period_data = get_period_data(period)
                comment = period_data.get("comment")
                expenses = period_data.get("expenses")
                incomes = period_data.get("incomes")

                # Create metrics
                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{total_income} {currency}")
                col2.metric("Total Expense", f"{total_expense} {currency}")
                col3.metric("Remaining Budget", f"{remaining_budget} {currency}")
                st.text(f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)

              
        





if __name__ == "__main__":
    main()
