## Octoxlabs Senior Backend Engineer Case Study

We aim to develop a composite application utilizing Docker and docker-compose, which comprises minimum five services: your Django REST Framework endpoint, query converter service(django, flask, fastapi etc.), logger service(celery or implement your handler if possible), a message queue service and an Elasticsearch service. The Django REST Framework endpoint should include minimum two features:

* **Authentication Mechanism:** We are looking for an authentication method similar to JWT. For instance, if there is a user with the username "octoAdmin," we would add an Authorization header as "Octoxlabs base64(octoAdmin<username>)". This token should uniquely identify the user "octoAdmin".
* **Endpoint:** Consider having data structured as an array like [{"Hostname": "octoxlabs01", "Ip": ["0.0.0.0"]}] stored in the Elasticsearch service. We expect to query your endpoint with "Hostname = octoxlabs*" and have this query translated into the JSON format for Elasticsearch. Please avoid using query_string in Elasticsearch, if possible. The scenario involves the endpoint converting the "Hostname = octoxlabs*" query into an Elasticsearch-compatible format, querying Elasticsearch, and then returning the data in the response.
  
  ```
	POST /search
	{
	    "query": "Hostname = octoxlabs*"
	}
  ```
	**Hint:** Elasticsearch indices have mappings, and their fields have properties like "keyword." For example, if you create an index in Elasticsearch named "octoxlabsdata," you can access its mapping with "GET /octoxlabsdata/_mapping".


Scenario: End-user send query request to django endpoint, django ask to converter service this query for elasticsearch-compatible format, send it to elasticsearch and return the results for frontend. Queries sent by the end-user should be logged in file or another elasticsearch indice by logger service.


Advantages of completing this case study include:
* Implement your logger service instead of celery. (You can use any programming language you want)
* Implementing unit tests.
* Implementing code quality tools.
* A management command that interacts with your endpoint.
* **!** Security.


Please submit your code via a GitHub link or as a zip file attachment in your response. Mail subject is this filename.  
ahmet[dot]kotan[at]octoxlabs[dot]com / Co-Founder and CTO @ Octoxlabs  
Good luck!
