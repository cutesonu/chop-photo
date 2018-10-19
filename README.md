# chop-photo

## Before Starting 
The python script for chop cutting of image. and deploying on Google App Engine.
Please check [Google App Engine Document](https://cloud.google.com/appengine/docs/standard/python/quickstart) the guide with Python27 environment.

1. install the Google Cloud SDK on the local which will be needed to deploy the new version to the app. 

2. Download the project
    
    git clone https://github.com/sonudesk/chop-photo.git

3. Install the dependencies
    
    Move to the project directory 
    
        pip install -r requirements.txt -t /lib

4. Deploy the App
    
        gcloud app deploy
       
    Then the new version script will be deployed on Cloud and then new service will run.  
    In addition to app engine, it is possible to manage the running services on AppEngine page of Google Cloud Console
