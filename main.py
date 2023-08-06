import json
import random
import sys
from time import sleep
from art import *
from utils import convert_date_string_to_datetime, convert_date_string_list_to_datetime, check_for_consecutive_dates
from evaluate_plan import get_total_consecutive_matches, get_end_of_first_round, get_team_with_most_consecutive_matches,\
    get_team_with_most_uneven_distribution_matches, get_team_with_most_scheduled_please_dont_play_dates,\
    get_total_amount_please_dont_play_dates, calculate_score, match_plan_to_report
from team import Team
from datetime import datetime
import pandas
from tqdm import tqdm


def get_all_match_dates(teams, start_date):
    match_dates = []
    try:
        start_date = convert_date_string_to_datetime(start_date)
    except ValueError:
        # print(f"First Round start date not given or invalid ({start_date})")
        start_date = datetime(1970, 1, 1)
    for team in teams:
        available_dates = team.available_dates_home_matches
        for date in available_dates:
            if date not in match_dates and date >= start_date:
                match_dates.append(date)
    # print(f"Found {len(match_dates)} possible match dates")
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
            if match_date in available_home_match_dates and match_date not in blocked_dates:
                thisdict['home_match'].append(team)
        map_general.append(thisdict)
    return map_general


def create_match_plan(general_map, end_date_first_round, start_date_sec_round, consecutive_matches, shuffle_matches):
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

    def _shuffle_match_list():
        home_team_list = entry['home_match']
        away_team_list = entry['away_match']
        shuffle_part_home = round(len(home_team_list) * shuffle_matches[1])
        shuffle_part_away = round(len(away_team_list) * shuffle_matches[1])
        copy_home_team_list = home_team_list[:shuffle_part_home]
        copy_away_team_list = away_team_list[:shuffle_part_away]
        random.shuffle(copy_home_team_list)
        random.shuffle(copy_away_team_list)
        entry['home_match'][:shuffle_part_home] = copy_home_team_list
        entry['away_match'][:shuffle_part_away] = copy_away_team_list
        # print(f"Shuffle Part Home: {shuffle_part_home}")
        # print(f"Shuffle Part Away: {shuffle_part_away}")
        # print("")

    def _is_next_match_consecutive(curr_team):
        last_match_date = curr_team.get_last_match_date()
        if last_match_date is None:
            return False
        curr_match_date = entry['datetime']
        if check_for_consecutive_dates(last_match_date, curr_match_date):
            return True
        return False

    def _allow_consecutive_match():
        if consecutive_matches[0] == 0:
            return False
        rand_number = random.randint(0, 100)
        given_probability = consecutive_matches[1]
        if given_probability >= rand_number:
            # print(f"allow sunday match: True")
            return True
        # print(f"allow sunday match: False")
        return False

    def _debug_sort_output(headline_print_text):
        print("")
        print(f"----------- {headline_print_text} for {entry['datetime'].strftime('%d.%m.%Y')} -----------")
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
        _sort_teams_by_least_free_home_match_days()
        _sort_teams_by_least_total_match_days()
        # _debug_sort_output("Sorting Opponents")
        if shuffle_matches[0] == 1:
            _shuffle_match_list()
            # _debug_sort_output("Shuffle Opponents")
        # print(f"----- Matching Opponents for {entry['datetime'].strftime('%d.%m.%Y')} -----")

        for curr_home_team in entry['home_match']:
            home_team_already_matched = False
            if _is_next_match_consecutive(curr_home_team):
                if not _allow_consecutive_match():
                    continue  # Skip if next match would be a consecutive match which is not allowed
            for curr_away_team in entry['away_match']:
                if home_team_already_matched:
                    continue  # Skip if current home team already has a matched partner in this round
                if curr_home_team.team_name == curr_away_team.team_name:
                    continue  # Skip as home team can not play against itself
                if any(curr_away_team in sublist for sublist in thisdict['matches']):
                    continue  # Skip if other team already has a match in this round
                if any(curr_home_team in sublist for sublist in thisdict['matches']):
                    continue  # Skip if this team already has a match in this round
                if _is_next_match_consecutive(curr_away_team):
                    if not _allow_consecutive_match():
                        continue  # Skip if next match would be a consecutive match which is not allowed
                if first_round:
                    already_scheduled_opponents = curr_away_team.get_list_of_opponents()
                else:
                    already_scheduled_opponents = curr_away_team.get_list_of_opponents(home_or_away="A")
                if curr_home_team.team_name in already_scheduled_opponents:
                    continue  # Skip if there is already a match planned between both teams
                if not first_round:
                    try:
                        start_date_sec_round_date = convert_date_string_to_datetime(start_date_sec_round)
                    except ValueError:
                        # print(f"Second Round start date not given or invalid ({start_date_sec_round})")
                        start_date_sec_round_date = datetime(1970, 1, 1)
                    if entry['datetime'] < start_date_sec_round_date:
                        continue  # Don't Start second round until a given start date

                #  Modify team objects
                curr_home_team.add_home_match_date(entry['datetime'], curr_away_team.team_name)
                curr_away_team.add_away_match_date(entry['datetime'], curr_home_team.team_name)

                thisdict['matches'].append([curr_home_team, curr_away_team])
                home_team_already_matched = True

                # print(f"-> {curr_home_team.team_name} -vs- {curr_away_team.team_name}")
                # input("Press Enter to continue ...")

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
        # print("")
        if first_round:
            # print("====== FIRST ROUND DONE ======")
            pass
        else:
            # print("====== SECOND ROUND DONE ======")
            pass
        # print(f"Expected matches for first round: {expected_games}")
        # print(f"All Teams are scheduled for {expected_games} matches after first round.")
        # print(f"Last match for first round is scheduled on {last_home_match[1].strftime('%d.%m.%Y')}")
        # print(f"Least free home match days is {least_free_home_matches[1]} for team '{least_free_home_matches[0]}'"
        #       f" which already has scheduled {team.get_total_home_matches()} matches")
        return True

    map_final = []
    # print("")
    # print("====== MATCHING PHASE ======")
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
    #print("")
    return map_final


