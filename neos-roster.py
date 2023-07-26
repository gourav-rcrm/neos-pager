import subprocess
import json
import http.client
from tabulate import tabulate
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os

# Load environment variables from .env file into os.environ
load_dotenv()

# Now you can access the environment variables using os.environ.get()
API_TOKEN_TEMP = os.environ.get('API_TOKEN_TEMP')

init()
Fore.RESET = Style.RESET_ALL
Fore.YELLOW = Fore.LIGHTYELLOW_EX

def get_user_ids():
    # Run the command and capture the output
    output = subprocess.check_output("pd user list --output=json", shell=True)
    # Convert the output to a Python list
    data = json.loads(output)

    # Create a 2D list with the required fields
    result_list = [[user["id"], user["summary"], user["email"]] for user in data]
    return result_list

def get_notification_rule_id(ans):
    users=get_user_ids()
    # Run the command and capture the output
    output = subprocess.check_output(f"pd rest get -e /users/{ans}/notification_rules", shell=True)
    # Convert the output to a Python dictionary
    data = json.loads(output)
    # Convert the JSON data to Python dictionary
    data_dict = data

    # Filter out the notification rules and contact methods with type 'email_contact_method'
    filtered_data = [
        {
            "Notification Rule ID": rule["id"],
            "Contact Method ID": rule["contact_method"]["id"],
            "Label": rule["contact_method"]["label"],
            "Address": rule["contact_method"]["address"]
        }
        for rule in data_dict["notification_rules"]
        if rule["contact_method"]["type"] == "phone_contact_method"
    ]

    # Get all the "id" fields from the "notification_rules" list
    all_ids = [rule['id'] for rule in data['notification_rules']]
    # Print all the IDs
    return [tabulate(filtered_data, headers="keys", tablefmt="grid"),all_ids]
def present(ans,users):
    for user in users:
        if user[0]==ans:
            return True
    return False
def delete_user_notification_rule():
    conn = http.client.HTTPSConnection("api.pagerduty.com")
    users=get_user_ids()
    print(Fore.YELLOW + "\nUser ID's \n",tabulate(users))
    print(Style.RESET_ALL)
    ans=input("\nCopy and paste the UserID whose notification rule you want to delete! ")
    if present(ans,users):
        all_ids=get_notification_rule_id(ans)
        print(Fore.YELLOW + "\nNotification Rule ID's \n",all_ids[0])
        print(Style.RESET_ALL)
        flag=True
        while len(all_ids[1])>0 and flag:
            index=input(Fore.RED + "\nCopy and paste the notification rule ID you want to delete! ")
            print(Style.RESET_ALL)
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/vnd.pagerduty+json;version=2",
                'Authorization': f"Token token={API_TOKEN_TEMP}"
                }

            conn.request("DELETE", f"/users/{ans}/notification_rules/{index}", headers=headers)

            res = conn.getresponse()
            data = res.read()
            print(data.decode("utf-8"))

            all_ids=get_notification_rule_id(ans)
            print(Fore.YELLOW + "\nNotification Rule ID's \n",all_ids[0])
            print(Style.RESET_ALL)
            more=input(Fore.RED + "\nDo you want to delete another notification rule? (Y/N) ")
            print(Style.RESET_ALL)
            if more=="N":
                flag=False
                exit()
        else:
            print("\nNo notification rules found for this user!\n")
    else:
        print(Fore.RED + "\nYou have not chosen a valid user ID\nThank you for using RecruitCRM Pagerduty CLI!")
        print(Style.RESET_ALL)

def create_user_notification_rule():
    users=get_user_ids()
    print("\nUser ID's \n",tabulate(users))
    ans=input(Fore.RED +"\nCopy and paste the UserID whose notification rule you want to create! ")
    print(Style.RESET_ALL)

    if present(ans,users):
        # Run the command and capture the output
        output = subprocess.check_output(f"pd rest get -e /users/{ans}/contact_methods -P type=phone_contact_method", shell=True)
        # Convert the output to a Python dictionary
        data = json.loads(output)
        # Get all the "id" fields from the "contact_methods" list
        all_ids = [[rule['id'],rule['label'],rule['address']] for rule in data['contact_methods']]
        # Print all the IDs
        print(all_ids)
        inp=input(Fore.RED +"\nCopy and paste the contact method ID you want to create! ")
        print(Style.RESET_ALL)
        conn = http.client.HTTPSConnection("api.pagerduty.com")

        payload = """{
        "notification_rule": {
            "type": "assignment_notification_rule",
            "start_delay_in_minutes": 0,
            "contact_method": {
            "id": "%s",
            "type": "phone_contact_method"
            },
            "urgency": "high"
        }
        }""" % inp

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/vnd.pagerduty+json;version=2",
            'Authorization': f"Token token={API_TOKEN_TEMP}"
            }

        conn.request("POST", f"/users/{ans}/notification_rules", payload, headers)

        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"),"Created ✅")

print(Fore.GREEN + "\nHello welcome Neo!")
ans=input("\nDo you want to delete(1) or create(2) a notification rule? (1/2) ")
if ans=="1":
    user_input=input("\nDo you really want to delete the notification rules of someone? (Y/N) ")
    if user_input=="Y":
        delete_user_notification_rule()
    else:
        print("\nYou have not chosen (Y/N), Thank you for using RecruitCRM Pagerduty CLI! ")
elif ans=="2":
    user_input=input("\nDo you really want to create a notification rules of someone? (Y/N) ")
    if user_input=="Y":
        create_user_notification_rule()
    else:
        print("\nYou have not chosen (Y/N), Thank you for using RecruitCRM Pagerduty CLI! ")
else:
    print("\nYou have not chosen (1/2)\nThank you for using RecruitCRM Pagerduty CLI! ")
print(Style.RESET_ALL)