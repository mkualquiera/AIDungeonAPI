from gql import gql, Client, WebsocketsTransport
from aobject import aobject
from aidscenario import AIDungeonScenario

class AIDungeonAdventure(AIDungeonScenario):
    client = None
    character_name = ""

    async def add_user_to_adventure(self):
        if self.client.debug:
            print("Adding user to adventure {}".format(self.public_id))
        result = await self.client.request(
            '''
            mutation ($adventurePlayPublicId: String) {
                addUserToAdventure(adventurePlayPublicId: $adventurePlayPublicId)
            }
            ''',
            variables = {
                'adventurePlayPublicId':self.public_id
            }
        )
        return result['addUserToAdventure']

    async def send_simple_action(self,type):
        if self.client.debug:
            print("Requesting {} in adventure {}".format(type,self.public_id))
        result = await self.client.request(
            '''
            mutation ($input: ContentActionInput) {
                sendAction(input: $input) {
                    id
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'type':type,
                    'id':self.id,
                    'characterName':self.character_name
                }
            }
        )
        return result

    async def set_character_name(self,name):
        if self.client.debug:
            print("Setting character name to {}".format(name))
        result = await self.client.request(
            '''
            mutation ($input: CharacterInput) {
                updateCharacter(input: $input) {
                    id
                    name
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'name':name,
                    'adventureId':self.id.split(':')[1]
                }
            }
        )
        self.character_name = name
        return result

    async def send_text(self,text,type="story"):
        if self.client.debug:
            print("Sending text >{}<".format(text))
        result = await self.client.request(
            '''
            mutation ($input: ContentActionInput) {
                sendAction(input: $input) {
                    id
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'type':type,
                    'text':text,
                    'id':self.id,
                    'characterName':self.character_name
                }
            }
        )
        return result

    async def undo(self):
        await self.send_simple_action('undo')

    async def redo(self):
        await self.send_simple_action('redo')

    async def retry(self):
        await self.send_simple_action('retry')

    async def alter_action(self,action_id,text):
        if self.client.debug:
            print("Requesting alter action {} in adventure {}...".format(
                action_id,
                self.public_id)
            )
        result = await self.client.request(
            '''
            mutation ($input: ContentActionInput) {
                doAlterAction(input: $input) {
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'actionId':action_id,
                    'text':text,
                    'type':'alter',
                    'id':self.id
                }
            }
        )

    async def alter_memory(self, new_memory):
        if self.client.debug:
            print("Requesting alter memory in adventure {}...".format(
                self.public_id)
            )
        result = await self.client.request(
            '''
            mutation ($input: ContentActionInput) {
                updateMemory(input: $input) {
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'text':new_memory,
                    'type':'remember',
                    'id':self.id
                }
            }
        )
        return result

    async def obtain_is_loading(self):
        return await self.obtain_simple_content('actionLoading')

    async def obtain_error(self):
        return await self.obtain_simple_content('error')

    async def obtain_gamestate(self):
        return await self.obtain_simple_content('gameState')

    async def obtain_mode(self):
        return await self.obtain_simple_content('mode')

    async def obtain_has_died(self):
        return await self.obtain_simple_content('died')

    async def obtain_is_third_person(self):
        return await self.obtain_simple_content('thirdPerson')

    async def obtain_actions(self):
        super().obtain_actions()

    async def obtain_prompt(self):
        actions = await self.obtain_actions()
        return actions[0]['text']

    async def obtain_last_action(self):
        actions = await self.obtain_actions()
        return actions[-1]

    async def obj_type(self):
        return "adventure"

    async def __init__(self, client, public_id='', half_id='', id=''):
        await super().__init__(client,half_id=half_id,id=id)
        if public_id != '':
            self.public_id = public_id
            self.id = await self.add_user_to_adventure()
