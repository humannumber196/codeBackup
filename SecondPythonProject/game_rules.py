# game_rules.py
# --------------
# COMP3620/6320 Artificial Intelligence
# The Australian National University
# For full attributions, see attributions.txt on Wattle at the end of the course

""" This file defines the rules of the game being played and the rules for both
    the red bird and the black bird.
    
    It describes the game flow, what constitutes a legal move for an agent, and
    how a successor state is produced.
    
    You should not need to look at this file.

    ********** YOU SHOULD NOT CHANGE ANYTHING IN THIS FILE **********
"""

from game import Game
from state import State
from actions import Actions, Directions

YELLOW_BIRD_SCORE = 100
TIME_PENALTY = 1

class ClassicGameRules(object):
    """ These game rules manage the control flow of a game, deciding when and
        how the game starts and ends.
    """
    def __init__(self, timeout=30):
        """ Make a new instance of the game rules.
            (ClassicGameRules, int) -> None
        """
        self.timeout = timeout

    def new_game(self, layout, red_bird_agent, black_bird_agent, display,
        quiet=False, catch_exceptions=False):
        """ Make and return a new Game object with the given parameters.
            (Layout, Agent, [Agent], RedBirdGraphics, bool, bool) -> Game
        """
        self.layout = layout
        initial_state = State(layout)
        game = Game(red_bird_agent, black_bird_agent, display, self,
            catch_exceptions=catch_exceptions)
        game.state = initial_state
        self.initial_state = initial_state.deepcopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """ Checks to see whether it is time to end the game.
            (ClassicGameRules, State, Game) -> None
        """
        if state.is_win():
            self.win(state, game)
        if state.is_lose():
            self.lose(state, game)

    def win(self, state, game):
        """ The game has been won by the red bird.
            (ClassicGameRules, State, Game) -> None
        """
        if not self.quiet:
            print "Red has won! Score:", state.score
        game.game_over = True

    def lose(self, state, game):
        """ The game has been lost by the red bird.
            (ClassicGameRules, State, Game) -> None
        """
        if not self.quiet:
            print "Red has lost. Score:", state.score
        game.game_over = True

    def get_progress(self, game):
        """ Returnt the fraction of yellow birds reached.
            (ClassicGameRules, Game) -> float
        """
        return float(game.state.get_num_yellow_bird()) /\
            self.initial_state.get_num_yellow_bird()

    def agent_crash(self, game, agent_index):
        """ Indicate that the agent crashed.
            (ClassicGameRules, Game, int) -> None
        """
        if agent_index == 0:
            print "Red crashed"
        else:
            print "A black bird crashed"

    def get_max_total_time(self, agent_index):
        """ Return the maximum total time the agent can take to make its decisions.
            (ClassicGameRules, int) -> float
        """
        return self.timeout

    def get_max_startup_time(self, agent_index):
        """ Return the maximum total time the agent can take to start up.
            (ClassicGameRules, int) -> float
        """
        return self.timeout

    def get_move_warning_time(self, agent_index):
        """ Return the time after which the agent gets a warning about taking
            too long to choose a move.
            (ClassicGameRules, int) -> float
        """
        return self.timeout

    def get_move_timeout(self, agent_index):
        """ Return the time which the agent has to make a move.
            (ClassicGameRules, int) -> float
        """
        return self.timeout

    def get_max_time_warnings(self, agent_index):
        """ Return the maximum number of move time warnings an agent can have.
            (ClassicGameRules, int) -> float
        """
        return 0


class RedBirdRules(object):
    """ These functions govern how the red bird interacts with his environment
        under the classic game rules.
    """
    
    @staticmethod
    def get_legal_actions(state):
        """ Returns a list of possible actions.
            (State) -> [str]
        """
        return Actions.get_legal_actions(state.red_bird_position,
            state.layout.walls, state.black_bird_position)
        
    @staticmethod
    def apply_action(state, action):
        """ Edits the state to reflect the results of the action.
            (State, str) -> None
        """
        if action not in RedBirdRules.get_legal_actions(state):
            raise Exception("Illegal action " + str(action))
        state.score_change = 0
        
        next_pos = Actions.get_successor(state.red_bird_position, action)
        state.red_bird_position = next_pos

        if next_pos in state.yellow_birds:
            state.score_change += state.current_yellow_bird_score#YELLOW_BIRD_SCORE
            state.yellow_birds = tuple([yb for yb in state.yellow_birds if yb != next_pos])
            state._yellow_bird_eaten = next_pos
            if state.black_bird_position is not None:
                state.current_yellow_bird_score = max(1, state.current_yellow_bird_score - 1)
            if not state.yellow_birds:
                state.terminal = True
        
        #There is only a time penalty if we do not have an adversary
        if state.get_black_bird_position() is None:
            state.score_change -= TIME_PENALTY

class BlackBirdRules(object):
    """ These functions dictate how black birds interact with their environment
        under the classic game rules.
    """
    
    @staticmethod
    def get_legal_actions(state):
        """ Black birds can move in the same way as red birds.
        """
        return Actions.get_legal_actions(state.black_bird_position,
            state.layout.walls, state.red_bird_position)
        
    @staticmethod
    def apply_action(state, action):
        """ Edits the state to reflect the results of the action.
            (State, str) -> None
        """
        if action not in BlackBirdRules.get_legal_actions(state):
            raise Exception("Illegal action " + str(action))
        state.score_change = 0
        
        next_pos = Actions.get_successor(state.black_bird_position, action)
        state.black_bird_position = next_pos

        if next_pos in state.yellow_birds:
            state.score_change -= state.current_yellow_bird_score
            state.yellow_birds = tuple([yb for yb in state.yellow_birds if yb != next_pos])
            state._yellow_bird_eaten = next_pos
            if state.black_bird_position is not None:
                state.current_yellow_bird_score = max(1, state.current_yellow_bird_score - 1)   
            if not state.yellow_birds:
                state.terminal = True

