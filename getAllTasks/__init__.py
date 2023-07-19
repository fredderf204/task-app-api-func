import logging
import os
import pymongo
from bson import json_util
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Set up connection information for Cosmos DB
    host = os.environ["host"]
    username = os.environ["dbusername"]
    password = os.environ["dbpassword"]
    database_name = os.environ["database_name"]
    collection_name = os.environ["collection_name"]

    uri = f"mongodb://{username}:{password}@{host}:10255/?ssl=true&retrywrites=false&maxIdleTimeMS=120000&appName=@{username}@"
    client = pymongo.MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    # Get all documents from the collection
    try:
        documents = collection.find()
    
        # Return the documents as a JSON array to the client
        return func.HttpResponse(
            body=json_util.dumps(documents),
            mimetype='application/json'
        )

    # If there is an error, return a 500 error to the client    
    except Exception as e:
        error_message_api = {"error": "Error finding tasks"}
        error_message_log = {"error": str(e)}
        logging.info(json_util.dumps(error_message_log))

    return func.HttpResponse(f"{error_message_api}", status_code=500, mimetype='application/json')
