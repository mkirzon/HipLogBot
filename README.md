Documentation available on [Notion](https://www.notion.so/Tech-Spec-28c90edaa7234444bc9d728f9c13342e)

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

