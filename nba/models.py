# -*- coding: utf-8 -*-

from django.db import models

# Maps DK player full names to NBA.com full names
DK_NBA_PLAYER_NAME_MAP = {
    'Denis Schroder': 'Dennis Schroder',
    u'José Calderón': 'Jose Calderon',
    'Chuck Hayes': 'Charles Hayes',
    u'Manu Ginóbili': 'Manu Ginobili',
    'J.J. Barea': 'Jose Juan Barea',
    u'Cristiano Felício': 'Cristiano Felicio',
    u'Kevin Martín': 'Kevin Martin',
    u'André Miller': 'Andre Miller',
    u'Danté Exum': 'Dante Exum',
}

# Create your models here.

class Team(models.Model):
    NBA_TEAM_MAP = {
        'SIXERS': '76ers',
        'CAVS': 'Cavaliers',
        'GRIZZ': 'Grizzlies',
        'MAVS': 'Mavericks',
        'BLAZERS': 'Trail Blazers',
    }

    # From NBA.com, received as an integer
    nba_id = models.CharField(max_length=15, null=True, blank=True, unique=True)
    name = models.CharField(max_length=50, unique=True)
    abbr = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return '%s %s' % (self.city, self.name)

    @classmethod
    def get_by_name(cls, s):
        s = s.upper()
        teams = {
            (t.name.upper(), t.city.upper(), t.abbr.upper()): t
            for t in Team.objects.all()
        }
        for k, team in teams.iteritems():
            name, city, abbr = k
            if name in s or s == city or s == abbr:
                return team
            if city in s and name in s:
                return team
        if s in cls.NBA_TEAM_MAP:
            return Team.objects.get(name=cls.NBA_TEAM_MAP[s])
        print '[WARNING/Team] Could not resolve team name: %s' % s
        return None

    def __unicode__(self):
        return self.full_name

