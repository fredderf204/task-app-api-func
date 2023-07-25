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

    # Decode form data
    body_unicode = req.get_body().decode('utf-8')
    from urllib.parse import parse_qs
    req_bodyd = parse_qs(body_unicode)

    # Get details from from data
    description = str(req_bodyd['description'])
    duedate = str(req_bodyd['duedate'])
    title = str(req_bodyd['title'])

    # Sense check
    if title is None:
        return func.HttpResponse(
             "Title missing",
             status_code=400
        )

    if duedate is None:
        duedaten = ""
    else:
        duedaten = str(duedate)

    # Create a new document
    document = {
        "id": collection.count_documents({}) + 1,
        "completed": False,
        "description": description,
        "duedate": duedaten,
        "title": title
    }

    # Insert document into the collection
    try:
        documents = collection.insert_one(document)
    
        # Return the documents as a JSON array to the client
        return func.HttpResponse(
            body='task added',
            mimetype='application/json'
        )

    # If there is an error, return a 500 error to the client    
    except Exception as e:
        error_message_api = {'error:' 'adding task failed'}
        error_message_log = {"error": str(e)}
        logging.info(json_util.dumps(error_message_log))

        return func.HttpResponse(f"{error_message_api}", status_code=500, mimetype='application/json')