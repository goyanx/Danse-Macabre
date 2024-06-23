__version__ = "1.0.0"

import requests
import json
import traceback

# Define the completion function that takes messages and an API key as input
def completion(messages, api_key="", proxy=''):
    # Set the API endpoint URL for ChatGPT completions
    url = "http://localhost:11434/v1/chat/completions"

    # If a proxy is set, then it should use that instead
    #if proxy is not None and proxy != '':
    #    url = proxy

    # Set the headers for the API request, including the Content-Type and Authorization with the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Set the data for the API request, including the model and the input messages
    data = {
        "model": "phi3:3.8b-mini-128k-instruct-q4_K_M",
        "messages": messages,
        "stream": False
    }

    # Send the API request using the POST method, passing the headers and the data as JSON
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the response status code is 200 (successful)
    if response.status_code == 200:
        try:
            # Extract the message from the response JSON and append it to the messages list
            completion = response.json()["choices"][0]["message"]
            messages.append(completion)
            return messages  # Return the updated messages list
        except json.JSONDecodeError as e:
            # If there is a JSON decoding error, print the raw response for debugging
            print("JSON decode error:", e)
            print("Response content:", response.content)
            raise Exception(f"Error: {response.status_code}, {response.text}")
        except KeyError as e:
            # If there is a KeyError, print the full response for debugging
            print("Key error:", e)
            print("Response JSON structure:", response.content)
            raise Exception(f"Error: {response.status_code}, {response.text}")
    else:
        # If the status code is not 200, raise an exception with the error details
        raise Exception(f"Error: {response.status_code}, {response.text}")
