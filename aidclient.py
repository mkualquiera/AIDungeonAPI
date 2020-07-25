from gql import gql, Client, WebsocketsTransport
from aidadventure import AIDungeonAdventure
from aidscenario import AIDungeonScenario
from aobject import aobject
import asyncio

class AIDungeonClient(aobject):
    token = ''
    gql_client = None
    debug = False

    def set_client_with_token(self, token):
        self.token = token
        gql_transport = WebsocketsTransport(
            url='wss://api.aidungeon.io/subscriptions',
            init_payload={'token':token}
        )
        self.gql_client = Client(
            transport=gql_transport,
            fetch_schema_from_transport=True
        )

    async def subscribe(self, subscription_text, callback, variables={}):
        asyncio.create_task(
            self.subscribe_b(subscription_text, callback, variables)
        )

    async def subscribe_b(self, subscription_text, callback, variables={}):
        query = gql(
            subscription_text
        )
        async for result in self.gql_client.subscribe_async(query,variable_values=variables):
            await callback(result)

    async def request(self, query_text, variables={}):
        query = gql(
            query_text
        )
        return await self.gql_client.execute_async(query,variable_values=variables)

    async def attempt_login(self, username, password):
        result = await self.request(
            """
            mutation ($email: String, $password: String, $anonymousId: String) {
                login(email: $email, password: $password, anonymousId: $anonymousId) {
                    id
                    accessToken
                    __typename
                }
            }
            """,
            variables = {
                'email':username,
                'password':password
            }
        )
        return result['login']['accessToken']

    async def refresh_search_index(self):
        await self.request(
            """
            mutation {
                refreshSearchIndex
            }
            """
        )

    async def get_user_adventures(self):
        await self.refresh_search_index()
        result = await self.request(
            """
            query user($input: ContentListInput) {
                user {
                    contentList(input: $input) {
                        id
                        contentType
                        contentId
                        title
                        description
                        tags
                        nsfw
                        published
                        createdAt
                        updatedAt
                        deletedAt
                        userVote
                        totalUpvotes
                        totalComments
                        user {
                            id
                            username
                        }
                    }
                }
            }
            """,
            variables = {
                'input':{
                    'contentType':'adventure',
                    'searchTerm':'',
                    'thirdPerson':None,
                    'sortOrder':'createdAt',
                    'timeRange':None
                }
            }
        )
        return result['user']['contentList']

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

    async def has_premium(self):
        result = await self.request(
            """
            {
                user {
                    hasPremium
                }
            }
            """
        )
        return result['user']['hasPremium']

    async def last_adventure_id(self):
        result = await self.request(
            """
            {
                user {
                    lastAdventure {
                        id
                    }
                }
            }
            """
        )
        return result['user']['lastAdventure']['id']
    
    async def create_adventure(self, scenario_id, prompt, prompt_variables={}):
        if self.debug:
            print("Creating advenure from scenario {}...".format(scenario_id))
        new_prompt = prompt
        for key in prompt_variables.keys():
            new_prompt = new_prompt.replace('${' + key + '}', prompt_variables[key])
        result = await self.request(
            """
            mutation ($id: String, $prompt: String) {  
                createAdventureFromScenarioId(id: $id, prompt: $prompt) {    
                        id    
                    }
                }
            """
            ,variables={
                'id':scenario_id,
                'prompt':new_prompt
            }
        )
        return result['createAdventureFromScenarioId']['id']


    async def connect_to_public_adventure(self, public_id):
        if self.debug:
            print("Connecting to public adventure {}...".format(public_id))
        return await AIDungeonAdventure(self, public_id=public_id)
    
    async def connect_to_private_adventure(self, id):
        if self.debug:
            print("Connecting to private adventure {}...".format(id))
        return await AIDungeonAdventure(self, half_id=id)

    async def connect_to_scenario(self, id):
        if self.debug:
            print("Connecting to scenario adventure {}...".format(id))
        return await AIDungeonScenario(self, half_id=id)

    async def __init__(self, token='', username='', password='', debug=False):
        self.debug = debug

        if token == '':
            self.set_client_with_token('')
            if username != '' and password != '':
                token = await self.attempt_login(username, password)
        self.set_client_with_token(token)

        if self.debug:
            print("Verifying user...")

        user = await self.request_user()
        if user == None:
            if self.debug:
                print("No valid user.")
            new_user = await self.request_create_anonymous_user()
            self.set_client_with_token(new_user['accessToken'])
            if self.debug:
                print("Initialized with anonymous user, token {}".format(self.token))
        else:
            if self.debug:
                print("User provided is valid.")
                print("Logged in as", user['username'])