if __name__ == '__main__':
    tprint("Ligaman +")
    # Parse json file
    with open('teams.json') as file:
        file_contents = file.read()
    parsed_json = json.loads(file_contents)
    teams_json = parsed_json['teams']
    weight = parsed_json['weight']
    start_date_first_round = parsed_json['start_date_first_round']
    start_date_second_round = parsed_json['start_date_second_round']
    end_date_first_round = parsed_json['end_date_first_round']
    general_blocked_dates = parsed_json['general_blocked_dates']
    allow_consecutive_matches = [parsed_json['consecutive_matches']['allow'],
                                 parsed_json['consecutive_matches']['probability']]
    allow_shuffle_matches = [parsed_json['shuffle_matches']['allow'],
                             parsed_json['shuffle_matches']['shuffle_part']]
    iterations = parsed_json['max_iterations']
    if iterations == 0:
        iterations = sys.maxsize
    return_on_first_match_plan = parsed_json['return_on_first_match_plan']

    match_plan = []
    report_match_plan = pandas.DataFrame()
    report = ""
    score = 999999

    for i in tqdm(range(iterations)):
        try:
            # Create an instance for every team within the json file
            all_teams = [Team(team_line,
                              convert_date_string_list_to_datetime(teams_json[team_line]['available_dates_home_matches']),
                              convert_date_string_list_to_datetime(teams_json[team_line]['blocked_dates_matches']),
                              convert_date_string_list_to_datetime(teams_json[team_line]['please_dont_play_dates'])
                              )
                         for team_line in teams_json]
            # print(f"Created an instance for {len(all_teams)} Teams")

            # Determine all possible match days
            all_match_dates = get_all_match_dates(all_teams, start_date_first_round)

            # Map match dates to all teams
            map_all_combinations = map_general_match_dates_to_teams(all_teams, all_match_dates)

            # Create a match plan
            curr_match_plan = create_match_plan(map_all_combinations, end_date_first_round, start_date_second_round,
                                           allow_consecutive_matches, allow_shuffle_matches)

            curr_score, curr_report = calculate_score(weight, all_teams)

            if curr_score < score:
                score = curr_score
                match_plan = curr_match_plan
                report = curr_report
                report_match_plan = match_plan_to_report(match_plan, all_teams)
                # print(report_match_plan)
                print("")
                print(f"Spielplan gefunden nach Iteration {i + 1} mit score {score}")

           # sleep(5)
            if return_on_first_match_plan:
                break
        except Exception as e:
            # sleep(1)
            # print(f"Run {i}: Was not able to create a matching plan")
            pass

    if match_plan:
        print("")
        print(report_match_plan)
        print("")
        print(report)
    else:
        print("")
        print("=======================================")
        print("Was not able to create a match plan :-(")
    input("Press Enter to continue ...")





    # print(mtv_luebeck.available_dates_home_matches)
