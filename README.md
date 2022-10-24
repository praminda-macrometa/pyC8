# PyC8

![PyPI](https://img.shields.io/pypi/v/pyC8)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyc8)
![PyPI - Format](https://img.shields.io/pypi/format/pyc8)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/pyc8)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyc8)

Python SDK for the Macrometa Global Data Network.

---

## Supported Python Versions
This SDK supports the following Python implementations:

* Python 3.4 - 3.10

## Installation

Install from PyPi using [pip](https://pip.pypa.io/en/latest/), a
package manager for Python.

```commandline
pip install pyC8
```

## Development environment
To enable developer environment position ourselves to project's root and run:

```bash
pip install -r requirements/dev.txt
```

## Testing

End-to-end tests can be found in tests/.
Before first run create .env file in tests/.
In `.env` file add variables:

* `FEDERATION_URL="<your federation url>"`
* `FABRIC="<selected fabric>"`
* `TENANT_EMAIL="<your tenant email>"`
* `TENANT_PASSWORD="<your tenant password>"`
* `API_KEY="<your api key>"`
* `TOKEN="<your token>"`
* `MM_TENANT_EMAIL="<Macrometa tenant email>"`
* `MM_TENANT_PASSWORD="<Macrometa tenant password>"`
* `MM_API_KEY="<Macrometa apy key>"`

**Note: MM_TENANT_EMAIL, MM_TENANT_PASSWORD, MM_API_KEY are super user credentials**

`.env` file is in `.gitignore`.

To run tests position yourself in the project's root while your virtual environment
is active and run:
```bash
python -m pytest
```

## Enable pre-commit hooks

You will need to install pre-commit hooks
Using homebrew:
```bash
brew install pre-commit
```
Using conda (via conda-forge):
```bash
conda install -c conda-forge pre-commit
```
To check installation run:
```bash
pre-commit --version
```
If installation was successful you will see version number.
You can find the Pre-commit configuration in `.pre-commit-config.yaml`.
Install the git hook scripts:
```bash
pre-commit install
```
Run against all files:
```bash
pre-commit run --all-files
```
If setup was successful pre-commit will run on every commit.
Every time you clone a project that uses pre-commit, running `pre-commit install`
should be the first thing you do.

## Build

To build package we need to position ourselves to project's root and run:

```bash
 $ python setup.py build
```

## Upgrade
```bash
pip install --upgrade pyc8
```

---

# Getting Started

The SDK allows you to use three ways for authentication:

1. Using the email and password

```python

  # Authentication email and password
  client = C8Client(protocol='https', host='gdn1.macrometa.io', port=443,
   email="user@example.com", password="XXXXX")
```

2. Using bearer token

```python

# Authentication with bearer token
client = C8Client(protocol='https', host='gdn1.macrometa.io', port=443,
 token=<your token>)

```


3. Using API key

```python

# Authentication with API key

client = C8Client(protocol='https', host='gdn1.macrometa.io', port=443,
 apikey=<your api key>)
```
## Usage:

```python

from c8 import C8Client
import time
import warnings

warnings.filterwarnings("ignore")
federation = "gdn.paas.macrometa.io"
demo_tenant = "mytenant@example.com"
demo_fabric = "_system"
demo_user = "user@example.com"
demo_user_name = "root"
demo_stream = "demostream"
collname = "employees"
# --------------------------------------------------------------
print("Create C8Client Connection...")
client = C8Client(protocol='https', host=federation, port=443,
                  email=demo_tenant, password='XXXXX',
                  geofabric=demo_fabric)

# --------------------------------------------------------------
print("Create Collection and insert documents")

if client.has_collection(collname):
    print("Collection exists")
else:
    client.create_collection(name=collname)

# List all Collections
coll_list = client.get_collections()
print(coll_list)

# Filter collection based on collection models DOC/KV/DYNAMO
colls = client.get_collections(collection_model='DOC')
print(colls)

# Get Collecion Handle and Insert
coll = client.get_collection(collname)
coll.insert(
    {'firstname': 'John', 'lastname': 'Berley', 'email': 'john.berley@macrometa.io'})

# insert document
client.insert_document(collection_name=collname,
                       document={'firstname': 'Jean', 'lastname': 'Picard',
                                 'email': 'jean.picard@macrometa.io'})
doc = client.get_document(collname, "John")
print(doc)

# insert multiple documents
docs = [
    {'firstname': 'James', 'lastname': 'Kirk', 'email': 'james.kirk@macrometa.io'},
    {'firstname': 'Han', 'lastname': 'Solo', 'email': 'han.solo@macrometa.io'},
    {'firstname': 'Bruce', 'lastname': 'Wayne', 'email': 'bruce.wayne@macrometa.io'}
]

client.insert_document(collection_name=collname, document=docs)

# insert documents from file
client.insert_document_from_file(collection_name=collname,
                                 csv_filepath="/home/user/test.csv")

# Add a hash Index
client.add_hash_index(collname, fields=['email'], unique=True)

# --------------------------------------------------------------

# Query a collection
print("query employees collection...")
query = 'FOR employee IN employees RETURN employee'
cursor = client.execute_query(query)
docs = [document for document in cursor]
print(docs)

# --------------------------------------------------------------
print("Delete Collection...")
# Delete Collection
client.delete_collection(name=collname)

```

Example for **real-time updates** from a collection in fabric:

```python

  from c8 import C8Client
  import time
  import warnings
  warnings.filterwarnings("ignore")
  federation = "gdn.paas.macrometa.io"
  demo_tenant = "mytenant@example.com"
  demo_fabric = "_system"
  demo_user = "user@example.com"
  demo_user_name = "root"
  demo_stream = "demostream"
  collname = "democollection"
  #--------------------------------------------------------------
  print("Create C8Client Connection...")
  client = C8Client(protocol='https', host=federation, port=443,
                       email=demo_tenant, password='XXXXX',
                       geofabric=demo_fabric)

  #--------------------------------------------------------------
  def callback_fn(event):
       print(event)
   #--------------------------------------------------------------
  client.on_change("employees", timeout=10, callback=callback_fn)


```

Example to **publish** documents to a stream:

```python

  from c8 import C8Client
  import time
  import base64
  import six
  import json
  import warnings
  warnings.filterwarnings("ignore")

  federation = "gdn.paas.macrometa.io"
  demo_tenant = "mytenant@example.com"
  demo_fabric = "_system"
  stream = "demostream"
  #--------------------------------------------------------------
  print("publish messages to stream...")
  client = C8Client(protocol='https', host=federation, port=443,
                       email=demo_tenant, password='XXXXX',
                       geofabric=demo_fabric)

  producer = client.create_stream_producer(stream)

  for i in range(10):
      msg1 = "Persistent: Hello from " + "("+ str(i) +")"
      producer.send(json.dumps(msg1))
      time.sleep(10) # 10 sec

```

Example to **subscribe** documents from a stream:

```python

  from c8 import C8Client
  import time
  import base64
  import six
  import json
  import warnings
  warnings.filterwarnings("ignore")

  federation = "gdn.paas.macrometa.io"
  demo_tenant = "mytenant@example.com"
  demo_fabric = "_system"
  stream = "demostream"
  #--------------------------------------------------------------
  print("publish messages to stream...")
  client = C8Client(protocol='https', host=federation, port=443,
                       email=demo_tenant, password='XXXXX',
                       geofabric=demo_fabric)


  subscriber = client.subscribe(stream=stream, local=False, subscription_name="test-subscription-1")
  for i in range(10):
      print("In ",i)
      m1 = json.loads(subscriber.recv())  #Listen on stream for any receiving msg's
      msg1 = base64.b64decode(m1["payload"])
      print("Received message '{}' id='{}'".format(msg1, m1["messageId"])) #Print the received msg over   stream
      subscriber.send(json.dumps({'messageId': m1['messageId']}))#Acknowledge the received msg.

  print(client.get_stream_subscriptions(stream=stream, local=False))

  print(client.get_stream_backlog(stream=stream, local=False))

```

Example: **stream management**:

```python
  from c8 import C8Client
  import time
  import warnings
  warnings.filterwarnings("ignore")

  federation = "gdn.paas.macrometa.io"
  demo_tenant = "mytenant@example.com"
  demo_fabric = "_system"
  stream = "demostream"
  #--------------------------------------------------------------
  print("publish messages to stream...")
  client = C8Client(protocol='https', host=federation, port=443,
                       email=demo_tenant, password='XXXXX',
                       geofabric=demo_fabric)

  #get_stream_stats
  print("Stream Stats: ", client.get_stream_stats(stream))

  print(client.get_stream_subscriptions(stream=stream, local=False))

  print(client.get_stream_backlog(stream=stream, local=False))

  #print(client.clear_stream_backlog(subscription="test-subscription-1"))
  print(client.clear_streams_backlog())

```

Advanced operations can be done using the `sream_colleciton` class.

```python

   from c8 import C8Client
   import warnings
   warnings.filterwarnings("ignore")

   federation = "gdn.paas.macrometa.io"
   demo_tenant = "mytenant@example.com"
   demo_fabric = "_system"

   #--------------------------------------------------------------
   print("consume messages from stream...")
   client = C8Client(protocol='https', host=federation, port=443)
   demotenant = client.tenant(email=demo_tenant, password='XXXXX')
   fabric = demotenant.useFabric(demo_fabric)
   stream = fabric.stream()

   #Skip all messages on a stream subscription
   stream_collection.skip_all_messages_for_subscription('demostream', 'demosub')

   #Skip num messages on a topic subscription
   stream_collection.skip_messages_for_subscription('demostream', 'demosub', 10)
   #Expire messages for a given subscription of a stream.
   #expire time is in seconds
   stream_collection.expire_messages_for_subscription('demostream', 'demosub', 2)
   #Expire messages on all subscriptions of stream
   stream_collection.expire_messages_for_subscriptions('demostream',2)
   #Reset subscription to message position to closest timestamp
   #time is in milli-seconds
   stream_collection.reset_message_subscription_by_timestamp('demostream','demosub', 5)
   #Reset subscription to message position closest to given position
   #stream_collection.reset_message_for_subscription('demostream', 'demosub')
   #stream_collection.reset_message_subscription_by_position('demostream','demosub', 4)
   #Unsubscribes the given subscription on all streams on a stream fabric
   stream_collection.unsubscribe('demosub')
   #delete subscription of a stream
   #stream_collection.delete_stream_subscription('demostream', 'demosub' , local=False)
```

Example for **restql** operations:

``` python
  from c8 import C8Client
  import json
  import warnings
  warnings.filterwarnings("ignore")
  region = "gdn1.macrometa.io"
  demo_tenant = "mytenant@example.com"
  demo_fabric = "_system"

  #--------------------------------------------------------------
  client = C8Client(protocol='https', host=region, port=443,
                       email=demo_tenant, password='hidden',
                       geofabric=demo_fabric)

  #--------------------------------------------------------------
  print("save restql...")
  data = {
    "query": {
      "parameter": {},
      "name": "demo",
      "value": "FOR employee IN employees RETURN employee"
    }
  }
  response = client.create_restql(data)
  #--------------------------------------------------------------
  print("execute restql without bindVars...")
  response = client.execute_restql("demo")
  print("Execute: ", response)
  #--------------------------------------------------------------
  # Update restql
  data = {
        "query": {
            "parameter": {},
            "value": "FOR employee IN employees Filter doc.firstname=@name RETURN employee"
        }
    }
  response = client.update_restql("demo", data)

  #--------------------------------------------------------------

  print("execute restql with bindVars...")
  response = fabric.execute_restql("demo",
                                   {"bindVars": {"name": "Bruce"}})
  #--------------------------------------------------------------
  print("get all restql...")
  response = fabric.get_all_restql()
  #--------------------------------------------------------------

  print("delete restql...")
  response = fabric.delete_restql("demo")
```

Workflow of **Spot Collections**

spot collections can be assigned or updated using the `tenant` class.

```python

from c8 import C8Client

# Initialize the client for C8DB.
client = C8Client(protocol='http', host='localhost', port=8529)

#Step 1: Make one of the regions in the fed as the Spot Region
# Connect to System admin
sys_tenant = client.tenant(email=macrometa-admin-email, password=macrometa-password)
sys_fabric = sys_tenant.useFabric("_system")

#Make REGION-1 as spot-region
sys_tenant.assign_dc_spot('REGION-1',spot_region=True)

#Make REGION-2 as spot-region
sys_tenant.assign_dc_spot('REGION-2',spot_region=True)

#Step 2: Create a geo-fabric and pass one of the spot regions. You can use the SPOT_CREATION_TYPES for the same. If you use AUTOMATIC, a random spot region will be assigned by the system.
# If you specify None, a geo-fabric is created without the spot properties. If you specify spot region,pass the corresponding spot region in the spot_dc parameter.
dcl = sys_tenant.dclist(detail=False)
demotenant = client.tenant(email="mytenant@example.com", password="hidden")
fabric = demotenant.useFabric("_system")
fabric.create_fabric('spot-geo-fabric', dclist=dcl,spot_creation_type= fabric.SPOT_CREATION_TYPES.SPOT_REGION, spot_dc='REGION-1')

#Step 3: Create spot collection in 'spot-geo-fabric'
spot_collection = fabric.create_collection('spot-collection', spot_collection=True)

#Step 4: Update Spot primary region of the geo-fabric. To change it, we need system admin credentials
sys_fabric = client.fabric(tenant=macrometa-admin, name='_system', username='root', password=macrometa-password)
sys_fabric.update_spot_region('mytenant', 'spot-geo-fabric', 'REGION-2')

```
