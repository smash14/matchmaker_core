from datetime import datetime


class Team:

    def __init__(self, team_name, available_dates_home_matches, blocked_dates_matches):
        self.team_name = team_name
        self.available_dates_home_matches = available_dates_home_matches  # provided by team
        self.blocked_dates_matches = blocked_dates_matches  # provided by team
        self._dates_home_matches = []
        self._dates_away_matches = []
        self._dates_matches = []  # home and away matches combined [H/A, DATE, OPPONENT]
        self._total_matches = 0
        self._total_home_matches = 0
        self._total_away_matches = 0
        self._total_consecutive_matches = 0  # matches both on Saturday and Sunday

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

    def add_home_match_date(self, date, opponent):
        self._check_for_consecutive_match(date)
        self._dates_matches.append(["H", date, opponent])
        self._dates_home_matches.append([date, opponent])
        self._total_home_matches += 1
        self._total_matches += 1

    def add_away_match_date(self, date, opponent):
        self._check_for_consecutive_match(date)
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

    def get_total_home_matches(self):
        return self._total_home_matches

    def get_total_away_matches(self):
        return self._total_away_matches

    def get_total_matches(self):
        return self._total_matches

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

