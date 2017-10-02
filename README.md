# The Extensible Data Gateway Environment (EDGE)
The Extensible Data Gateway Environment (EDGE) is a data integration platform designed to facilitate high-performance geospatial data discovery and access with the ability to support multimetadata standard specifications. EDGE is designed with two main building blocks: data aggregation service and enterprise geospatial indexed search cluster. The data aggregation service provides web service interfaces for searches, metadata packaging, and data access. Aggregation often involves retrieving data from two or more sources and packaging the resulting sets into a single response to the requestor. It could also serve as a proxy to other local/remote services to reduce the number of interfaces a requestor has to access. The enterprise geospatial indexed search cluster, which currently supports Apache Solr (http://lucene.apache.org/solr/) and ElasticSearch (http://elasticsearch.org), is a horizontal scale cluster for faceted search with geospatial support.

# Setup

1. Setup and activate a conda environment

    ````
    conda create --name edge python
    source activate edge
    ````

2. Install dependencies

    ````
    cd edge/src/main/python
    pip install -r requirements.txt
    ````

3. Update pythonpath

    ````
    source edge-env.bash
    ````

4. Launch EDGE service

    ````
    python server.py
    ````
# Adding Custom Plugin

You will need to customize EDGE to work with your existing Apache Solr or ElasticSearch metadata endpoints.

## ElasticSearch

For an ElasticSearch example plugin, see [plugins/example/elastic](src/main/python/plugins/example/elastic)

Copy the plugins/example/elastic plugin into a new directory, for example, plugsin/myproject/elastic.

Update [plugin.conf](src/main/python/plugins/example/elastic/plugin.conf) datasetUrl to point to an ElasticSarch index endpoint.

Update [template.xml](src/main/python/plugins/example/elastic/template.xml to match the response XML. Metadata values for each document returned are stored in the doc variable dictionary, for example, doc['ShortName'].

Update [server.py](src/main/python/server.py) to add a new endpoint that will invoke the newly created plugin, for example,

    ````
    (r"/myplugin/es", GenericHandler, dict(pluginName='myplugin', format=['elastic'])),
    ````

Restart EDGE and access the new endpoint at [http://localhost:8890/myplugin/es](http://localhost:8890/myplugin/es).
