# Authentication

For Firebase - 
1. Download the json key to your laptop
2. Update references to the environment variable GOOGLE_APPLICATION_CREDENTIALS (eg in main app files, in test files)


For Cloufunctions - 
1. Use the same service account on your local workstation (i.e. the json key file) as the one you c

# Deploying
First we need to create a zip file containing: main.py, requirements.txt, src/. To do this, create a copy of this project with just those elements. 

1. Create the copy folder
2. Open a new terminal there
3. Run this 
```
zip -r -X hip-log-pkg.zip .
```

* -r stands for recursive, so it gets all files and sub-folders.
* -X excludes those AppleDouble files which ends up getting unzipped by Cloud platforms

2. Upload to Google Cloud Storage bucket 


# Setting up for development

In reverse chronological order from a user interaction, or in essence, we configure this bottom up: 
1. GCP Project
2. A database (i.e. Firestore)
3. A processing server (i.e. serverless Cloud Functions) 
4. A chat bot (Dialogflow)
5. A messenger front end (i.e. Facebook messenger)

## Configuring a Firestore 

## Configuring Serverless Function

1. Custom Principals with manual roles 
2. When building the function, allow unauthenticated access 


## Configuring a Dialogflow


1. 

# Testing

## Test cloud functions

1. Start the functions development server. 
```
functions-framework --target=main --source "/Users/mkirzon/Documents/2023/230901 - Hip Log Bot/hip-log-bot-cloud-function/src/main.py" --debug
```

2. Submit a curl command to it. Replace the url at the end if needed. 
```
curl -X POST -H 'Content-Type: application/json' -d '{"responseId":"924e4b7e-57d3-4dc2-a0dd-1750df534df4-6318e683","queryResult":{"queryText":"i did yoga on 2023-12-31","parameters":{"activity":"Yoga","date":"2023-12-31T12:00:00Z","duration":"","reps":"","weight":""},"allRequiredParamsPresent":true,"fulfillmentMessages":[{"text":{"text":[""]}}],"outputContexts":[{"name":"projects/hip-log-bot/agent/sessions/a6480f9a-41d7-18e7-6f0d-c3ee14c98cfe/contexts/__system_counters__","parameters":{"no-input":0,"no-match":0,"activity":"Yoga","activity.original":"yoga","date":"2023-12-31T12:00:00Z","date.original":"2023-12-31","duration":"","duration.original":"","reps":"","reps.original":"","weight":"","weight.original":""}}],"intent":{"name":"projects/hip-log-bot/agent/intents/3f813326-a34e-4845-875d-5803cf3c3cc2","displayName":"LogActivity"},"intentDetectionConfidence":1,"languageCode":"en"},"originalDetectIntentRequest":{"source":"DIALOGFLOW_CONSOLE","payload":{}},"session":"projects/hip-log-bot/agent/sessions/a6480f9a-41d7-18e7-6f0d-c3ee14c98cfe"}' http://192.168.1.87:8080
```