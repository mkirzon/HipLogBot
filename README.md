# Authentication

## Firebase
This authentication is what allows the python code to read/write to Firebase. 

1. Download the json key corresponding to the firebase service account "firebase-adminsdk"
2. Update the path in `.env` for GOOGLE_APPLICATION_CREDENTIALS to point to this file 
2. Update references to the environment variable GOOGLE_APPLICATION_CREDENTIALS (eg in main app files, in test files)

## Cloud Functions
Cloud functions have their own authentication that dictates what tools can _call_ them. In our case, Dialogflow must be able to send POST requests to the Cloud Function webhooks. 
This is managed with IAM principals and roles.

In our case, we had to manually create the appropriate service agent for Dialogflow and then grant it the appropriate permissions. Make sure the project IAM settings have an entry for the account  `service-425447198130@gcp-sa-dialogflow.iam.gserviceaccount.com` with these roles granted - 
1. Cloud Functions Invoker
2. Dialogflow Service Agent


# Architecture & Service Setup

In reverse chronological order from a user interaction, or in essence, we configure this bottom up: 
1. GCP Project
2. A database (i.e. Firestore)
3. A processing server (i.e. serverless Cloud Functions) 
4. A chat bot (Dialogflow)
5. A messenger front end (i.e. Facebook messenger)


## Configuring Firestore db
TODO 

## Configuring Cloud Functions

1. Custom Principals with manual roles 
2. When building the function, allow unauthenticated access 

## Configuring Dialogflow
TODO

# Testing

## Running standard pytests

This is tricky. Our requirements: 
1) The code must remain unchanged, regardless of execution context (main.py locally or on GCP, pytest, VS Debugger)
2) 

Some troubleshooing tips -
* In VSCode, when using the Test Explorer, I suspect that the pytest.ini file isn't loaded when running the workspace shortcut (as oppose to tests folder or individual tests). This is a limitation of the pytest-env plugin I think. 

## Test cloud functions

Assuming all pytests pass locally, do a final "integration" test -

1. Start the functions development server. 
```
functions-framework --target=main --source "/Users/mkirzon/Documents/2023/230901 - Hip Log Bot/hip-log-bot-cloud-function/src/main.py" --debug
```

2. Submit a curl command to it. Replace the url at the end if needed. 
```
curl -X POST -H 'Content-Type: application/json' -d '{"responseId":"924e4b7e-57d3-4dc2-a0dd-1750df534df4-6318e683","queryResult":{"queryText":"i did yoga on 2023-12-31","parameters":{"activity":"Yoga","date":"2023-12-31T12:00:00Z","duration":"","reps":"","weight":""},"allRequiredParamsPresent":true,"fulfillmentMessages":[{"text":{"text":[""]}}],"outputContexts":[{"name":"projects/hip-log-bot/agent/sessions/a6480f9a-41d7-18e7-6f0d-c3ee14c98cfe/contexts/__system_counters__","parameters":{"no-input":0,"no-match":0,"activity":"Yoga","activity.original":"yoga","date":"2023-12-31T12:00:00Z","date.original":"2023-12-31","duration":"","duration.original":"","reps":"","reps.original":"","weight":"","weight.original":""}}],"intent":{"name":"projects/hip-log-bot/agent/intents/3f813326-a34e-4845-875d-5803cf3c3cc2","displayName":"LogActivity"},"intentDetectionConfidence":1,"languageCode":"en"},"originalDetectIntentRequest":{"source":"DIALOGFLOW_CONSOLE","payload":{}},"session":"projects/hip-log-bot/agent/sessions/a6480f9a-41d7-18e7-6f0d-c3ee14c98cfe"}' http://172.17.50.33:8080
```

# Deployment

## Cloud functions

Prereqs:
* Must have gcloud cli installed (and PATH updated to include it)

1. Start the gcloud cli: 
```
gcloud init
```
2. `cd` to the cloud function `src` folder 
3. Deploy with this command - 
```
gcloud functions deploy hip-log-bot-cf \
--gen2 \
--runtime=python311 \
--region=us-central1 \
--source=. \
--entry-point=main \
--trigger-http \
--allow-unauthenticated \
--set-env-vars FIRESTORE_COLLECTION_NAME=activityLogs
```

Notes:
1. Note that if you make a new hip log function (ie provide a new name besides `hip-log-bot-cf`), you'll have to make these changes: 
    i. Manually enter permissions for the service agent principal
    ii. Update the webhook url in Dialogflow
1. We include the env var`FIRESTORE_COLLECTION_NAME` to configure the deployed instance with the database-collection (eg a prod vs test one)



# Development

## Creating new Intents

1. Create and test them within Dialogflow
1. Update `ALLOWED_TYPES` within the `Intent` class
1. Add handling for the new intent in (in this order): 
    * `Intent._extract_log_input()`
    * `main()`
1. Write test cases
