import requests
import json
import pandas as pd
import re
from getpass import getpass
from datetime import datetime

# Set the Splunk API endpoint url and login url
splunk_api_url = "https://127.0.0.1:8089/services/search/jobs/export"
splunk_login_url =  "https://127.0.0.1:8089/services/auth/login"

def main():
    print("This script automatically searches your queries in Splunk Enterprise\n")

    # Get the login header
    header = auth()

    # Take query input and create a query using search commanda
    search = str(input("Enter your search query:"))
    search_command = "search "
    search_query = f"{search_command}{search}"

    search_params = {
        "search": search_query,
        "output_mode": "json"
    }
    searchsplunk(search_params, header)

    # Continue the code if user wants to do more searches
    while True:
        choice = input("Do you want to do another search?(y/n)")
        if choice == "y":
            search = str(input("Enter your search query:"))
            search_command = "search "
            search_query = f"{search_command}{search}"
            search_params = {
                "search": search_query,
                "output_mode": "json"
            }
            searchsplunk(search_params, header)
        elif choice == "n":
            exit()
        else:
            print("Invalid choice. Please enter y or n.")

def auth():
    while True:
        try:
            # Get the username and password from user
            username = input("Enter your username: ")
            password = getpass("Enter your password: ")
            
            # Make an API request to get a session key
            response = requests.post(splunk_login_url, data={"username": username, "password": password}, verify=False)

            # Extract the session key from the response content
            session_key = response.content.decode()

            # Use regex to get the sessionkey from response. It is between <sessionKey> and </sessionKey>.
            match_key = re.findall(r'<sessionKey>(.*?)<\/sessionKey>', session_key)

            # Since the match_key is a list, extract it as str using following line
            match_keystr = str(match_key[0])

            # Set the session key as a header in the search API request
            headers = {"Authorization": f"Splunk {match_keystr}"}
            return(headers) # Return header for searching
        except:
            print("Not authenticated!")
    
def searchsplunk(search_params, header):
    try:
        # Make the API request to run the search and retrieve the results
        response = requests.get(splunk_api_url, params=search_params, headers=header, verify=False)

        # Split the response content by newlines and parse each line as a separate JSON object
        search_results = [json.loads(line) for line in response.content.decode().split('\n') if line.strip()]

        # Format the JSON data with indentation
        formatted_results = json.dumps(search_results, indent=2)

        # Print the results
        print(formatted_results)

        #Normalize the json
        df = pd.json_normalize(search_results)
       
        # Write the json into excel using pandas, format its name as date and time
        current_date_time = datetime.now()
        formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")
        df.to_excel(formatted_date_time+"-splunk-search-results.xlsx", index=False)

        print("Export to Excel file successful.")

    except json.decoder.JSONDecodeError:
        print("Error: Response content is not in valid JSON format.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
