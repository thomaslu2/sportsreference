import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import AWAY
from sportsipy.nfl.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsipy.nfl.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2017

BOXSCORE = '201802040nwe'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (YEAR, 7):
        return MockPQ(read_file('boxscores-7-2017.html'))
    if url == BOXSCORES_URL % (YEAR, 8):
        return MockPQ(read_file('boxscores-8-2017.html'))
    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNFLBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Sunday Feb 4, 2018',
            'time': '6:30pm',
            'datetime': datetime(2018, 2, 4, 18, 30),
            'stadium': 'U.S. Bank Stadium',
            'attendance': 67612,
            'duration': '3:46',
            'winner': AWAY,
            'winning_name': 'Philadelphia Eagles',
            'winning_abbr': 'PHI',
            'losing_name': 'New England Patriots',
            'losing_abbr': 'NWE',
            'won_toss': 'Patriots (deferred)',
            'weather': None,
            'vegas_line': 'New England Patriots -4.5',
            'surface': 'Sportturf',
            'roof': 'Dome',
            'over_under': '48.5 (over)',
            'away_points': 41,
            'away_first_downs': 25,
            'away_rush_attempts': 27,
            'away_rush_yards': 164,
            'away_rush_touchdowns': 1,
            'away_pass_completions': 29,
            'away_pass_attempts': 44,
            'away_pass_yards': 374,
            'away_pass_touchdowns': 4,
            'away_interceptions': 1,
            'away_times_sacked': 0,
            'away_yards_lost_from_sacks': 0,
            'away_net_pass_yards': 374,
            'away_total_yards': 538,
            'away_fumbles': 0,
            'away_fumbles_lost': 0,
            'away_turnovers': 1,
            'away_penalties': 6,
            'away_yards_from_penalties': 35,
            'away_third_down_conversions': 10,
            'away_third_down_attempts': 16,
            'away_fourth_down_conversions': 2,
            'away_fourth_down_attempts': 2,
            'away_time_of_possession': '34:04',
            'home_points': 33,
            'home_first_downs': 29,
            'home_rush_attempts': 22,
            'home_rush_yards': 113,
            'home_rush_touchdowns': 1,
            'home_pass_completions': 28,
            'home_pass_attempts': 49,
            'home_pass_yards': 505,
            'home_pass_touchdowns': 3,
            'home_interceptions': 0,
            'home_times_sacked': 1,
            'home_yards_lost_from_sacks': 5,
            'home_net_pass_yards': 500,
            'home_total_yards': 613,
            'home_fumbles': 1,
            'home_fumbles_lost': 1,
            'home_turnovers': 1,
            'home_penalties': 1,
            'home_yards_from_penalties': 5,
            'home_third_down_conversions': 5,
            'home_third_down_attempts': 10,
            'home_fourth_down_conversions': 1,
            'home_fourth_down_attempts': 2,
            'home_time_of_possession': '25:56',
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nfl_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
        assert getattr(self.boxscore, 'summary') == {
            'away': [9, 13, 7, 12],
            'home': [3, 9, 14, 7]
        }

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            if key == '_uri':
                continue
            assert value is None

    def test_nfl_boxscore_dataframe_returns_dataframe_of_all_values(self):
        df = pd.DataFrame([self.results], index=[BOXSCORE])

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, self.boxscore.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nfl_boxscore_players(self):
        boxscore = Boxscore(BOXSCORE)

        assert len(boxscore.home_players) == 27
        assert len(boxscore.away_players) == 29

        for player in boxscore.home_players:
            assert not player.dataframe.empty
        for player in boxscore.away_players:
            assert not player.dataframe.empty

    def test_nfl_boxscore_string_representation(self):
        expected = ('Boxscore for Philadelphia Eagles at New England Patriots '
                    '(Sunday Feb 4, 2018)')

        boxscore = Boxscore(BOXSCORE)

        assert boxscore.__repr__() == expected


