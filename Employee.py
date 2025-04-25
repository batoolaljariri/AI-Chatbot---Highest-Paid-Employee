import os
import json
import re
import streamlit as st
from groq import Groq
from pydantic import BaseModel
from typing import List

# Load employee data from a JSON file
EMPLOYEE_DATA_FILE = r"C:\Users\User\Desktop\employeeData.json"

def load_employee_data():
    with open(EMPLOYEE_DATA_FILE, "r") as file:
        return json.load(file)

# Define Schema for Employee Response
class EmployeeBaseModel(BaseModel):
    name: str
    salary: float
    position: str = None  # Optional for this data
    department: str = None  # Optional for this data

class EmployeeModel(BaseModel):
    employees: List[EmployeeBaseModel]

# Function to get the highest-paid employee
def get_highest_paid_employee():
    data = load_employee_data()
    employees = data.get("employees", [])
    if not employees:
        return None
    return max(employees, key=lambda x: x["SALARY"])

# Extract JSON object from the API response
def extract_json_from_response(response):
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
    return None

# Initialize the GROQ API key
client = Groq(api_key='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')

st.set_page_config(page_title="AI Chatbot - Highest Paid Employee", page_icon="💰")
st.title("💰 AI Chatbot - Find the Highest Paid Employee")
st.write("This chatbot fetches the highest-paid employee and generates a response using Groq LLaMA.")

if st.button("Find Highest Paid Employee"):
    top_employee = get_highest_paid_employee()
    if not top_employee:
        st.error("No employee data found!")
    else:
        # Get the full name of the employee
        employee_name = f"{top_employee['FIRST_NAME']} {top_employee['LAST_NAME']}"
        st.success(f"Highest Paid Employee: {employee_name} - ${top_employee['SALARY']}")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"""You are an HR chatbot. When asked about the highest-paid employee,
                     return JSON output only if it validates against the schema below:
                     {json.dumps(EmployeeModel.model_json_schema(), indent=2)}"""},
                    {"type": "text", "text": f"The highest-paid employee is {employee_name}, earning ${top_employee['SALARY']}, working in the company."}
                ]
            }
        ]

        try:
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
                stream=False,
                stop=None,
                response_format={"type": "json_object"}
            )

            response = completion.choices[0].message.content
            chatbot_response = extract_json_from_response(response)
            st.subheader("Chatbot Response:")
            st.json(chatbot_response)
        except Exception as e:
            st.error(f"Error querying LLaMA: {e}")
