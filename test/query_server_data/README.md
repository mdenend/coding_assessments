For simplicity sake, I decided to just store the data for two patients, ids 1 and 2, as JSON files for the three different servers. I also included id 3 in just one file, in case one server has a patient, but the other two don't.
The server should be able to handle this case.

Using files for data storage isn't a good practice. In a real world scenario, I would be using a database to store this info. But we don't need to here. Plus, we'd assume the servers are going to function as expected.