class Player(models.Model):
    # From NBA.com, received as an integer
    nba_id = models.CharField(max_length=15, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    team = models.ForeignKey(Team, related_name='players', null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    dk_position = models.CharField(max_length=2, null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    weight = models.PositiveIntegerField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    school = models.CharField(max_length=80, null=True, blank=True)
    country = models.CharField(max_length=80, null=True, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    # Not necessarily end - start due to breaks/injuries
    seasons = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return ' '.join([n for n in [self.first_name, self.last_name] if n])

    @classmethod
    def __get_first_last_name(cls, name):
        stripped = name.replace('.', '').split(' ')
        first_name = stripped[0]
        last_name = ' '.join(stripped[1:])
        return (first_name, last_name)

    @classmethod
    def filter_by_name(cls, name):
        return [p for p in cls.objects.all() if p.full_name == name]

    @classmethod
    def get_by_name_slow(cls, name):
        def name_in_dict(int_name, arg_name):
            return (arg_name in DK_NBA_PLAYER_NAME_MAP
                    and int_name == DK_NBA_PLAYER_NAME_MAP[arg_name])

        def name_equals(int_name, arg_name):
            int_new = int_name.replace('.', '').lower().strip()
            arg_new = arg_name.replace('.', '').lower().strip()
            return (int_new == arg_new
                    or int_new in arg_new
                    or arg_new in int_new)

        def name_contains(int_name, arg_name):
            int_first, int_last = cls.__get_first_last_name(int_name)
            arg_first, arg_last = cls.__get_first_last_name(arg_name)
            return ((int_first in arg_first or arg_first in int_first)
                    and (int_last in arg_last or arg_last in int_last))

        try:
            name = unicode(name, encoding='utf-8')
        except TypeError:
            pass
        # Order matters. name_in_dict should catch UnicodeDecodeErrors
        players = [p for p in cls.objects.all()
                   if name_in_dict(p.full_name, name)
                   or name_equals(p.full_name, name)
                   or name_contains(p.full_name, name)]
        if len(players) == 1:
            return players[0]
        elif len(players) == 0:
            print 'Player %s does not exist' % name
            raise cls.DoesNotExist
        else:
            print ('Multiple players named %s found (%s)'
                   % (name, ', '.join(players)))
            raise cls.MultipleObjectsReturned

    @classmethod
    def get_by_name(cls, name):
        first_name, last_name = cls.__get_first_last_name(name)
        try:
            return cls.objects.get(first_name__iexact=first_name,
                                   last_name__iexact=last_name)
        except cls.DoesNotExist, cls.MultipleObjectsReturned:
            try:
                return cls.objects.get(first_name__contains=first_name,
                                       last_name__contains=last_name)
            except cls.DoesNotExist, cls.MultipleObjectsReturned:
                return cls.get_by_name_slow(name)

    def get_dkpoints(self, date):
        try:
            return GameStats.objects.get(game__date=date, player=self).dk_points
        except GameStats.DoesNotExist:
            return 0.0

    def get_stat(self, date, stat):
        """
        @param date [datetime.date]: Date to query
        @param stats [str]: Stat name to query
        @return [int/float]: Stat value
        """
        try:
            gs = GameStats.objects.get(game__date=date, player=self)
            return getattr(gs, stat)
        except GameStats.DoesNotExist:
            return 0.0

    def get_stats(self, date, *stats):
        """
        @param date [datetime.date]: Date to query
        @param *stats [tuple]: List of stat names
        @return [dict]: { [stat name]: [stat value] }
        e.g. player_obj.get_stats(datetime.date(2015, 1, 1), 'min', 'pts')
        >> { 'min': 34, 'pts': 18 }
        """
        try:
            gs = GameStats.objects.get(game__date=date, player=self)
            return { stat: getattr(gs, stat) for stat in stats }
        except GameStats.DoesNotExist:
            return { stat: 0.0 for stat in stats }

    def get_salary(self, date):
        try:
            return DKSalary.objects.get(player=self, date=date).salary
        except DKSalary.DoesNotExist:
            return None

    def __unicode__(self):
        return self.full_name

class Game(models.Model):
    # From NBA.com
    nba_id = models.CharField(max_length=15, null=True, blank=True, unique=True)
    home_team = models.ForeignKey(Team, related_name='home_games')
    away_team = models.ForeignKey(Team, related_name='away_games')
    date = models.DateField()
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)
    winner = models.ForeignKey(Team, null=True, blank=True, related_name='won_games')
    season_id = models.CharField(max_length=15, null=True, blank=True)
    season = models.CharField(max_length=9, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('home_team', 'away_team', 'date')

    def __unicode__(self):
        return ('%s @ %s %s'
                % (self.away_team.abbr, self.home_team.abbr, self.date))

class GameStats(models.Model):
    """
    Stat abbreviations:
    min: Minutes played
    fgm/fga: Field goals made/attempted
    fg3m/fg3a: Three pointers made/attempted
    ftm/fta: Free throws made/attempted
    oreb/dreb: Offensive/defensive rebounds
    reb/ast/stl/blk/tov: Rebounds, assists, steals, blocks, turnovers
    pf: Personal fouls
    pts: Points
    plus_minus: Plus/minus
    """
    game = models.ForeignKey(Game, related_name='game_stats')
    player = models.ForeignKey(Player, related_name='game_stats')
    min = models.PositiveIntegerField(null=True, blank=True)
    fgm = models.PositiveIntegerField(null=True, blank=True)
    fga = models.PositiveIntegerField(null=True, blank=True)
    fg3m = models.PositiveIntegerField(null=True, blank=True)
    fg3a = models.PositiveIntegerField(null=True, blank=True)
    ftm = models.PositiveIntegerField(null=True, blank=True)
    fta = models.PositiveIntegerField(null=True, blank=True)
    oreb = models.PositiveIntegerField(null=True, blank=True)
    dreb = models.PositiveIntegerField(null=True, blank=True)
    reb = models.PositiveIntegerField(null=True, blank=True)
    ast = models.PositiveIntegerField(null=True, blank=True)
    stl = models.PositiveIntegerField(null=True, blank=True)
    blk = models.PositiveIntegerField(null=True, blank=True)
    tov = models.PositiveIntegerField(null=True, blank=True)
    pf = models.PositiveIntegerField(null=True, blank=True)
    pts = models.PositiveIntegerField(null=True, blank=True)
    plus_minus = models.IntegerField(null=True, blank=True)

    @property
    def fg_pct(self):
        return float(self.fgm) / self.fga

    @property
    def fg3_pct(self):
        return float(self.fg3m) / self.fg3a

    @property
    def ft_pct(self):
        return float(self.ftm) / self.fta

    @property
    def dk_points(self):
        """
        Point = +1 PT
        Made 3pt. shot = +0.5 PTs
        Rebound = +1.25 PTs
        Assist = +1.5 PTs
        Steal = +2 PTs
        Block = +2 PTs
        Turnover = -0.5 PTs
        Double-Double = +1.5PTs
            (MAX 1 PER PLAYER: Points, Rebounds, Assists, Blocks, Steals)
        Triple-Double = +3PTs
            (MAX 1 PER PLAYER: Points, Rebounds, Assists, Blocks, Steals)
        """
        doubles = [
            x for x in [self.pts, self.reb, self.ast, self.blk, self.stl]
            if x >= 10
        ]
        points = (1.0 * self.pts + 0.5 * self.fg3m + 1.25 * self.reb
                  + 1.5 * self.ast + 2.0 * self.stl + 2.0 * self.blk
                  + -0.5 * self.tov)
        points += 1.5 if len(doubles) >= 2 else 0.0
        points += 3.0 if len(doubles) >= 3 else 0.0
        return points

    class Meta:
        unique_together = ('game', 'player')

    def __unicode__(self):
        return ('%s %s' % (unicode(self.player), unicode(self.game)))

class Injury(models.Model):
    player = models.ForeignKey(Player, related_name='injuries')
    status = models.CharField(max_length=50)
    date = models.DateField()
    comment = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        unique_together = ('player', 'date', 'comment')

    def __unicode__(self):
        return '%s %s %s' % (unicode(self.player), self.status, self.date)

class DKContest(models.Model):
    dk_id = models.CharField(max_length=15, unique=True)
    date = models.DateField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    total_prizes = models.DecimalField(max_digits=18, decimal_places=2,
                                       null=True, blank=True)
    entries = models.PositiveIntegerField(null=True, blank=True)
    entry_fee = models.FloatField(null=True, blank=True)
    positions_paid = models.PositiveIntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.name, self.date)

class DKContestPayout(models.Model):
    contest = models.ForeignKey(DKContest, related_name='payouts')
    upper_rank = models.PositiveIntegerField()
    lower_rank = models.PositiveIntegerField()
    payout = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        unique_together = ('contest', 'upper_rank', 'lower_rank')

    def __unicode__(self):
        return ('%s (%s - %s: %s)' %
                (self.contest, self.upper_rank, self.lower_rank, self.payout))

class DKResult(models.Model):
    contest = models.ForeignKey(DKContest, related_name='results')
    dk_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    rank = models.PositiveIntegerField()
    points = models.FloatField()
    pg = models.ForeignKey(Player, related_name='dk_pg_results')
    sg = models.ForeignKey(Player, related_name='dk_sg_results')
    sf = models.ForeignKey(Player, related_name='dk_sf_results')
    pf = models.ForeignKey(Player, related_name='dk_pf_results')
    c = models.ForeignKey(Player, related_name='dk_c_results')
    g = models.ForeignKey(Player, related_name='dk_g_results')
    f = models.ForeignKey(Player, related_name='dk_f_results')
    util = models.ForeignKey(Player, related_name='dk_util_results')

    def get_lineup(self):
        return [self.pg, self.sg, self.sf, self.pf, self.c, self.g, self.f,
                self.util]

    def get_lineup_dict(self):
        return {
            'PG': self.pg, 'SG': self.sg, 'SF': self.sf, 'PF': self.pf,
            'C': self.c, 'G': self.g, 'F': self.f, 'UTIL': self.util
        }

    def __unicode__(self):
        return '%s %s' % (unicode(self.contest), unicode(self.rank))

class DKSalary(models.Model):
    player = models.ForeignKey(Player, related_name='dk_salaries')
    date = models.DateField(null=True, blank=True)
    salary = models.PositiveIntegerField()

    class Meta:
        unique_together = ('player', 'date')

    def __unicode__(self):
        return '%s %s %s' % (self.player, self.date, self.salary)
