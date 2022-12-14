import math
import boto3
import time
import json
from boto3.dynamodb.conditions import Key, Attr
import datetime
from botocore.exceptions import ClientError


REGION="us-east-1"
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table('AirQualityData')
table_output = dynamodb.Table('AirQualityDataOutput')

#https://www.acurite.com/blog/soil-moisture-guide-for-plants-and-vegetables.html
#using this site for categories
CATEGORIES={'very dry': (0, 20), 'dry': (21,40), 'moist':(41,60), 'wet':(61,80), 'very dry to dry':(0,40), 'dry to moist':(21,60), 'moist to wet':(41,80), 'dry to wet':(21,80)}
VERY_DRY = []
DRY = ['lavendar', 'lemon balm', 'rose', 'gardenia']
MOIST =['aster', 'big blue stem', 'lupine', 'blueberry', 'juniper']
WET = ['asilbe', 'bleeding heart', 'marsh marigold', 'cranberry']
VERY_DRY_TO_DRY = ['agave', 'cactus']
DRY_TO_MOIST = ['daffodil', 'daylilly', 'lily', 'peony', 'apple', 'peach', 'strawberry']
MOIST_TO_WET = ['meadow rue', 'willow', 'dogwood']
DRY_TO_WET = ['sedges', 'elderberry']

# BREAKPOINTS={}

# BREAKPOINTS['pm10']=[{'data': (0,54),    'aqi': (0,50)}, 
#                      {'data': (55,154),  'aqi': (51,100)}, 
#                      {'data': (155,254), 'aqi': (101,150)}, 
#                      {'data': (255,354), 'aqi': (151, 200)}, 
#                      {'data': (355,424), 'aqi': (201,300)}, 
#                      {'data': (425,504), 'aqi': (301,400)}, 
#                      {'data': (505,604), 'aqi': (401,500)}]

# BREAKPOINTS['pm2_5']=[{'data': (0,15.4),     'aqi': (0,50)}, 
#                      {'data': (15.5,40.4),   'aqi': (51,100)}, 
#                      {'data': (40.5,65.4),   'aqi': (101,150)}, 
#                      {'data': (65.5,150.4),  'aqi': (151, 200)}, 
#                      {'data': (150.5,250.4), 'aqi': (201,300)}, 
#                      {'data': (250.5,350.4), 'aqi': (301,400)}, 
#                      {'data': (350.5,500.4), 'aqi': (401,500)}]

# BREAKPOINTS['co']=  [{'data': (0.0,4.4),    'aqi': (0,50)}, 
#                      {'data': (4.5,9.4),  'aqi': (51,100)}, 
#                      {'data': (9.5,12.4), 'aqi': (101,150)}, 
#                      {'data': (12.5,15.4), 'aqi': (151, 200)}, 
#                      {'data': (15.5,30.4), 'aqi': (201,300)}, 
#                      {'data': (30.5,40.4), 'aqi': (301,400)}, 
#                      {'data': (40.5,50.4), 'aqi': (401,500)}]

# BREAKPOINTS['so2']=[{'data': (0.000,0.034),    'aqi': (0,50)}, 
#                      {'data': (0.035,0.144),  'aqi': (51,100)}, 
#                      {'data': (0.145,0.224), 'aqi': (101,150)}, 
#                      {'data': (0.225,0.304), 'aqi': (151, 200)}, 
#                      {'data': (0.305,0.604), 'aqi': (201,300)}, 
#                      {'data': (0.605,0.804), 'aqi': (301,400)}, 
#                      {'data': (0.805,1.004), 'aqi': (401,500)}]


def lambda_handler(event, context):
    
    now=int(time.time())
    timestampold=now-86400
    PLANTS = ['plant0', 'plant1', 'plant2', 'plant3', 'plant4'] 
    #for plant in plants? check moisture and notify user which plants too low moisture?
    stationID='ST102'
    DATAKEYS=["pm2_5", "pm10", "co", "so2"]
    AQI=[]
    
    response = table.scan(
               FilterExpression=Key('stationID').eq(stationID) & Attr('timestamp').gt(timestampold)
        )
    items = response['Items']
    
    AQI_output_json={}
    AQI_output_json["stationID"]=stationID
    AQI_output_json["timestamp"]=now
    
    for key in DATAKEYS:
        readings=[]    
        for item in items:
            readings.append(float(item['data'][key]))
    
        readings_avg = sum(readings)/len(readings)
        C_p=readings_avg
        for i in range(0,len(BREAKPOINTS[key])):
            BP_Lo = BREAKPOINTS[key][i]['data'][0]
            BP_Hi = BREAKPOINTS[key][i]['data'][1]
            I_Lo = BREAKPOINTS[key][i]['aqi'][0]
            I_Hi = BREAKPOINTS[key][i]['aqi'][1]
            if C_p>=BP_Lo and C_p<BP_Hi:
                I_p = (I_Hi-I_Lo)*(C_p-BP_Lo)/(BP_Hi-BP_Lo)+I_Lo
                result = int(math.ceil(I_p))
                AQI_output_json[key]=result
                AQI_output_json["latitude"]=item['data']["latitude"]
                AQI_output_json["longitude"]=item['data']["longitude"]
                AQI.append((key, result))
                break
    
    
    
    AQI_sorted = sorted(AQI, key=lambda x: x[-1],reverse=True)
    AQI_final = AQI_sorted[0][1]
    main_pollutant = AQI_sorted[0][0]
    AQI_output_json["aqi"]=AQI_final
    AQI_output_json["main_pollutant"]=main_pollutant
    
    table_output.put_item(
            Item=AQI_output_json
            )
    outputstring = "For station "+stationID+", at time "+str(now)+", AQI is "+str(AQI_final)+" and main pollutant is "+str(main_pollutant)
    if AQI_final > 100:
        try:
            ses = boto3.client('ses', region_name=REGION)
            reponse = ses.send_email(
                Source='ipoage30@gatech.edu',
                Destination={'ToAddresses': ['bella.poage@gmail.com']},
                Message={
                    'Subject': {'Data': 'Dangerous Air Quality Levels'},
                    'Body': {
                        'Text': {'Data': outputstring}
                    }
                }
            )

        except ClientError as e:
            print(e.response['Error']['Message'])
    
            return False
        else:
            print("Email sent! Message ID:"),
            #print(response['MessageId'])
    return {
        "statusCode": 200,
        "body": outputstring
    }