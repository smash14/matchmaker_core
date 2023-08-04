from datetime import datetime


def get_consecutive_matches_list(all_teams):
    consecutive_matches = []
    for team in all_teams:
        consecutive_matches.append([team.team_name, team.get_total_consecutive_matches()])
    return sorted(consecutive_matches, reverse=False)


def get_total_consecutive_matches(all_teams):
    total_consecutive_matches = 0
    for team in all_teams:
        total_consecutive_matches += team.get_total_consecutive_matches()


def get_end_of_first_round(all_teams):
    expected_matches = len(all_teams) * 2 - 2
    end_of_first_round = datetime(1970, 1, 1)
    for team in all_teams:
        last_match = team.get_date_of_match_nr(int(expected_matches / 2) - 1)  # should always be int
        if last_match > end_of_first_round:
            end_of_first_round = last_match
    return end_of_first_round
