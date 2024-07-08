from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes.association import router as AssociationRouter
from app.models.association import PACSqueryCore
from app.controllers.association import get_analyses
import os
import requests
import json
import asyncio
from aiokafka import AIOKafkaConsumer
running = True
description = """
A simple FastAPI `consumer` application that constantly polls a 
`kafka` broker for messages containing DICOM tags. This application
can deserialize messages, get/set DICOM association rules, and 
finally request `pfbridge` to create a workflow.
"""

## pfdcm
app = FastAPI(
    title='consumer',
    version='0.0.1',
    contact={"name": "FNNDSC", "email": "dev@babymri.org"},
    openapi_tags=[],
    description=description
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)
loop = asyncio.get_event_loop()

async def consume():
    consumer = None
    try:
        consumer = AIOKafkaConsumer("test", bootstrap_servers=f"{os.getenv('KAFKA_URL')},{os.getenv('KAFKA_URL')}",
                                loop=loop)
    except Exception as ex:
        print(f"{ex}. Retrying in 10 seconds")
        sleep(10)
        consumer = AIOKafkaConsumer("test", bootstrap_servers=f"{os.getenv('KAFKA_URL')},{os.getenv('KAFKA_URL')}",
                                    loop=loop)

    await consumer.start()
    try:
        async for msg in consumer:
            print(
                "consumed: ",
                msg.topic,
                msg.partition,
                msg.offset,
                msg.key,
                msg.value,
                msg.timestamp,
            )
            if "Connection established" in str(msg.value):
                continue
            dict_str = msg.value.decode("UTF-8")
            dict_str = dict_str.replace('"', '')
            dict_str = dict_str.replace("'", '"')
            d_tag = json.loads(dict_str)
            query = PACSqueryCore(
                Modality=d_tag["Modality"],
                StudyDescription=d_tag['StudyDescription']
            )
            analyses = get_analyses(query)
            for analysis in analyses:
                request_workflow(d_tag['SeriesInstanceUID'], d_tag['StudyInstanceUID'], analysis)
    except Exception as ex:
        print(f"Error occured:{ex}")
    finally:
        await consumer.stop()

def request_workflow(srs_id, std_id, analysis):
    pfbridge_url = f'{os.getenv("PFBRIDGE_URL")}/analyze/?test=false'
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    try:
        response =  requests.post(
                pfbridge_url,
                json={'imageMeta': { "StudyInstanceUID": std_id,
                                     "SeriesInstanceUID": srs_id},
                      "analyzeFunction": analysis},
        headers = headers)

    except Exception as e:
        print(str(e))


@app.on_event("startup")
async def startup_event():
        loop.create_task(consume())



@app.on_event("shutdown")
async def shutdown_event():
    consumer = AIOKafkaConsumer("test", bootstrap_servers=f"{os.getenv('KAFKA_URL')},{os.getenv('KAFKA_URL')}",
                                loop=loop)
    await consumer.stop()

app.include_router(AssociationRouter, prefix="/api/v1")