class TestNFLBoxscores:
    def setup_method(self):
        self.expected = {
            '7-2017': [
                {'boxscore': '201710190rai',
                 'away_name': 'Kansas City Chiefs',
                 'away_abbr': 'kan',
                 'away_score': 30,
                 'home_name': 'Oakland Raiders',
                 'home_abbr': 'rai',
                 'home_score': 31,
                 'winning_name': 'Oakland Raiders',
                 'winning_abbr': 'rai',
                 'losing_name': 'Kansas City Chiefs',
                 'losing_abbr': 'kan'},
                {'boxscore': '201710220chi',
                 'away_name': 'Carolina Panthers',
                 'away_abbr': 'car',
                 'away_score': 3,
                 'home_name': 'Chicago Bears',
                 'home_abbr': 'chi',
                 'home_score': 17,
                 'winning_name': 'Chicago Bears',
                 'winning_abbr': 'chi',
                 'losing_name': 'Carolina Panthers',
                 'losing_abbr': 'car'},
                {'boxscore': '201710220buf',
                 'away_name': 'Tampa Bay Buccaneers',
                 'away_abbr': 'tam',
                 'away_score': 27,
                 'home_name': 'Buffalo Bills',
                 'home_abbr': 'buf',
                 'home_score': 30,
                 'winning_name': 'Buffalo Bills',
                 'winning_abbr': 'buf',
                 'losing_name': 'Tampa Bay Buccaneers',
                 'losing_abbr': 'tam'},
                {'boxscore': '201710220ram',
                 'away_name': 'Arizona Cardinals',
                 'away_abbr': 'crd',
                 'away_score': 0,
                 'home_name': 'Los Angeles Rams',
                 'home_abbr': 'ram',
                 'home_score': 33,
                 'winning_name': 'Los Angeles Rams',
                 'winning_abbr': 'ram',
                 'losing_name': 'Arizona Cardinals',
                 'losing_abbr': 'crd'},
                {'boxscore': '201710220min',
                 'away_name': 'Baltimore Ravens',
                 'away_abbr': 'rav',
                 'away_score': 16,
                 'home_name': 'Minnesota Vikings',
                 'home_abbr': 'min',
                 'home_score': 24,
                 'winning_name': 'Minnesota Vikings',
                 'winning_abbr': 'min',
                 'losing_name': 'Baltimore Ravens',
                 'losing_abbr': 'rav'},
                {'boxscore': '201710220mia',
                 'away_name': 'New York Jets',
                 'away_abbr': 'nyj',
                 'away_score': 28,
                 'home_name': 'Miami Dolphins',
                 'home_abbr': 'mia',
                 'home_score': 31,
                 'winning_name': 'Miami Dolphins',
                 'winning_abbr': 'mia',
                 'losing_name': 'New York Jets',
                 'losing_abbr': 'nyj'},
                {'boxscore': '201710220gnb',
                 'away_name': 'New Orleans Saints',
                 'away_abbr': 'nor',
                 'away_score': 26,
                 'home_name': 'Green Bay Packers',
                 'home_abbr': 'gnb',
                 'home_score': 17,
                 'winning_name': 'New Orleans Saints',
                 'winning_abbr': 'nor',
                 'losing_name': 'Green Bay Packers',
                 'losing_abbr': 'gnb'},
                {'boxscore': '201710220clt',
                 'away_name': 'Jacksonville Jaguars',
                 'away_abbr': 'jax',
                 'away_score': 27,
                 'home_name': 'Indianapolis Colts',
                 'home_abbr': 'clt',
                 'home_score': 0,
                 'winning_name': 'Jacksonville Jaguars',
                 'winning_abbr': 'jax',
                 'losing_name': 'Indianapolis Colts',
                 'losing_abbr': 'clt'},
                {'boxscore': '201710220cle',
                 'away_name': 'Tennessee Titans',
                 'away_abbr': 'oti',
                 'away_score': 12,
                 'home_name': 'Cleveland Browns',
                 'home_abbr': 'cle',
                 'home_score': 9,
                 'winning_name': 'Tennessee Titans',
                 'winning_abbr': 'oti',
                 'losing_name': 'Cleveland Browns',
                 'losing_abbr': 'cle'},
                {'boxscore': '201710220sfo',
                 'away_name': 'Dallas Cowboys',
                 'away_abbr': 'dal',
                 'away_score': 40,
                 'home_name': 'San Francisco 49ers',
                 'home_abbr': 'sfo',
                 'home_score': 10,
                 'winning_name': 'Dallas Cowboys',
                 'winning_abbr': 'dal',
                 'losing_name': 'San Francisco 49ers',
                 'losing_abbr': 'sfo'},
                {'boxscore': '201710220sdg',
                 'away_name': 'Denver Broncos',
                 'away_abbr': 'den',
                 'away_score': 0,
                 'home_name': 'Los Angeles Chargers',
                 'home_abbr': 'sdg',
                 'home_score': 21,
                 'winning_name': 'Los Angeles Chargers',
                 'winning_abbr': 'sdg',
                 'losing_name': 'Denver Broncos',
                 'losing_abbr': 'den'},
                {'boxscore': '201710220pit',
                 'away_name': 'Cincinnati Bengals',
                 'away_abbr': 'cin',
                 'away_score': 14,
                 'home_name': 'Pittsburgh Steelers',
                 'home_abbr': 'pit',
                 'home_score': 29,
                 'winning_name': 'Pittsburgh Steelers',
                 'winning_abbr': 'pit',
                 'losing_name': 'Cincinnati Bengals',
                 'losing_abbr': 'cin'},
                {'boxscore': '201710220nyg',
                 'away_name': 'Seattle Seahawks',
                 'away_abbr': 'sea',
                 'away_score': 24,
                 'home_name': 'New York Giants',
                 'home_abbr': 'nyg',
                 'home_score': 7,
                 'winning_name': 'Seattle Seahawks',
                 'winning_abbr': 'sea',
                 'losing_name': 'New York Giants',
                 'losing_abbr': 'nyg'},
                {'boxscore': '201710220nwe',
                 'away_name': 'Atlanta Falcons',
                 'away_abbr': 'atl',
                 'away_score': 7,
                 'home_name': 'New England Patriots',
                 'home_abbr': 'nwe',
                 'home_score': 23,
                 'winning_name': 'New England Patriots',
                 'winning_abbr': 'nwe',
                 'losing_name': 'Atlanta Falcons',
                 'losing_abbr': 'atl'},
                {'boxscore': '201710230phi',
                 'away_name': 'Washington Redskins',
                 'away_abbr': 'was',
                 'away_score': 24,
                 'home_name': 'Philadelphia Eagles',
                 'home_abbr': 'phi',
                 'home_score': 34,
                 'winning_name': 'Philadelphia Eagles',
                 'winning_abbr': 'phi',
                 'losing_name': 'Washington Redskins',
                 'losing_abbr': 'was'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(7, 2017).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(7, 2017, 5).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_weeks(self, *args, **kwargs):
        expected = {
            '7-2017': [
                {'boxscore': '201710190rai',
                 'away_name': 'Kansas City Chiefs',
                 'away_abbr': 'kan',
                 'away_score': 30,
                 'home_name': 'Oakland Raiders',
                 'home_abbr': 'rai',
                 'home_score': 31,
                 'winning_name': 'Oakland Raiders',
                 'winning_abbr': 'rai',
                 'losing_name': 'Kansas City Chiefs',
                 'losing_abbr': 'kan'},
                {'boxscore': '201710220chi',
                 'away_name': 'Carolina Panthers',
                 'away_abbr': 'car',
                 'away_score': 3,
                 'home_name': 'Chicago Bears',
                 'home_abbr': 'chi',
                 'home_score': 17,
                 'winning_name': 'Chicago Bears',
                 'winning_abbr': 'chi',
                 'losing_name': 'Carolina Panthers',
                 'losing_abbr': 'car'},
                {'boxscore': '201710220buf',
                 'away_name': 'Tampa Bay Buccaneers',
                 'away_abbr': 'tam',
                 'away_score': 27,
                 'home_name': 'Buffalo Bills',
                 'home_abbr': 'buf',
                 'home_score': 30,
                 'winning_name': 'Buffalo Bills',
                 'winning_abbr': 'buf',
                 'losing_name': 'Tampa Bay Buccaneers',
                 'losing_abbr': 'tam'},
                {'boxscore': '201710220ram',
                 'away_name': 'Arizona Cardinals',
                 'away_abbr': 'crd',
                 'away_score': 0,
                 'home_name': 'Los Angeles Rams',
                 'home_abbr': 'ram',
                 'home_score': 33,
                 'winning_name': 'Los Angeles Rams',
                 'winning_abbr': 'ram',
                 'losing_name': 'Arizona Cardinals',
                 'losing_abbr': 'crd'},
                {'boxscore': '201710220min',
                 'away_name': 'Baltimore Ravens',
                 'away_abbr': 'rav',
                 'away_score': 16,
                 'home_name': 'Minnesota Vikings',
                 'home_abbr': 'min',
                 'home_score': 24,
                 'winning_name': 'Minnesota Vikings',
                 'winning_abbr': 'min',
                 'losing_name': 'Baltimore Ravens',
                 'losing_abbr': 'rav'},
                {'boxscore': '201710220mia',
                 'away_name': 'New York Jets',
                 'away_abbr': 'nyj',
                 'away_score': 28,
                 'home_name': 'Miami Dolphins',
                 'home_abbr': 'mia',
                 'home_score': 31,
                 'winning_name': 'Miami Dolphins',
                 'winning_abbr': 'mia',
                 'losing_name': 'New York Jets',
                 'losing_abbr': 'nyj'},
                {'boxscore': '201710220gnb',
                 'away_name': 'New Orleans Saints',
                 'away_abbr': 'nor',
                 'away_score': 26,
                 'home_name': 'Green Bay Packers',
                 'home_abbr': 'gnb',
                 'home_score': 17,
                 'winning_name': 'New Orleans Saints',
                 'winning_abbr': 'nor',
                 'losing_name': 'Green Bay Packers',
                 'losing_abbr': 'gnb'},
                {'boxscore': '201710220clt',
                 'away_name': 'Jacksonville Jaguars',
                 'away_abbr': 'jax',
                 'away_score': 27,
                 'home_name': 'Indianapolis Colts',
                 'home_abbr': 'clt',
                 'home_score': 0,
                 'winning_name': 'Jacksonville Jaguars',
                 'winning_abbr': 'jax',
                 'losing_name': 'Indianapolis Colts',
                 'losing_abbr': 'clt'},
                {'boxscore': '201710220cle',
                 'away_name': 'Tennessee Titans',
                 'away_abbr': 'oti',
                 'away_score': 12,
                 'home_name': 'Cleveland Browns',
                 'home_abbr': 'cle',
                 'home_score': 9,
                 'winning_name': 'Tennessee Titans',
                 'winning_abbr': 'oti',
                 'losing_name': 'Cleveland Browns',
                 'losing_abbr': 'cle'},
                {'boxscore': '201710220sfo',
                 'away_name': 'Dallas Cowboys',
                 'away_abbr': 'dal',
                 'away_score': 40,
                 'home_name': 'San Francisco 49ers',
                 'home_abbr': 'sfo',
                 'home_score': 10,
                 'winning_name': 'Dallas Cowboys',
                 'winning_abbr': 'dal',
                 'losing_name': 'San Francisco 49ers',
                 'losing_abbr': 'sfo'},
                {'boxscore': '201710220sdg',
                 'away_name': 'Denver Broncos',
                 'away_abbr': 'den',
                 'away_score': 0,
                 'home_name': 'Los Angeles Chargers',
                 'home_abbr': 'sdg',
                 'home_score': 21,
                 'winning_name': 'Los Angeles Chargers',
                 'winning_abbr': 'sdg',
                 'losing_name': 'Denver Broncos',
                 'losing_abbr': 'den'},
                {'boxscore': '201710220pit',
                 'away_name': 'Cincinnati Bengals',
                 'away_abbr': 'cin',
                 'away_score': 14,
                 'home_name': 'Pittsburgh Steelers',
                 'home_abbr': 'pit',
                 'home_score': 29,
                 'winning_name': 'Pittsburgh Steelers',
                 'winning_abbr': 'pit',
                 'losing_name': 'Cincinnati Bengals',
                 'losing_abbr': 'cin'},
                {'boxscore': '201710220nyg',
                 'away_name': 'Seattle Seahawks',
                 'away_abbr': 'sea',
                 'away_score': 24,
                 'home_name': 'New York Giants',
                 'home_abbr': 'nyg',
                 'home_score': 7,
                 'winning_name': 'Seattle Seahawks',
                 'winning_abbr': 'sea',
                 'losing_name': 'New York Giants',
                 'losing_abbr': 'nyg'},
                {'boxscore': '201710220nwe',
                 'away_name': 'Atlanta Falcons',
                 'away_abbr': 'atl',
                 'away_score': 7,
                 'home_name': 'New England Patriots',
                 'home_abbr': 'nwe',
                 'home_score': 23,
                 'winning_name': 'New England Patriots',
                 'winning_abbr': 'nwe',
                 'losing_name': 'Atlanta Falcons',
                 'losing_abbr': 'atl'},
                {'boxscore': '201710230phi',
                 'away_name': 'Washington Redskins',
                 'away_abbr': 'was',
                 'away_score': 24,
                 'home_name': 'Philadelphia Eagles',
                 'home_abbr': 'phi',
                 'home_score': 34,
                 'winning_name': 'Philadelphia Eagles',
                 'winning_abbr': 'phi',
                 'losing_name': 'Washington Redskins',
                 'losing_abbr': 'was'}
            ],
            '8-2017': [
                {'boxscore': '201710260rav',
                 'away_name': 'Miami Dolphins',
                 'away_abbr': 'mia',
                 'away_score': 0,
                 'home_name': 'Baltimore Ravens',
                 'home_abbr': 'rav',
                 'home_score': 40,
                 'winning_name': 'Baltimore Ravens',
                 'winning_abbr': 'rav',
                 'losing_name': 'Miami Dolphins',
                 'losing_abbr': 'mia'},
                {'boxscore': '201710290cle',
                 'away_name': 'Minnesota Vikings',
                 'away_abbr': 'min',
                 'away_score': 33,
                 'home_name': 'Cleveland Browns',
                 'home_abbr': 'cle',
                 'home_score': 16,
                 'winning_name': 'Minnesota Vikings',
                 'winning_abbr': 'min',
                 'losing_name': 'Cleveland Browns',
                 'losing_abbr': 'cle'},
                {'boxscore': '201710290buf',
                 'away_name': 'Oakland Raiders',
                 'away_abbr': 'rai',
                 'away_score': 14,
                 'home_name': 'Buffalo Bills',
                 'home_abbr': 'buf',
                 'home_score': 34,
                 'winning_name': 'Buffalo Bills',
                 'winning_abbr': 'buf',
                 'losing_name': 'Oakland Raiders',
                 'losing_abbr': 'rai'},
                {'boxscore': '201710290tam',
                 'away_name': 'Carolina Panthers',
                 'away_abbr': 'car',
                 'away_score': 17,
                 'home_name': 'Tampa Bay Buccaneers',
                 'home_abbr': 'tam',
                 'home_score': 3,
                 'winning_name': 'Carolina Panthers',
                 'winning_abbr': 'car',
                 'losing_name': 'Tampa Bay Buccaneers',
                 'losing_abbr': 'tam'},
                {'boxscore': '201710290phi',
                 'away_name': 'San Francisco 49ers',
                 'away_abbr': 'sfo',
                 'away_score': 10,
                 'home_name': 'Philadelphia Eagles',
                 'home_abbr': 'phi',
                 'home_score': 33,
                 'winning_name': 'Philadelphia Eagles',
                 'winning_abbr': 'phi',
                 'losing_name': 'San Francisco 49ers',
                 'losing_abbr': 'sfo'},
                {'boxscore': '201710290nyj',
                 'away_name': 'Atlanta Falcons',
                 'away_abbr': 'atl',
                 'away_score': 25,
                 'home_name': 'New York Jets',
                 'home_abbr': 'nyj',
                 'home_score': 20,
                 'winning_name': 'Atlanta Falcons',
                 'winning_abbr': 'atl',
                 'losing_name': 'New York Jets',
                 'losing_abbr': 'nyj'},
                {'boxscore': '201710290nwe',
                 'away_name': 'Los Angeles Chargers',
                 'away_abbr': 'sdg',
                 'away_score': 13,
                 'home_name': 'New England Patriots',
                 'home_abbr': 'nwe',
                 'home_score': 21,
                 'winning_name': 'New England Patriots',
                 'winning_abbr': 'nwe',
                 'losing_name': 'Los Angeles Chargers',
                 'losing_abbr': 'sdg'},
                {'boxscore': '201710290nor',
                 'away_name': 'Chicago Bears',
                 'away_abbr': 'chi',
                 'away_score': 12,
                 'home_name': 'New Orleans Saints',
                 'home_abbr': 'nor',
                 'home_score': 20,
                 'winning_name': 'New Orleans Saints',
                 'winning_abbr': 'nor',
                 'losing_name': 'Chicago Bears',
                 'losing_abbr': 'chi'},
                {'boxscore': '201710290cin',
                 'away_name': 'Indianapolis Colts',
                 'away_abbr': 'clt',
                 'away_score': 23,
                 'home_name': 'Cincinnati Bengals',
                 'home_abbr': 'cin',
                 'home_score': 24,
                 'winning_name': 'Cincinnati Bengals',
                 'winning_abbr': 'cin',
                 'losing_name': 'Indianapolis Colts',
                 'losing_abbr': 'clt'},
                {'boxscore': '201710290sea',
                 'away_name': 'Houston Texans',
                 'away_abbr': 'htx',
                 'away_score': 38,
                 'home_name': 'Seattle Seahawks',
                 'home_abbr': 'sea',
                 'home_score': 41,
                 'winning_name': 'Seattle Seahawks',
                 'winning_abbr': 'sea',
                 'losing_name': 'Houston Texans',
                 'losing_abbr': 'htx'},
                {'boxscore': '201710290was',
                 'away_name': 'Dallas Cowboys',
                 'away_abbr': 'dal',
                 'away_score': 33,
                 'home_name': 'Washington Redskins',
                 'home_abbr': 'was',
                 'home_score': 19,
                 'winning_name': 'Dallas Cowboys',
                 'winning_abbr': 'dal',
                 'losing_name': 'Washington Redskins',
                 'losing_abbr': 'was'},
                {'boxscore': '201710290det',
                 'away_name': 'Pittsburgh Steelers',
                 'away_abbr': 'pit',
                 'away_score': 20,
                 'home_name': 'Detroit Lions',
                 'home_abbr': 'det',
                 'home_score': 15,
                 'winning_name': 'Pittsburgh Steelers',
                 'winning_abbr': 'pit',
                 'losing_name': 'Detroit Lions',
                 'losing_abbr': 'det'},
                {'boxscore': '201710300kan',
                 'away_name': 'Denver Broncos',
                 'away_abbr': 'den',
                 'away_score': 19,
                 'home_name': 'Kansas City Chiefs',
                 'home_abbr': 'kan',
                 'home_score': 29,
                 'winning_name': 'Kansas City Chiefs',
                 'winning_abbr': 'kan',
                 'losing_name': 'Denver Broncos',
                 'losing_abbr': 'den'}
            ]
        }
        result = Boxscores(7, 2017, 8).games

        assert result == expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(7, 2017)

        assert result.__repr__() == 'NFL games for week 7'

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation_multi_week(self, *args,
                                                               **kwargs):
        result = Boxscores(7, 2017, 8)

        assert result.__repr__() == 'NFL games for weeks 7, 8'
