from datetime import datetime
import pandas

def get_consecutive_matches_list(all_teams):
    consecutive_matches = []
    for team in all_teams:
        consecutive_matches.append([team.team_name, team.get_total_consecutive_matches()])
    return sorted(consecutive_matches, reverse=False)


def get_total_consecutive_matches(all_teams):
    total_consecutive_matches = 0
    for team in all_teams:
        total_consecutive_matches += team.get_total_consecutive_matches()
    return total_consecutive_matches


def get_team_with_most_consecutive_matches(all_teams):
    most_matches = 0
    team_with_most_matches = None
    for team in all_teams:
        if team.get_total_consecutive_matches() > most_matches:
            most_matches = team.get_total_consecutive_matches()
            team_with_most_matches = team.team_name
    return team_with_most_matches, most_matches


def get_team_with_most_uneven_distribution_matches(all_teams):
    most_uneven_dist = 0
    team_most_uneven_dist = ""
    for team in all_teams:
        if team.get_distribution_home_away_matches() > most_uneven_dist:
            most_uneven_dist = team.get_distribution_home_away_matches()
            team_most_uneven_dist = team.team_name
    return team_most_uneven_dist, most_uneven_dist


def get_team_with_most_scheduled_please_dont_play_dates(all_teams):
    most_please_dont_play = 0
    team_please_dont_play = "-"
    for team in all_teams:
        if team.get_total_scheduled_please_dont_play_dates() > most_please_dont_play:
            most_please_dont_play = team.get_total_scheduled_please_dont_play_dates()
            team_please_dont_play = team.team_name
    return team_please_dont_play, most_please_dont_play


def get_please_dont_play_list(all_teams):
    pls_dont_play = []
    for team in all_teams:
        pls_dont_play.append([team.team_name,
                              team.get_total_scheduled_please_dont_play_dates()])
    return pls_dont_play


def get_total_amount_please_dont_play_dates(all_teams):
    total = 0
    for team in all_teams:
        total += team.get_total_scheduled_please_dont_play_dates()
    return total


def get_end_of_first_round(all_teams):
    expected_matches = len(all_teams) * 2 - 2
    end_of_first_round = datetime(1970, 1, 1)
    for team in all_teams:
        last_match = team.get_date_of_match_nr(int(expected_matches / 2) - 1)  # should always be int
        if last_match > end_of_first_round:
            end_of_first_round = last_match
    return end_of_first_round


def get_distribution_game_days(all_teams, match_plan):
    total_distribution = 0
    list_distirbution_per_day = []
    max_distribution = [0, datetime(1970, 1, 1)]
    for match_day in match_plan:
        distribution_per_team = []
        match_day_date = match_day['datetime']
        for team in all_teams:
            distribution_per_team.append([team.team_name, team.get_amount_of_matches_until_date(match_day_date)])
        list_distirbution_per_day.append(distribution_per_team)

    distribution_per_day = []
    for match_day in list_distirbution_per_day:
        max_distribution_per_day = 0
        min_distribution_per_day = 999  # TODO Proper init of lower end
        for team in match_day:
            curr_team_name = team[0]
            curr_distribution = sum(team[1])
            if curr_distribution > max_distribution_per_day:
                max_distribution_per_day = curr_distribution
            if curr_distribution < min_distribution_per_day:
                min_distribution_per_day = curr_distribution
        distribution_per_day.append(max_distribution_per_day - min_distribution_per_day)

    total_distribution = sum(distribution_per_day)
    max_distribution[0] = max(distribution_per_day)
    max_distribution_index = distribution_per_day.index(max(distribution_per_day))
    date_of_max_distribution = match_plan[max_distribution_index]['datetime']  # TODO this needs testing...
    max_distribution[1] = date_of_max_distribution

    return total_distribution, max_distribution


