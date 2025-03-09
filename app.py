import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define a route that handles POST requests
@app.route('/createJira', methods=['POST'])
def createJira():
    # The URL for creating a Jira issue
    url = "https://xxx.atlassian.net/rest/api/3/issue"

    API_TOKEN = ""
    auth = HTTPBasicAuth("", API_TOKEN)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Get the data from the incoming GitHub issue data
    data = request.get_json()

    # Extract necessary information from GitHub data
    github_comment_body = data.get('comment', {}).get('body', '')
    github_action = data.get('action', '')

    # Check if the action is 'created' and the comment contains '/jira'
    if github_action == 'created' and '/jira' in github_comment_body.lower():
        # Extract the title and body from the GitHub issue
        github_title = data.get('issue', {}).get('title', 'Default GitHub Issue Title')
        github_body = data.get('issue', {}).get('body', 'Default GitHub Issue Description')

        # Prepare the payload dynamically
        payload = json.dumps({
            "fields": {
                "description": {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": github_body,
                                    "type": "text"
                                }
                            ],
                            "type": "paragraph"
                        }
                    ],
                    "type": "doc",
                    "version": 1
                },
                "project": {
                    "key": "TDH"
                },
                "issuetype": {
                    "id": "10016"
                },
                "summary": github_title,
            },
            "update": {}
        })

        # Make the POST request to create the issue in Jira
        response = requests.post(url, data=payload, headers=headers, auth=auth)

        # Log the response from Jira and return it
        if response.status_code == 201:
            return jsonify({"message": "Jira issue created successfully", "jira_issue": response.json()}), 201
        else:
            return jsonify({"message": "Failed to create Jira issue", "error": response.json()}), 400
    else:
        # Return a message if the condition is not met (i.e., comment doesn't contain '/jira' or action isn't 'created')
        return jsonify({"message": "No action taken. Either comment didn't contain '/jira' or action wasn't 'created'."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



