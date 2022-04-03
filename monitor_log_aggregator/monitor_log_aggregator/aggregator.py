from kafka import KafkaConsumer, KafkaProducer
import json
import threading
import time
import pymongo
import logging
from monitor_log_aggregator import kafka_server, module_config, db_instances, db_topics, client

node_ip = module_config["kafka_ip"]
node_port = module_config["kafka_port"]
log_threads = dict()
logging.basicConfig(filename="monitor_log_aggregator.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

def consume_log(topic,node_ip,node_port):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers='{}:{}'.format(node_ip,node_port),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id="consumer-group-a"
        )
        
        print(consumer)
        logging.info("Starting the consumer")
        for msg in consumer:
            # print("Registered User ={}".format(json.loads(msg.value)))
            print(msg.value)
            file_name = topic + ".txt"
            with open(file_name, "a") as f:
                f.write(msg.value.decode('utf-8') + '\n')
            # time.sleep(1)
            # break
    except Exception as e:
        logging.error(e)

def get_instance_data_from_db():
    logging.info("Getting topic names from db")
    # cursor=[{'topic':'logTopic2','ip':'localhost','port':'9092'}]
    cursor = db_topics.topics.find({})
    for item in cursor:
        topic = item['topic_name']
        t = threading.Thread(target=consume_log,args=(topic,node_ip,node_port))
        # t.daemon = True
        log_threads[topic] = t
        t.start()


def new_instance_added(topic):
    logging.info("Creating new consumer for new topic")
    t = threading.Thread(target=consume_log,args=(topic,node_ip,node_port))
    # t.daemon = True
    log_threads[topic] = t
    t.start()

def instance_deleted(topic):
    logging.info("Deleting consumer for deleted topic")
    log_threads[topic].join()
    log_threads.pop(topic)


def db_watcher():
    logging.info("Watcher started")
    resume_token = None
    pipeline = [{'$match': { '$or': [ { 'operationType': 'insert' }, { 'operationType': 'delete' } ] }}]
    change_stream = client.logger.topics.watch(pipeline)
    for change in change_stream:
        if change["operationType"] == "insert":
            print(change["fullDocument"]["topic_name"])
            new_instance_added(change["fullDocument"]["topic_name"])
        else:
            print(change["fullDocument"]["instance_id"])
            instance_deleted(change["fullDocument"]["instance_id"])
        resume_token = change_stream.resume_token

def start():
    logging.info("Log aggregator is running")
    watcher = threading.Thread(target = db_watcher)
    watcher.start()
    get_instance_data_from_db()