def calculate_score(weight, all_teams, match_plan):
    total_consec_matches = get_total_consecutive_matches(all_teams)
    most_consec_matches_team, most_consec_matches_team_amount = get_team_with_most_consecutive_matches(all_teams)
    most_uneven_home_away_team, most_uneven_home_away_amount = get_team_with_most_uneven_distribution_matches(all_teams)
    total_pls_dont_play_dates = get_total_amount_please_dont_play_dates(all_teams)
    most_pls_dont_play_team, most_pls_dont_play_amount = get_team_with_most_scheduled_please_dont_play_dates(all_teams)

    total_distribution_game_days, max_distribution_game_days = get_distribution_game_days(all_teams, match_plan)

    score = total_consec_matches * weight['amount_consecutive_matches'] + \
            most_uneven_home_away_amount * weight['distribution_home_away_matches'] + \
            total_pls_dont_play_dates * weight['amount_please_dont_play_dates'] + \
            max_distribution_game_days[0] * weight['distribution_game_days']

    # print(data_table)
    report = ""
    # print(f"Ende der Hinrunde: {end_of_first_round.strftime('%d.%m.%Y')}")
    report += f"Gesamtzahl der Doppelpunktspiel-Wochenenden (Spiele am Samstag und Sonntag): {get_total_consecutive_matches(all_teams)} (" \
              f"Max. ist {most_consec_matches_team} mit insgesamt {most_consec_matches_team_amount}).\n"

    report += f"Mannschaft mit der groessten Abweichung von Heim- und Auswaertsspielen: {most_uneven_home_away_team} " \
              f"mit {most_uneven_home_away_amount}.\n"

    report += f"Insgesamt {total_pls_dont_play_dates} unerwuenschte spiele. Die meisten von {most_pls_dont_play_team}" \
              f" mit {most_pls_dont_play_amount} unerwuenschten Spielen.\n"

    report += f"Die maximale Abweichung der Spieltage betraegt {max_distribution_game_days[0]} am" \
              f" {max_distribution_game_days[1].strftime('%d.%m.%Y')}\r\n\r\n"

    report += f"Score: {score} = ({total_consec_matches} * {weight['amount_consecutive_matches']}) + " \
              f"({most_uneven_home_away_amount} * {weight['distribution_home_away_matches']}) + " \
              f"({total_pls_dont_play_dates} * {weight['amount_please_dont_play_dates']}) + " \
              f"({max_distribution_game_days[0]} * {weight['distribution_game_days']})"

    return score, report


def match_plan_to_report(match_plan, all_teams):
    headers_data_match_plan = ["Datum", "Heimmannschaft", "(H)", "(A)", "", "Gastmannschaft", "(H)", "(A)"]
    # print("=================== FINAL MATCH PLAN ===================")
    end_of_first_round = get_end_of_first_round(all_teams)
    match_plan_to_print = []
    for match_day in match_plan:
        if match_day['matches']:
            match_date = match_day['datetime']
            # print(f"{match_date.strftime('%d.%m.%Y')}:")
            for match in match_day['matches']:
                match_plan_to_print.append([match_date.strftime('%d.%m.'),
                                            match[0].team_name,
                                            match[0].get_amount_of_matches_until_date(match_date)[0],
                                            match[0].get_amount_of_matches_until_date(match_date)[1],
                                            "-vs-",
                                            match[1].team_name,
                                            match[1].get_amount_of_matches_until_date(match_date)[0],
                                            match[1].get_amount_of_matches_until_date(match_date)[1]])
            if match_day['datetime'] == end_of_first_round:
                match_plan_to_print.append(["--", "--", "--", "--", "--", "--", "--", "--"])
    pandas.set_option('display.max_colwidth', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', None)
    data_table = pandas.DataFrame(match_plan_to_print, columns=headers_data_match_plan)
    #print(data_table)
    # print("")
    # print(f"Ende der Hinrunde: {end_of_first_round.strftime('%d.%m.%Y')}")
    # print("")
    return data_table
