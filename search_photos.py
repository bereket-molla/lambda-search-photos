import boto3
import json
from opensearchpy import OpenSearch

def lambda_handler(event, context):
    # initialize Amazon Lex V2 client
    lex_client = boto3.client('lexv2-runtime')
    
    # get search query from API gateway GET method
    print(event)
    search_query = event['queryStringParameters']['q']
    
    # disambiguate query using Amazon Lex V2 bot
    response = lex_client.recognize_text(
        botId='66I0XJ9E2N',
        botAliasId='SHJNUTQJXN',
        localeId='en_US',
        sessionId='test',
        text=search_query
    )
    
    # initialize search query body
    search_body = {
        "query": {
            "bool": {
                "should": []
            }
        }
    }
    
    # check if the Lex response has any keywords
    if 'interpretations' in response:
        for interpretation in response['interpretations']:
            # check if keywordOne or keywordTwo is present
            if "keywordOne" in interpretation["intent"]["slots"]:
                if interpretation["intent"]["slots"]["keywordOne"]:
                    key1 = interpretation["intent"]["slots"]["keywordOne"]["value"]["interpretedValue"]
                    # add keywordOne to search query
                    search_body["query"]["bool"]["should"].append({"terms": {"labels": [key1]}})
                
            if "keywordTwo" in interpretation["intent"]["slots"]:
                if interpretation["intent"]["slots"]["keywordTwo"]:
                    key2 = interpretation["intent"]["slots"]["keywordTwo"]["value"]["interpretedValue"]
                    # add keywordTwo to search query
                    search_body["query"]["bool"]["should"].append({"terms": {"labels": [key2]}})
        
        print(search_body)
        # initialize OpenSearch client
        client = OpenSearch(
            "https://search-photos-hucjac425ni3nynyrweghwfwo4.us-east-1.es.amazonaws.com",
            http_auth=("photos", "Ironmansucks.1")
        )
        
        # search OpenSearch using search query body
        response = client.search(
            index="photos",
            body=search_body
        )
        
        print("Here is what I got", response)
        # extract search results
        hits = response["hits"]["hits"]
        results = []
        for hit in hits:
            results.append(hit["_source"])
        
        
        # return search results
        response =  {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps({'results': results})}

     
        
    else:
        # return empty array of results
        response =  {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
            },
            'body': json.dumps({'results': []})}
     
    return response
