from gql import gql, Client, WebsocketsTransport
from .aobject import aobject

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
        result = await self.client.request(
            query,
            variables = {
                'id':self.id
            }
        )
        return result['content']

    async def subscribe_content(self,inner,callback):
        query = """
        subscription subscribeContent($id: String) {
            subscribeContent(id: $id) {
        """
        query += inner
        query += '''
            }
        }
        '''

        async def inner_callback(object):
            await callback(object["subscribeContent"])

        await self.client.subscribe(
            query,
            inner_callback,
            variables = {
                'id':self.id
            }
        )

    async def obtain_actions(self):
        if self.client.debug:
            print("Requesting actions for {} {}".format(self.obj_type(),self.id))
        result = await self.request_content('''
            actions {
                id
                text
            }
        ''')
        return result['actions']

    async def register_actions_callback(self, callback):
        if self.client.debug:
            print("Registering actions callback for {} {}".format(self.obj_type(),self.id))

        async def inner_callback(object):
            await callback(object['actions'])

        await self.subscribe_content('''
            actions {
                id
                text
            }
        ''',inner_callback)

    async def obtain_options(self):
        if self.client.debug:
            print("Requesting options for {} {}".format(self.obj_type(), self.id))
        result = await self.request_content('''
            options {
                id
                title
            }
        ''')
        return result['options']

    async def obtain_prompt(self):
        return await self.obtain_simple_content('prompt')

    async def obtain_simple_content(self,element):
        if self.client.debug:
            print("Requesting {} for {} {}".format(element,self.obj_type(),self.id))
        result = await self.request_content(element)
        return result[element]

    async def register_simple_content_callback(self,element,callback):
        if self.client.debug:
            print("Creating {} callback for {} {}".format(element,self.obj_type(),self.id))

        async def inner_callback(object):
            await callback(object[element])

        await self.subscribe_content(element,inner_callback)

    async def obtain_memory(self):
        return await self.obtain_simple_content('memory')

    async def register_memory_callback(self, callback):
        await self.register_simple_content_callback('memory',callback)

    def obj_type(self):
        return "scenario"

    async def __init__(self, client, half_id='', id=''):
        self.client = client

        if id != '':
            self.id = id
        elif half_id != '':
            self.id = self.obj_type() + ':' + half_id
