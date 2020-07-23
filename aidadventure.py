from gql import gql, Client, WebsocketsTransport

class AIDungeonAdventure:
    public_id = ""
    id = ""
    client = None
    character_name = ""

    def add_user_to_adventure(self):
        if self.client.debug:
            print("Adding user to adventure {}".format(self.public_id))
        result = self.client.request(
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

    def request_content(self,inner):
        query = """
        query ($id: String) {
            content(id: $id) {
        """
        query += inner
        query += '''
            }
        }
        '''
        result = self.client.request(
            query,
            variables = {
                'id':self.id
            }
        )
        return result

    def send_action(self,type):
        result = self.client.request(
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

    def set_character_name(self,name):
        if self.client.debug:
            print("Setting character name to {}".format(name))
        result = self.client.request(
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

    def send_text(self,text,type="story"):
        result = self.client.request(
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

    def undo(self):
        if self.client.debug:
            print("Requesting undo in adventure {}".format(self.public_id))
        self.send_action('undo')

    def redo(self):
        if self.client.debug:
            print("Requesting redo in adventure {}".format(self.public_id))
        self.send_action('redo')

    def retry(self):
        if self.client.debug:
            print("Requesting retry in adventure {}".format(self.public_id))
        self.send_action('retry')

    def alter_action(self,action_id,text):
        if self.client.debug:
            print("Requesting alter action {} in adventure {}...".format(
                action_id,
                self.public_id)
            )
        result = self.client.request(
            '''
            query ($id: String) {
                content(id: $id) {
                    actionLoading
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

    def alter_memory(self, new_memory):
        if self.client.debug:
            print("Requesting alter memory in adventure {}...".format(
                self.public_id)
            )
        result = self.client.request(
            '''
            mutation ($input: ContentActionInput) {
                updateMemory(input: $input) {
                    id
                    memory
                    __typename
                }
            }
            ''',
            variables = {
                'input':{
                    'text':text,
                    'type':'remember',
                    'id':self.id
                }
            }
        )
        return result

    def obtain_is_loading(self):
        if self.client.debug:
            print("Requesting if adventure is loading...")
        result = self.request_content('actionLoading')
        return result['content']['actionLoading']

    def obtain_actions(self):
        if self.client.debug:
            print("Requesting actions for adventure {}".format(self.public_id))
        result = self.request_content('''
            actions {
                id
                text
            }
        ''')
        return result['content']['actions']

    def obtain_error(self):
        if self.client.debug:
            print("Requesting error for adventure {}".format(self.public_id))
        result = self.request_content('error')
        return result['content']['error']

    def obtain_memory(self):
        if self.client.debug:
            print("Requesting memory for adventure {}".format(self.public_id))
        result = self.request_content('memory')
        return result['content']['memory']

    def obtain_gamestate(self):
        if self.client.debug:
            print("Requesting gamestate for adventure {}".format(self.public_id))
        result = self.request_content('gameState')
        return result['content']['gameState']

    def obtain_mode(self):
        if self.client.debug:
            print("Requesting mode for adventure {}".format(self.public_id))
        result = self.request_content('mode')
        return result['content']['mode']

    def obtain_has_died(self):
        if self.client.debug:
            print("Requesting has died for adventure {}".format(self.public_id))
        result = self.request_content('died')
        return result['content']['died']

    def obtain_is_third_person(self):
        if self.client.debug:
            print("Requesting is third person for adventure {}".format(self.public_id))
        result = self.request_content('thirdPerson')
        return result['content']['thirdPerson']

    def obtain_last_action(self):
        actions = self.obtain_actions()
        return actions[-1]

    def __init__(self, client, public_id):
        self.client = client
        self.public_id = public_id
        self.id = self.add_user_to_adventure()
