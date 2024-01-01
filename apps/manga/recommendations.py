# encoding:utf-8
from math import sqrt
from typing import Tuple, List


# Returns a distance-based similarity score for person1 and person2
def sim_distance(preferences, person1, person2):
    """
    Calculate the similarity distance between two persons based on their preferences.

    Parameters:
        preferences (dict): A dictionary containing the preferences of different persons.
        person1 (str): The name of the first person.
        person2 (str): The name of the second person.

    Returns:
        float: The similarity distance between person1 and person2.
    """
    # Get the list of shared_items
    shared_items = {item: 1 for item in preferences[person1] if item in preferences[person2]}

    # if they have no ratings in common, return 0
    if len(shared_items) == 0:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum(
        (preferences[person1][item] - preferences[person2][item]) ** 2
        for item in shared_items
    )

    return 1 / (1 + sum_of_squares)


def sim_pearson(preferences, person1, person2):
    """
    Calculate the Pearson similarity score between two users.

    Parameters:
        preferences (dict): Dictionary containing the ratings of users for different items.
        person1 (str): Identifier of the first user.
        person2 (str): Identifier of the second user.

    Returns:
        float: Pearson similarity score between the two users.
    """

    # Get the list of mutually rated items
    shared_items = {item: 1 for item in preferences[person1] if item in preferences[person2]}

    # if there are no ratings in common, return 0
    if len(shared_items) == 0:
        return 0

    # Calculate the number of mutually rated items
    num_mutually_rated_items = len(shared_items)

    # Calculate the sums of all the preferences
    sum_user1 = sum([preferences[person1][item] for item in shared_items])
    sum_user2 = sum([preferences[person2][item] for item in shared_items])

    # Calculate the sums of the squares
    sum_user1_sq = sum([pow(preferences[person1][item], 2) for item in shared_items])
    sum_user2_sq = sum([pow(preferences[person2][item], 2) for item in shared_items])

    # Calculate the sum of the products
    sum_product = sum([preferences[person1][item] * preferences[person2][item] for item in shared_items])

    # Calculate the Pearson score
    numerator = sum_product - (sum_user1 * sum_user2 / num_mutually_rated_items)
    denominator = sqrt((sum_user1_sq - pow(sum_user1, 2) / num_mutually_rated_items) * (
                sum_user2_sq - pow(sum_user2, 2) / num_mutually_rated_items))
    if denominator == 0:
        return 0

    r = numerator / denominator

    return r


# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def top_matches(preferences, person, n=5, similarity=sim_pearson):
    """
    Returns the top n matches for a given person based on similarity scores.

    Parameters:
        preferences (dict): A dictionary containing the preferences of different people.
        person (str): The person for whom to find matches.
        n (int, optional): The number of matches to return. Defaults to 5.
        similarity (Callable[[dict, str, str], float], optional): The similarity function to use. Defaults to sim_pearson.

    Returns:
        List[Tuple[float, str]]: A list of tuples containing the similarity score and the person's name.
    """
    # Calculate the similarity scores between the given person and all other people
    scores = [(similarity(preferences, person, other), other) for other in preferences if other != person]

    # Sort the scores in descending order
    scores.sort()

    # Return the top n matches
    return scores[:n]


# Gets recommendations for a person by using a weighted average of every other user's rankings
from typing import Dict, List


def get_recommendations(preferences, person, similarity=sim_pearson):
    """
    Get movie recommendations for a given person based on their preferences and similarity function.

    Parameters:
        preferences (dict): Dictionary of preferences for each person.
        person (str): The person for whom movie recommendations are being generated.
        similarity (function, optional): The similarity function to use. Defaults to sim_pearson.

    Returns:
        list: Sorted list of movie recommendations for the person.
    """
    # Initialize dictionaries to store the totals and sums of similarities
    totals = {}
    sim_sums = {}

    # Iterate over each person in the preferences
    for other in preferences:
        # Skip the current person
        if other == person:
            continue

        # Calculate the similarity between the current person and the other person
        similarity_score = similarity(preferences, person, other)

        # Ignore scores of zero or lower
        if similarity_score <= 0:
            continue

        # Iterate over each item in the other person's preferences
        for movie in preferences[other]:
            # Only consider items that the person hasn't seen or hasn't rated
            if movie not in preferences[person] or preferences[person][movie] == 0:
                # Calculate the weighted score for the item
                totals.setdefault(movie, 0)
                totals[movie] += preferences[other][movie] * similarity_score

                # Calculate the sum of similarities for the item
                sim_sums.setdefault(movie, 0)
                sim_sums[movie] += similarity_score

    # Create the normalized list of rankings
    rankings = [(total / sim_sums[movie], movie) for movie, total in totals.items()]

    # Sort the rankings in descending order
    rankings.sort()

    return rankings


def transform_prefs(prefs):
    """
    Transforms a dictionary of preferences by flipping the keys and values.

    Parameters:
        prefs (dict): A dictionary of preferences where each key represents a person and the value is a dictionary of items and their respective preferences.

    Returns:
        dict: A transformed dictionary where each key represents an item and the value is a dictionary of people and their respective preferences for that item.
    """
    transformed_prefs = {}
    for person, item_prefs in prefs.items():
        for item, preference in item_prefs.items():
            transformed_prefs.setdefault(item, {})

            # Flip item and person
            transformed_prefs[item][person] = preference
    return transformed_prefs


def calculate_similar_items(preferences, n=10):
    """
    Calculate the most similar items for each item in the preference matrix.

    Parameters:
        preferences (dict): The preference matrix.
        n (int): The number of similar items to calculate. Default is 10.

    Returns:
        dict: A dictionary of items showing which other items they are most similar to.
    """

    # Create a dictionary to store the result
    result = {}

    # Invert the preference matrix to be item-centric
    item_prefs = transform_prefs(preferences)

    count = 0
    for item in item_prefs:
        count += 1

        # Find the most similar items to this one
        scores = top_matches(item_prefs, item, n=n, similarity=sim_distance)
        result[item] = scores

    return result


def get_recommended_items(preferences, item_match, person):
    """
    Get recommended items for a given user based on item similarity.

    Parameters:
        preferences (dict): Dictionary of user ratings for different items.
        item_match (dict): Dictionary of items and their similarity scores.
        person (str): The user for whom recommendations are being generated.

    Returns:
        list: List of recommended items in descending order of ranking.
    """
    user_ratings = preferences[person]
    scores = {}
    total_sim = {}

    # Loop over items rated by this user
    for item, rating in user_ratings.items():
        # Loop over items similar to this one
        for similarity, item2 in item_match[item]:
            # Ignore if this user has already rated this item
            if item2 in user_ratings:
                continue
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            total_sim.setdefault(item2, 0)
            total_sim[item2] += similarity

    rankings = [(score / total_sim[item], item) for item, score in scores.items()] if total_sim else []

    rankings.sort(reverse=True)
    return rankings