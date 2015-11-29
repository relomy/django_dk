from django.db import models

# Create your models here.

class Team(models.Model):
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
    game_id = models.ForeignKey(Game, related_name='game_stats')
    player_id = models.ForeignKey(Player, related_name='game_stats')
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
    plus_minus = models.PositiveIntegerField(null=True, blank=True)

    @property
    def fg_pct(self):
        return float(self.fgm) / self.fga

    @property
    def fg3_pct(self):
        return float(self.fg3m) / self.fg3a

    @property
    def ft_pct(self):
        return float(self.ftm) / self.fta

    def __unicode__(self):
        return ('%s %s' % (unicode(self.player), unicode(self.game)))

