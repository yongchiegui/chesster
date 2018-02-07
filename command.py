import rating
import re
import slack

add_keywords = ['add', 'added', 'adding']
remove_keywords = ['remove', 'removed', 'removing']
result_keywords = ['win', 'won', 'winning', 'lose', 'lost', 'losing']
challenge_keywords = ['challenge']
showall_keywords = ['show', 'showall']

keyword_to_command = {
    'add': 'add',
    'added': 'add',
    'adding': 'add',
    'remove': 'remove',
    'removed': 'remove',
    'removing': 'remove',
    'challenge': 'challenge',
    'challenged': 'challenge',
    'challenging': 'challenge',
    'win': 'win',
    'won': 'win',
    'winning': 'win',
    'lose': 'lose',
    'lost': 'lose',
    'losing': 'lose',
    'draw': 'draw',
    'drew': 'draw',
    'drawing': 'draw',
    'show': 'showall',
    'showall': 'showall'
}

user_id_pattern = '^<@[UuWw]\w{8}>$'


class CommandManager:
    """Manage all the commands for Chesster"""
    def __init__(self):
        self.commands = []

    def put_command_in_queue(self, command):
        command_keyword = 'explode'
        for index, word in enumerate(command['text']):
            if word in keyword_to_command:
                command_keyword = keyword_to_command[word]
                command['text'][index] = command_keyword
                break

        # TODO: Use string to create commands more elegantly than a series of if else statements
        if command_keyword == 'add':
            self.commands.append(AddCommand(command))
        elif command_keyword == 'remove':
            self.commands.append(RemoveCommand(command))
        elif command_keyword == 'challenge':
            self.commands.append(ChallengeCommand(command))
        elif command_keyword in ['win', 'lose', 'draw']:
            self.commands.append(ResultCommand(command))
        elif command_keyword == 'showall':
            self.commands.append(ShowAllCommand(command))
        else:
            self.commands.append(ExplodeCommand(command))

    def execute_top_command_in_queue(self):
        if len(self.commands) > 0:
            return self.commands.pop().execute()


class Command(object):
    """Command abstract class"""
    def __init__(self, command):
        self.invoker_id = command['user']
        self.invoker_name = slack.get_name_from_id(command['user'])
        self.text = command['text']
        self.arguments = []

    def extract_arguments(self):
        """To be overriden by the different child commands"""
        raise Exception('Not implemented exception')

    def execute(self):
        """To be overridden by the different child commands"""
        raise Exception('Not implemented exception')


class AddCommand(Command):
    def extract_arguments(self):
        """Argument format: ['player_name', 'player_name']"""
        for word in self.text:
            if re.match(user_id_pattern, word):
                name = slack.get_name_from_id(word)
                self.arguments.append(name)

    # TODO: Can't add player to ladder if already there
    def execute(self):
        """Add players to the ladder"""
        self.extract_arguments()
        response = self.invoker_name + ' has added '
        for player in self.arguments:
            rating.add_player(player)
            response = response + player + ', '
        response = response.rstrip(', ') + ' to the ladder.'

        return response


class RemoveCommand(Command):
    def extract_arguments(self):
        """Argument format: ['player_name', 'player_name']"""
        for word in self.text:
            if re.match(user_id_pattern, word):
                name = slack.get_name_from_id(word)
                self.arguments.append(name)

    # TODO: Can't remove player from ladder if not there
    def execute(self):
        """Remove players from the ladder"""
        self.extract_arguments()
        response = self.invoker_name + ' has removed '
        for player in self.arguments:
            rating.remove_player(player)
            response = response + player + ', '
        response = response.rstrip(', ') + ' from the ladder.'

        return response


class ChallengeCommand(Command):
    def extract_arguments(self):
        """Argument format: ['player_name']"""
        for word in self.text:
            if re.match(user_id_pattern, word):
                name = slack.get_name_from_id(word)
                self.arguments.append(name)

    def execute(self):
        """Challenge a player"""
        self.extract_arguments()
        response = self.invoker_name + ' has challenged ' + self.arguments[0]
        return response


class ResultCommand(Command):
    def extract_arguments(self):
        """Argument format: ['player1', 'player2', winner ] """
        opponent = ''
        for word in self.text:
            if re.match(user_id_pattern, word):
                opponent = slack.get_name_from_id(word)

        for word in self.text:
            if word == 'win':
                self.arguments.extend([self.invoker_name, opponent, self.invoker_name])
            elif word == 'lose':
                self.arguments.extend([self.invoker_name, opponent, opponent])
            elif word == 'draw':
                self.arguments.extend([self.invoker_name, opponent, None])

    def execute(self):
        """Set new ratings based on match results"""
        self.extract_arguments()
        new_rating_player_one, new_player_rating_two = rating.set_new_ratings_based_on_match_results\
                                                        (self.arguments[0], self.arguments[1], self.arguments[2])
        response = 'New ratings: ' + self.arguments[0] + ': ' + str(new_rating_player_one) \
                   + '. ' + self.arguments[1] + ': ' + str(new_player_rating_two)
        return response


class ShowAllCommand(Command):
    def extract_arguments(self):
        """Argument format: None"""
        return None

    def execute(self):
        """Show all player ratings"""
        response = ''
        ratings_dict = rating.get_all_player_ratings()
        for name, elo in ratings_dict:
            response = response + name + ': ' + str(elo) + '\r\n'
        return response


class ExplodeCommand(Command):
    def extract_arguments(self):
        """Argument format: None"""
        return None

    def execute(self):
        """Explode"""
        return 'I can\'t process what you just said. Please don\'t tell' \
                ' my creator. I kid, I kid. He\'s a swell guy. Gulp.'