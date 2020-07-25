from gql import gql, Client, WebsocketsTransport
from aobject import aobject

ScenarioIDS = {
    'SINGLEPLAYER_HUB':'458627',
    'CUSTOM_SINGLEPLAYER':'458625',
    'MULTIPLAYER_HUB':'458672',
    'CUSTOM_MULTIPLAYER':'458789',
}

class AIDungeonScenario(aobject):
    public_id = ""
    id = ""
    client = None

    async def request_content(self,inner):
        query = """
        query ($id: String) {
            content(id: $id) {
        """
        query += inner
        query += '''
            }
        }
        '''
        print(self.id)
        result = await self.client.request(
            query,
            variables = {
                'id':self.id
            }
        )
        return result

    async def obtain_actions(self):
        if self.client.debug:
            print("Requesting actions for adventure {}".format(self.public_id))
        result = await self.request_content('''
            actions {
                id
                text
            }
        ''')
        return result['content']['actions']

    async def obtain_options(self):
        if self.client.debug:
            print("Requesting actions for adventure {}".format(self.public_id))
        result = await self.request_content('''
            options {
                id
                title
            }
        ''')
        return result['content']['options']
    
    async def obtain_prompt(self):
        return await self.obtain_simple_content('prompt')

    async def obtain_simple_content(self,element):
        if self.client.debug:
            print("Requesting {} for adventure {}".format(element,self.public_id))
        result = await self.request_content(element)
        return result['content'][element]

    async def obtain_memory(self):
        return await self.obtain_simple_content('memory')

    async def obj_type(self):
        return "scenario"

    async def __init__(self, client, half_id='', id=''):
        self.client = client

        if id != '':
            self.id = id
        elif half_id != '':
            self.id = await self.obj_type() + ':' + half_id
