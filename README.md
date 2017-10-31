# The Extensible Data Gateway Environment (EDGE)
The Extensible Data Gateway Environment (EDGE) is a data integration platform designed to facilitate high-performance geospatial data discovery and access with the ability to support multimetadata standard specifications. EDGE is designed with two main building blocks: data aggregation service and enterprise geospatial indexed search cluster. The data aggregation service provides web service interfaces for searches, metadata packaging, and data access. Aggregation often involves retrieving data from two or more sources and packaging the resulting sets into a single response to the requestor. It could also serve as a proxy to other local/remote services to reduce the number of interfaces a requestor has to access. The enterprise geospatial indexed search cluster, which currently supports Apache Solr (http://lucene.apache.org/solr/) and ElasticSearch (http://elasticsearch.org), is a horizontal scale cluster for faceted search with geospatial support.

EDGE now lives at the Apache Software Foundation under the Apache Science Data Analytics Platform (SDAP) Incubating project.

You can access the SDAP Website at https://sdap.apache.org

The SDAP Source Code lives at https://github.com/apache/incubator-sdap-edge
