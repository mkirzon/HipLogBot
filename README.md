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