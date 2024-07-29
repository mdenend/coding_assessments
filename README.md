# Coalesce Backend

This repository contains my solution to Niravana's coding assignment. It consists of a backend server that's configurable to query from any number of servers, plus a testing framework designed to replicate acutal running of three servers locally using `flask`.

## To set up
To set up the server, you need to have `python` installed. From the root directory, run 
```python -m venv .venv```

Then activate the virtual environment:

```
source .venv/bin/activate
```

Or for Windows:
```
# In cmd.exe
.venv\Scripts\activate.bat
# In PowerShell
.venv\Scripts\Activate.ps1
```

Then install the requirements:
```
pip install -r requirements.txt
```

## To run the server
```
flask --app src.coalesce_server run
```

Note that this will not work on its own. It is configured to query three other servers running at ports 5001, 5002, and 5003. To start up these testing servers, you can do so by running, in a different shell window:
```
python test/run_query_servers.py
```
If you need to change any of these ports, you can do so under `test/query_server_config/.env_server[1-3]` for the server you wish to change. You will also need to change the addresses under `src/config/config.yml` to correspond to the new server(s) port(s).

## How to query the server

After you've started up the coalesce server and the three test servers, the actual endpoint is at `/api/coalescence/<method>?member_id=<id>`. `<method>` is a required parameter specifying one of the four following coalescence methods:

- `default`: I thought the most reasonable strategy would be to show the maximum oop_max and remaining_oop_max from the servers, since the member would know that they would for sure not have to pay any more than any of the maxes that are listed. I also did the same approach for copay; however, since the copay goes towards the oop_max, I thought the copay should never exceed the maximum remaining_oop_max, so if copay exceeds that, I set copay to the max remaining_oop_max.
- `max`: Takes the max of all three of oop_max, remaining_oop_max, and copay.
- `min`: Takes the min of all three of oop_max, remaining_oop_max, and copay.
- `avg`: Takes the avg of all three of oop_max, remaining_oop_max, and copay. Since we're dealing with cents, I rounded to 0 places. I also still use float division (/) because integer divison (//) would just take the floor of the cent amount, but I think we should just round to the nearest amount.

If an invalid coalesence method is provided, a 400 error code is returned.

`member_id` is a required parameter. There are three members the test query servers understand: 1, 2, and 3. You can see what servers return in `test/query_server_data`. Of note, member id 3 is only on query server 1, so all four coalescence methods should by definition return the same values for that user. If a member id doesn't exist on any servers, I decided to return a 404 Not Found error, even though a 200 OK could be justified with a blank response.

### Extending coalescence methods
Further coalescence methods can be defined by following these steps:
1. In `src/strategies.py`, add a function that has `oop_max_list`, `remaining_oop_max_list`, and `copay_list` as `List[int]` parameters, and returns of three integers: `oop_max`, `remaining_oop_max`, and `copay`. Choose how you coalesce these parameters.
2. In `src/coalesce_server.py`, import the new function you created and add a new key:value pair to `VALID_STRATEGIES`. key is the endpoint you wish the API to query, and value is the function you imported.

## Tests
To run tests, from this directory, run
```
pytest -v test/tests.py
```

For testing, I thought it would be best to have an end-to-end tests using the three servers that can be spun up. I considered unit tests but I thought this would be a bit overkill for a single endpoint. If I were working on a more robust backend, I definitely would write unit tests, since their goal is to ensure that developers don't break the functionality of an endpoint in the future.

The tests I wrote are to check that all the coalescence methods work for all three patients, and a couple of error cases: no member id, member id not found, and invalid coalescence method. I used pytest's fixtures to setup and teardown the servers after the entire suite of them is finished (this is fine since the servers do not change their data in any test, otherwise I would have to consider more fine-grained fixture scopes), and pytest's parameterize to reduce the bloat of testing code.

## Considerations/Consolations
Because I spent a decent amount of time solving this, I think I've (hopefully) got my point across, and I wanted to get this done by today (Monday), I decided to stop working and list things that I would do for more cleanup if I had more time.

- First and probably most important, this definitely would not go into production, running `flask run`. If this were meant for production, I would use something else meant to handle production load wSGI servers. I usually prefer `gunicorn` for this purpose, but `gunicorn` doesn't run on Windows (https://github.com/benoitc/gunicorn/issues/524), so I decided against trying to find a WSGI solution for this problem, as I would almost certainly run this server on a Linux OS over Windows if it were in production.
- The port of the coalescence server is always at port 5000. One could fix this by independently running the server by setting `FLASK_RUN_PORT` to the port of their choice, and I could fix this in testing by adding a .env file for the server and passing that in my server setup in pytest (much like I did for the query servers), but I thought against it as it would add more complexity to an already complex submission.
- I set up no authentication, as that's out of the scope of this assignment. If I were to, I would probably use an Oauth2 flow with JWT. A proxy server like oauth2-proxy could be use to terminate the JWT token, or the backend could directly handle it if we wanted to fine-grain the authentication per endpoint.
- The coalesence server should better handle if it can't reach a server (like Connection Refused, or timing out) and return a properly formatted 500 error code.
- As already mentioned, I decided against doing unit tests for one endpoint, but definitely would for a more robust backend.
- It appears querying for and returning the values from other Flask API servers seems incredibly slow on Windows. I would expect this to be much faster on a MacOS, but I don't want to use my work laptop for testing coding interview problems.
- To tie to the previous consession, performance was never considered. I probably would cache the values using something like Redis if it were, or discuss with the team possible caching options. We could just start with caching in memory, but I would suggest caching with Redis or some similar solution for something more customer facing. I don't think this little of data should need caching, but the slowness of querying three flask servers on Windows made me consider it.
- I prefer to build out an OpenAPI/Swagger specification, but I felt like that would be overkill for a one endpoint coding example. I can just explain in the README what my endpoint does, output, and error codes.
- I could have added logging to the server using Python's `logging` module, but I would have wanted to add a `logging.conf` file as well. I thought this would be unnecessary bloat for such a small example.
- I gave serious thought about Dockerizing both the actual coalesce server and the query servers, but this would reduce portability of running the solution, because it would require Docker to be on the machine. This solution, as it stands, only needs Python to run. If I did decide to Dockerize it, I would have a Docker Compose file that kicks off all four servers together and puts them into a network. Then the addresses would be like http://query-server-1:5000, http://query-server-2:5000, etc.
- One thing that I think looks a bit silly is the fact that I have two different ways of loading configurations: I use YAML for the coalesce server, and I use .env files for the query servers. Each config has a purpose:
    - The .env file can be used with `flask run`.
    - I used yaml for the actual backend because I wanted to be able to list an arbitrary number of servers. I can't do this easily with an environmental variable unless if it's comma limited like http://localhost:5001,http:localhost:5002,... I just felt like this wasn't very clean so decided against it.
- Not many comments in this code, I usually comment my functions/methods/classes like I do in `src/strategies.py`, the `default_strategy` function. I tend to at least loosely follow Google's Python style guide: https://google.github.io/styleguide/pyguide.html. I consider this too simple to comment too much. Hopefully it's easy to understand :-)