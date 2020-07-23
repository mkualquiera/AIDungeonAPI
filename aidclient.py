from gql import gql, Client, WebsocketsTransport
from aidadventure import AIDungeonAdventure


class AIDungeonClient:
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

    def request(self, query_text, variables={}):
        query = gql(
            query_text
        )
        return self.gql_client.execute(query,variable_values=variables)

    def request_user(self):
        result = self.request(
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

    def request_create_anonymous_user(self):
        result = self.request(
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

    def send_event(self, eventName):
        if self.debug:
            print("Sending event {}...".format(eventName))
        result = self.request(
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

    def get_adventure(self, id):
        return AIDungeonAdventure(self, id)

    def __init__(self, token='', debug=False):
        self.debug = debug
        self.set_client_with_token(token)
        if self.debug:
            print("Verifying user...")
        if self.request_user() == None:
            new_user = self.request_create_anonymous_user()
            self.set_client_with_token(new_user['accessToken'])
            if self.debug:
                print("Initialized with anonymous user, token {}".format(self.token))
