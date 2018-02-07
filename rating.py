import json
import math
import operator
import s3

with open('config.json', 'r') as f:
    config = json.load(f)

DEFAULT_RATING = config['GENERAL']['DEFAULT_RATING']


def add_player(player):
    """Adds a new player to the ladder"""
    ratings = s3.get_ratings_from_s3()
    ratings[player] = DEFAULT_RATING
    s3.store_ratings_to_s3(sorted(ratings.items(), key=operator.itemgetter(1), reverse=True))


def remove_player(player):
    """Removes a player from the ladder"""
    ratings = s3.get_ratings_from_s3()
    ratings.pop(player)
    s3.store_ratings_to_s3(sorted(ratings.items(), key=operator.itemgetter(1), reverse=True))


def set_new_ratings_based_on_match_results(player_one, player_two, winner=None):
    """Calculates two players' new ratings given the match result"""
    ratings = s3.get_ratings_from_s3()

    player_rating_one = int(ratings[player_one])
    player_rating_two = int(ratings[player_two])

    transformed_rating_one = math.pow(10, player_rating_one / 400.0)
    transformed_rating_two = math.pow(10, player_rating_two / 400.0)

    expected_score_one = transformed_rating_one / (transformed_rating_one + transformed_rating_two)
    expected_score_two = transformed_rating_two / (transformed_rating_one + transformed_rating_two)

    if winner == player_one:
        actual_score_one = 1
        actual_score_two = 0
    elif winner == player_two:
        actual_score_one = 0
        actual_score_two = 1
    else:
        actual_score_one = 0.5
        actual_score_two = 0.5

    new_player_rating_one = int(player_rating_one + 40 * (actual_score_one - expected_score_one))
    new_player_rating_two = int(player_rating_two + 40 * (actual_score_two - expected_score_two))

    ratings[player_one] = new_player_rating_one
    ratings[player_two] = new_player_rating_two

    s3.store_ratings_to_s3(sorted(ratings.items(), key=operator.itemgetter(1), reverse=True))
    return new_player_rating_one, new_player_rating_two


def get_all_player_ratings():
    """Get all of the player's ratings"""
    ratings = s3.get_ratings_from_s3()
    return sorted(ratings.items(), key=operator.itemgetter(1), reverse=True)