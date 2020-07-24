from gql import gql, Client, WebsocketsTransport
from aidadventure import AIDungeonAdventure
from aobject import aobject

class AIDungeonClient(aobject):
    token = ''
    gql_client = None
    debug = False

    def set_client_with_token(self, token):
        self.token = token
        gql_transport = transport = WebsocketsTransport(
            url='wss://api.aidungeon.io/subscriptions',
            init_payload={'token':token}
        )
        self.gql_client = Client(
            transport=gql_transport,
            fetch_schema_from_transport=True
        )

    async def request(self, query_text, variables={}):
        query = gql(
            query_text
        )
        return await self.gql_client.execute_async(query,variable_values=variables)

    async def request_user(self):
        result = await self.request(
            """
            {
                user {
                    id
                    username
                    __typename
                }
            }
            """
        )
        return result['user']

    async def request_create_anonymous_user(self):
        result = await self.request(
            """
            mutation {
                createAnonymousAccount
                {
                    id
                    accessToken
                    __typename
                }
            }
            """
        )
        return result['createAnonymousAccount']

    async def send_event(self, eventName):
        if self.debug:
            print("Sending event {}...".format(eventName))
        result = await self.request(
            """
                mutation ($input: EventInput) {  sendEvent(input: $input)}
            """,
            variables={
                'input':{
                    'eventName':eventName,
                    'platform':'web'
                }
            }
        )
        return result

    async def get_adventure(self, id):
        return await AIDungeonAdventure(self, id)

    async def __init__(self, token='', debug=False):
        self.debug = debug
        self.set_client_with_token(token)
        if self.debug:
            print("Verifying user...")
        if await self.request_user() == None:
            new_user = await self.request_create_anonymous_user()
            self.set_client_with_token(new_user['accessToken'])
            if self.debug:
                print("Initialized with anonymous user, token {}".format(self.token))
