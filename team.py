from datetime import datetime


class Team:

    def __init__(self, team_name, available_dates_home_matches, blocked_dates_matches, please_dont_play_dates):
        self.team_name = team_name
        self.available_dates_home_matches = available_dates_home_matches  # provided by team
        self.blocked_dates_matches = blocked_dates_matches  # provided by team
        self.please_dont_play_dates = please_dont_play_dates  # provided by team
        self._dates_home_matches = []
        self._dates_away_matches = []
        self._dates_matches = []  # home and away matches combined [H/A, DATE, OPPONENT]
        self._total_matches = 0
        self._total_home_matches = 0
        self._total_away_matches = 0
        self._total_consecutive_matches = 0  # matches both on Saturday and Sunday
        self._scheduled_please_dont_play_dates = 0  # if a game is scheduled on a day which is asked to be blcoked

    @property
    def team_name(self):
        return self._team_name

    @team_name.setter
    def team_name(self, value):
        self._team_name = value

    @property
    def available_dates_home_matches(self):
        return self._available_dates_home_matches

    @available_dates_home_matches.setter
    def available_dates_home_matches(self, value):
        # TODO: Proper error handling and sorting
        self._available_dates_home_matches = sorted(value)

    @property
    def blocked_dates_matches(self):
        return self._blocked_dates_matches

    @blocked_dates_matches.setter
    def blocked_dates_matches(self, value):
        # TODO: Proper error handling and sorting
        self._blocked_dates_matches = sorted(value)

    @property
    def please_dont_play_dates(self):
        return self._please_dont_play_dates

    @please_dont_play_dates.setter
    def please_dont_play_dates(self, value):
        # TODO: Proper error handling and sorting
        self._please_dont_play_dates = sorted(value)

    def add_home_match_date(self, date, opponent):
        self._check_for_consecutive_match(date)
        if date in self._please_dont_play_dates:
            self._scheduled_please_dont_play_dates += 1
        self._dates_matches.append(["H", date, opponent])
        self._dates_home_matches.append([date, opponent])
        self._total_home_matches += 1
        self._total_matches += 1

    def add_away_match_date(self, date, opponent):
        self._check_for_consecutive_match(date)
        if date in self._please_dont_play_dates:
            self._scheduled_please_dont_play_dates += 1
        self._dates_matches.append(["A", date, opponent])
        self._dates_away_matches.append([date, opponent])
        self._total_away_matches += 1
        self._total_matches += 1

    def _check_for_consecutive_match(self, date_new):
        try:
            last_match = self._dates_matches[-1][1]
            diff = date_new - last_match
            if diff.days <= 1:
                self._total_consecutive_matches += 1
        except IndexError:
            pass

    def get_total_consecutive_matches(self):
        return self._total_consecutive_matches

    def get_total_home_matches(self):
        return self._total_home_matches

    def get_total_away_matches(self):
        return self._total_away_matches

    def get_total_matches(self):
        return self._total_matches

    def get_total_scheduled_please_dont_play_dates(self):
        return self._scheduled_please_dont_play_dates

    def get_last_match_date(self):
        try:
            return self._dates_matches[-1][1]
        except IndexError:
            return None

    def get_free_home_match_days_after_date(self, current_date):
        """
        Returns number of free home match dates after a given date
        :param current_date: date to compare with
        :return: number of free home match dates after or equal to a given date
        """
        free_match_days = 0
        for date in self.available_dates_home_matches:
            if (date - current_date).days >= 0:
                free_match_days += 1
        # print(f"{self.team_name} hat noch {free_match_days} freie Heimspiele")
        return free_match_days

    def get_amount_of_matches_until_date(self, date):
        total_matches = [0, 0]  # H / A
        for match in self._dates_matches:
            if match[1] <= date:
                if match[0] == "H":
                    total_matches[0] += 1
                else:
                    total_matches[1] += 1
        return total_matches

    def get_list_of_opponents(self, home_or_away="all"):
        """
        Returns a list of scheduled matches with opponents
        :param home_or_away: returns all, only home matches or only away matches: 'all', 'H', or 'A'
        :return: list of scheduled matches with opponents name
        """
        opponents = []
        for match in self._dates_matches:
            if home_or_away == "all":
                opponents.append(match[2])
            elif home_or_away == match[0]:
                opponents.append(match[2])
        return opponents

    def get_date_of_match_nr(self, match_nr):
        if match_nr >= self._total_matches or match_nr < 0:  # Starting at 0 ?!
            return None
        return self._dates_matches[match_nr][1]

    def get_distribution_home_away_matches(self):
        """
        get the distribution of home and away matches. The return value represents the most uneven distribution
        :return: distribution factor of home and away matches
        """
        max_outlier = 0
        curr_outlier = 0
        for match in self._dates_matches:
            if match[0] == "H":
                curr_outlier += 1
                if abs(curr_outlier) > max_outlier:
                    max_outlier = abs(curr_outlier)
            if match[0] == "A":
                curr_outlier -= 1
                if abs(curr_outlier) > max_outlier:
                    max_outlier = abs(curr_outlier)
        return max_outlier

