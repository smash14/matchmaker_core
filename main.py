import json
from itertools import count

from utils import convert_date_string_to_datetime, convert_date_string_list_to_datetime
from team import Team
from datetime import datetime
import pandas


def get_all_match_dates(teams, start_date):
    match_dates = []
    start_date = convert_date_string_to_datetime(start_date)
    for team in teams:
        available_dates = team.available_dates_home_matches
        for date in available_dates:
            if date not in match_dates and date >= start_date:
                match_dates.append(date)
    print(f"Found {len(match_dates)} possible match dates")
    return sorted(match_dates)  # TODO: Sorting redundant?


def map_general_match_dates_to_teams(teams, all_match_dates):
    map_general = []
    for match_date in all_match_dates:
        thisdict = {'datetime': match_date,
                    'home_match': [],
                    'away_match': []}
        for team in teams:
            available_home_match_dates = team.available_dates_home_matches
            blocked_dates = team.blocked_dates_matches
            if match_date not in blocked_dates:
                thisdict['away_match'].append(team)
            if match_date in available_home_match_dates:
                thisdict['home_match'].append(team)
        map_general.append(thisdict)
    return map_general


def create_match_plan(general_map, start_date_sec_round):
    def _sort_teams_by_least_free_home_match_days():
        def __get_free_home_matches(elem):
            return elem.get_free_home_match_days_after_date(entry['datetime'])

        if (len(entry['home_match'])) > 1:
            entry['home_match'] = sorted(entry['home_match'], key=__get_free_home_matches)

    def _sort_teams_by_least_total_match_days():
        def __get_total_matches(elem):
            return elem.get_total_matches()

        if (len(entry['away_match'])) > 1:
            entry['away_match'] = sorted(entry['away_match'], key=__get_total_matches)

    def _debug_sort_output():
        data_home_team = []
        headers_data_home = ["Home Team", "Matches", "(H)", "(A)",
                             "Free Home Days", "(Total)"]
        headers_data_away = ["Away Team", "Matches", "(H)", "(A)"]
        data_away_team = []
        for curr_home_team in entry['home_match']:
            data_home_team.append([curr_home_team.team_name,
                                   curr_home_team.get_total_matches(),
                                   curr_home_team.get_total_home_matches(),
                                   curr_home_team.get_total_away_matches(),
                                   curr_home_team.get_free_home_match_days_after_date(entry['datetime']),
                                   len(curr_home_team.available_dates_home_matches)])
        for curr_away_team in entry['away_match']:
            if curr_away_team.team_name is not curr_home_team.team_name:
                data_away_team.append([curr_away_team.team_name,
                                       curr_away_team.get_total_matches(),
                                       curr_away_team.get_total_home_matches(),
                                       curr_away_team.get_total_away_matches()])

        if data_home_team:
            print("")
            print(pandas.DataFrame(data_home_team, columns=headers_data_home))
            print("")
        if data_away_team:
            print(pandas.DataFrame(data_away_team, columns=headers_data_away))
            print("")

    def _match_two_opponents(first_round=True):
        print("")
        print(f"----------- Sorting Opponents for {entry['datetime'].strftime('%d.%m.%Y')} -----------")
        _sort_teams_by_least_free_home_match_days()
        _sort_teams_by_least_total_match_days()
        _debug_sort_output()
        print(f"----- Matching Opponents for {entry['datetime'].strftime('%d.%m.%Y')} -----")

        for curr_home_team in entry['home_match']:
            for curr_away_team in entry['away_match']:
                if curr_home_team.team_name == curr_away_team.team_name:
                    continue  # Skip as home team can not play against itself
                if first_round:
                    already_scheduled_opponents = curr_away_team.get_list_of_opponents()
                else:
                    already_scheduled_opponents = curr_away_team.get_list_of_opponents(home_or_away="A")
                if curr_home_team.team_name in already_scheduled_opponents:
                    continue  # Skip if there is already a match planned between both teams
                if not first_round:
                    start_date_sec_round_date = convert_date_string_to_datetime(start_date_sec_round)
                    if entry['datetime'] < start_date_sec_round_date:
                        continue  # Start second round not until a given start date

                # remove home team from home match list and away match list
                entry['home_match'].remove(curr_home_team)
                entry['away_match'].remove(curr_home_team)

                # remove away team from away match and home match list, if needed
                entry['away_match'].remove(curr_away_team)
                if curr_away_team in entry['home_match']:
                    entry['home_match'].remove(curr_away_team)

                #  Modify team objects
                curr_home_team.add_home_match_date(entry['datetime'], curr_away_team.team_name)
                curr_away_team.add_away_match_date(entry['datetime'], curr_home_team.team_name)

                thisdict['matches'].append([curr_home_team, curr_away_team])

                print(f"-> {curr_home_team.team_name} -vs- {curr_away_team.team_name}")

    def _check_round_complete(first_round=True):
        if first_round:
            expected_games = len(all_teams) - 1
        else:
            expected_games = len(all_teams) * 2 - 2
        least_free_home_matches = ["", 999]
        last_home_match = ["", datetime(1970, 1, 1)]
        for team in all_teams:
            if team.get_total_matches() != expected_games:
                return False
            if team.get_last_match_date() > last_home_match[1]:
                last_home_match = [team.team_name, team.get_last_match_date()]
        for team in all_teams:
            if team.get_free_home_match_days_after_date(last_home_match[1]) < least_free_home_matches[1]:
                least_free_home_matches[1] = team.get_free_home_match_days_after_date(last_home_match[1])
                least_free_home_matches[0] = team.team_name
        print("")
        if first_round:
            print("====== FIRST ROUND DONE ======")
        else:
            print("====== SECOND ROUND DONE ======")
        print(f"Expected matches for first round: {expected_games}")
        print(f"All Teams are scheduled for {expected_games} matches after first round.")
        print(f"Last match for first round is scheduled on {last_home_match[1].strftime('%d.%m.%Y')}")
        print(f"Least free home match days is {least_free_home_matches[1]} for team '{least_free_home_matches[0]}'"
              f" which already has scheduled {team.get_total_home_matches()} matches")
        return True

    map_final = []
    print("")
    print("====== MATCHING PHASE ======")
    first_round_done = False
    second_round_done = False
    for entry in general_map:
        thisdict = {'datetime': entry['datetime'],
                    'matches': []}
        if not first_round_done:
            if _check_round_complete(first_round=True):
                first_round_done = True

        if not first_round_done:
            _match_two_opponents(first_round=True)
            map_final.append(thisdict)
        else:
            if _check_round_complete(first_round=False):
                second_round_done = True
                break
            _match_two_opponents(first_round=False)
            map_final.append(thisdict)
    if not second_round_done:
        raise Exception(f"Was not able to create a matching plan")
    print("")
    return map_final


if __name__ == '__main__':
    # Parse json file
    with open('teams.json') as file:
        file_contents = file.read()
    parsed_json = json.loads(file_contents)
    teams_json = parsed_json['teams']
    start_date_first_round = parsed_json['start_date_first_round']
    start_date_second_round = parsed_json['start_date_second_round']
    general_blocked_dates = parsed_json['general_blocked_dates']

    # Create an instance for every team within the json file
    all_teams = [Team(team_line,
                      convert_date_string_list_to_datetime(teams_json[team_line]['available_dates_home_matches']),
                      convert_date_string_list_to_datetime(teams_json[team_line]['blocked_dates_matches']))
                 for team_line in teams_json]
    print(f"Created an instance for {len(all_teams)} Teams")

    # Determine all possible match days
    all_match_dates = get_all_match_dates(all_teams, start_date_first_round)

    # Map match dates to all teams
    map_all_combinations = map_general_match_dates_to_teams(all_teams, all_match_dates)

    # Create a match plan
    match_plan = create_match_plan(map_all_combinations, start_date_second_round)

    print(match_plan)

    # print(mtv_luebeck.available_dates_home_matches)
