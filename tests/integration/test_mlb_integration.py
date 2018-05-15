import os
from flexmock import flexmock
from mocker import Mocker, MockerTestCase
from pyquery import PyQuery
from sportsreference import utils
from sportsreference.mlb.constants import STANDINGS_URL, TEAM_STATS_URL
from sportsreference.mlb.teams import Teams


MONTH = 4
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb_stats', filename)
    return open('%s' % filepath, 'r').read()


class MockPQ:
    def __init__(self, html_contents):
        self.html_contents = html_contents

    def __call__(self, div):
        if div == 'div#all_teams_standard_batting':
            return read_file('%s_batting.html' % YEAR)
        elif div == 'div#all_teams_standard_pitching':
            return read_file('%s_pitching.html' % YEAR)
        else:
            return read_file('%s_overall.html' % YEAR)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestMLBIntegration(MockerTestCase):
    def setUp(self):
        self.results = {
            'rank': 3,
            'abbreviation': 'HOU',
            'name': 'Houston Astros',
            'league': 'AL',
            'games': 162,
            'wins': 101,
            'losses': 61,
            'win_percentage': .624,
            'streak': None,
            'runs': 5.5,
            'runs_against': 4.3,
            'run_difference': 1.2,
            'strength_of_schedule': 0.0,
            'simple_rating_system': 1.2,
            'pythagorean_win_loss': '99-63',
            'luck': 2,
            'interleague_record': '15-5',
            'home_record': '48-33',
            'home_wins': 48,
            'home_losses': 33,
            'away_record': '53-28',
            'away_wins': 53,
            'away_losses': 28,
            'extra_inning_record': '4-4',
            'extra_inning_wins': 4,
            'extra_inning_losses': 4,
            'single_run_record': '19-13',
            'single_run_wins': 19,
            'single_run_losses': 13,
            'record_vs_right_handed_pitchers': '80-37',
            'wins_vs_right_handed_pitchers': 80,
            'losses_vs_right_handed_pitchers': 37,
            'record_vs_left_handed_pitchers': '21-24',
            'wins_vs_left_handed_pitchers': 21,
            'losses_vs_left_handed_pitchers': 24,
            'record_vs_teams_over_500': '18-15',
            'wins_vs_teams_over_500': 18,
            'losses_vs_teams_over_500': 15,
            'record_vs_teams_under_500': '83-46',
            'wins_vs_teams_under_500': 83,
            'losses_vs_teams_under_500': 46,
            'last_ten_games_record': None,
            'wins_last_ten_games': None,
            'losses_last_ten_games': None,
            'last_twenty_games_record': None,
            'wins_last_twenty_games': None,
            'losses_last_twenty_games': None,
            'last_thirty_games_record': None,
            'wins_last_thirty_games': None,
            'losses_last_thirty_games': None,
            'number_players_used': 46,
            'average_batter_age': 28.8,
            'plate_appearances': 6271,
            'at_bats': 5611,
            'total_runs': 896,
            'hits': 1581,
            'doubles': 346,
            'triples': 20,
            'home_runs': 238,
            'runs_batted_in': 854,
            'stolen_bases': 98,
            'times_caught_stealing': 42,
            'bases_on_balls': 509,
            'times_struck_out': 1087,
            'batting_average': .282,
            'on_base_percentage': .346,
            'slugging_percentage': .478,
            'on_base_plus_slugging_percentage': .823,
            'on_base_plus_slugging_percentage_plus': 127,
            'total_bases': 2681,
            'grounded_into_double_plays': 139,
            'times_hit_by_pitch': 70,
            'sacrifice_hits': 11,
            'sacrifice_flies': 61,
            'intentional_bases_on_balls': 27,
            'runners_left_on_base': 1094,
            'number_of_pitchers': 27,
            'average_pitcher_age': 28.5,
            'runs_allowed_per_game': 4.32,
            'earned_runs_against': 4.12,
            'games_finished': 161,
            'complete_games': 1,
            'shutouts': 9,
            'complete_game_shutouts': 0,
            'saves': 45,
            'innings_pitched': 1446.0,
            'hits_allowed': 1314,
            'home_runs_against': 192,
            'bases_on_walks_given': 522,
            'strikeouts': 1593,
            'hit_pitcher': 70,
            'balks': 4,
            'wild_pitches': 86,
            'batters_faced': 6111,
            'earned_runs_against_plus': 96,
            'fielding_independent_pitching': 3.91,
            'whip': 1.270,
            'hits_per_nine_innings': 8.2,
            'home_runs_per_nine_innings': 1.2,
            'bases_on_walks_given_per_nine_innings': 3.2,
            'strikeouts_per_nine_innings': 9.9,
            'strikeouts_per_base_on_balls': 3.05,
            'opposing_runners_left_on_base': 1073
        }
        self.abbreviations = [
            'NYY', 'BOS', 'ATL', 'LAA', 'HOU', 'MIL', 'PHI', 'ARI', 'STL',
            'PIT', 'SEA', 'WSN', 'CHC', 'COL', 'NYM', 'TOR', 'CLE', 'SFG',
            'OAK', 'MIN', 'DET', 'TBR', 'LAD', 'TEX', 'SDP', 'MIA', 'CIN',
            'KCR', 'BAL', 'CHW'
        ]
        html_contents = read_file('%s-standings.html' % YEAR)
        team_stats = read_file('%s.html' % YEAR)

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        mock_pyquery = self.mocker.replace(PyQuery)
        mock_pyquery(STANDINGS_URL % YEAR)
        self.mocker.result(MockPQ(html_contents))
        mock_pyquery(TEAM_STATS_URL % YEAR)
        self.mocker.result(MockPQ(team_stats))
        self.mocker.replay()

        self.teams = Teams()

    def test_mlb_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_mlb_integration_returns_correct_attributes_for_team(self):
        houston = self.teams('HOU')

        for attribute, value in self.results.items():
            assert getattr(houston, attribute) == value

    def test_mlb_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations