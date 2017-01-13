import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
import nba.models as nba_models
from sportsbook.algs import arb
from sportsbook.utils.odds import decimal_to_us_str

class Odds(models.Model):
    site = models.CharField(max_length=20)
    # 'MONEYLINE', 'POINT TOTAL', etc.
    bet_type = models.CharField(max_length=20)
    bet_time = models.DateTimeField(db_index=True)
    # TODO: Using the get_gamestr() method for now, but this should be a
    #       foreign key that references the nba_game table.
    game = models.CharField(max_length=100)
    team1 = models.ForeignKey(nba_models.Team, related_name='odds1')
    # Odds are in European (decimal) format
    odds1 = models.FloatField()
    pos1 = models.IntegerField(default=1)
    team2 = models.ForeignKey(nba_models.Team, related_name='odds2')
    odds2 = models.FloatField()
    pos2 = models.IntegerField(default=2)
    prop_id = models.CharField(max_length=50, null=True, blank=True)
    game_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('site', 'bet_type', 'bet_time', 'game')

    def __unicode__(self):
        return ('%s %s @ %s: %s (%.2f|%s) v %s (%.2f|%s)'
                % (self.site, self.bet_type, self.bet_time, self.team1,
                   self.odds1, decimal_to_us_str(self.odds1), self.team2,
                   self.odds2, decimal_to_us_str(self.odds2)))

    @classmethod
    def get_gamestr(cls, team1, team2):
        # Sort teams
        team1, team2 = cls.order_teams((team1, team2))
        return '%d:%d' % (team1.id, team2.id)

    @classmethod
    def order_teams(cls, teams):
        """
        Args:
            cls [Odds]: Odds class.
            teams [list]: Unordered list of teams.
        Returns:
            [list]: List of ordered teams. Used for deciding team1/team2 in
                    this model.
        """
        # Sort by internal id
        return sorted(teams, key=lambda x: x.id)

    @classmethod
    def write_moneyline(cls, odds, site):
        """
        Write a pair of odds from a site to the database.

        Args:
            odds [tuple]: ((Team1, Odds1, Pos1), (Team2, Odds2, Pos2), Game Id,
                           Prop Id), where @Team is a Team object
                           (e.g. <Team: Houston Rockets>), @Odds is a European
                           odds float (e.g. 1.4), Pos in an integer for the bet
                           position (e.g. 1 or 2), and Game Id and Prop Id are
                           the corresponding ids.
            site [str]: Website key (e.g. BOOKMAKER).
        Returns:
            None
        """
        if odds:
            ((t_a, o_a, p_a), (t_b, o_b, p_b), game_id, prop_id) = odds
            ((t1, o1, p1), (t2, o2, p2)) = sorted(
                ((t_a, o_a, p_a), (t_b, o_b, p_b)), key=lambda x: x[0].id
            )
            gamestr = Odds.get_gamestr(t1, t2)
            o, _ = Odds.objects.update_or_create(
                site=site,
                bet_type='MONEYLINE',
                bet_time=timezone.now(),
                game=gamestr,
                team1=t1,
                team2=t2,
                defaults={
                    'odds1': o1,
                    'odds2': o2,
                    'pos1': p1,
                    'pos2': p2,
                    'game_id': game_id,
                    'prop_id': prop_id,
                }
            )
            print 'Updated %s' % o
            return o

    @classmethod
    def match_odds(cls, bet_time, bet_type, delta=60):
        """
        Args:
            cls [Odds]: Odds class.
            bet_time [datetime]: Timestamp we are querying for.
            bet_type [list]: Type of bet (e.g. MONEYLINE).
            delta [int]: Margin of error, in seconds. Defaults to 1 minute.
        Returns:
            [list]: List of odds objects that match the criteria. Limits to one
                    per site.
        """
        min_bet_time = bet_time - datetime.timedelta(seconds=delta)
        max_bet_time = bet_time + datetime.timedelta(seconds=delta)
        return Odds.objects.filter(bet_time__gte=min_bet_time,
                                   bet_time__lte=max_bet_time,
                                   bet_type=bet_type).distinct('site')

    def match_odds(self, delta=60):
        """
        Get closest odds to the current odds object.

        Args:
            self [Odds]: Odds instance.
            bet_time [datetime]: Timestamp we are querying for.
            delta [int]: Max margin of error, in seconds. Defaults to 1 minute.
        Returns:
            [list]: List of odds objects that match the criteria. Limits to one
                    per site.
        """
        results = []
        min_bet_time = self.bet_time - datetime.timedelta(seconds=delta)
        max_bet_time = self.bet_time + datetime.timedelta(seconds=delta)
        odds = (Odds.objects.filter(bet_time__gte=min_bet_time,
                                    bet_time__lte=max_bet_time,
                                    bet_type=self.bet_type,
                                    game=self.game)
                            .exclude(site=self.site)
                            .order_by('bet_time'))
        for site in set([o.site for o in odds]):
            closest = sorted([o for o in odds if o.site == site],
                             key=lambda x: abs(o.bet_time - self.bet_time))[0]
            results.append(closest)
        return results

    def write_arbs(self, delta=10):
        """
        Calculate the arb opportunities within the specified timeframe.

        Args:
            self [Odds]: Odds instance.
            delta [int]: Max timeframe to query, in seconds.
        Returns
            [list]: List of Arb instances that were written.
        """
        arb_list = []
        closest_odds = self.match_odds(delta)
        for other_odds in closest_odds:
            arb = Arb.write_arb(self, other_odds)
            if arb:
                arb_list.append(arb)
        return arb_list

    def get_arbs(self, delta=10, **kwargs):
        """
        Return the arb opportunities within the specified timeframe.

        Args:
            self [Odds]: Odds instance.
            delta [int]: Max timeframe to query, in seconds.
            kwargs [dict]: Other params to query on (e.g. margin).
        Returns
            [QuerySet]: List of Arb instances that fit the query criteria.
        """
        return (Arb.objects.filter(Q(odds1=self) | Q(odds2=self))
                           .filter(delta__lte=datetime.timedelta(seconds=delta))
                           .filter(**kwargs))

class Arb(models.Model):
    OPTIONS = {
        'Odds1 Team1 - Odds2 Team 2': 1,
        'Odds1 Team2 - Odds2 Team 1': 2,
    }
    OPTIONS_CHOICES = (
        (1, 'Odds1 Team1 - Odds2 Team 2'),
        (2, 'Odds1 Team2 - Odds2 Team 1'),
    )
    option = models.IntegerField(choices=OPTIONS_CHOICES)
    # Order odds by date (earlier odds are odds1, later odds are odds2)
    odds1 = models.ForeignKey(Odds, related_name='arb1')
    odds2 = models.ForeignKey(Odds, related_name='arb2')
    percentage = models.FloatField() # Percentage to allocate to odds1
    margin = models.FloatField()     # Margin made off the bet
    delta = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('option', 'odds1', 'odds2')

    def __unicode__(self):
        if self.option == 1:
            return ('[%s] %s, %s: %.2f @ %.2f|%s\n'
                    '[%s] %s, %s: %.2f @ %.2f|%s\n'
                    'Margin: %2f (Time interval: %s)'
                    % (self.odds1.bet_time, self.odds1.site, self.odds1.team1,
                       self.percentage, self.odds1.odds1,
                       decimal_to_us_str(self.odds1.odds1),
                       self.odds2.bet_time, self.odds2.site, self.odds2.team2,
                       1-self.percentage, self.odds2.odds2,
                       decimal_to_us_str(self.odds2.odds2),
                       self.margin, self.delta))
        elif self.option == 2:
            return ('[%s] %s, %s: %.2f @ %.2f|%s\n'
                    '[%s] %s, %s: %.2f @ %.2f|%s\n'
                    'Margin: %2f (Time interval: %s)'
                    % (self.odds1.bet_time, self.odds1.site, self.odds1.team2,
                       self.percentage, self.odds1.odds2,
                       decimal_to_us_str(self.odds1.odds2),
                       self.odds2.bet_time, self.odds2.site, self.odds2.team1,
                       1-self.percentage, self.odds2.odds1,
                       decimal_to_us_str(self.odds2.odds1),
                       self.margin, self.delta))
        else:
            return 'Undefined Representation for Object'

    @classmethod
    def order_odds(cls, odds):
        """
        Order odds by timestamp.

        Args:
            cls [Odds]: Odds class.
            teams [list]: Unordered list of odds.
        Returns:
            [list]: List of ordered odds. Used for deciding odds1/odds2 in
                    this model.
        """
        # Sort by internal id
        return sorted(odds, key=lambda x: x.bet_time)

    @classmethod
    def write_arb(cls, odds1, odds2):
        """
        Takes two unordered Odds objects, orders them by timestamp, calculates
        if there is an arb opportunity. If so, writes it to the database.

        Args:
            odds1 [Odds]: Odds object.
            odds2 [Odds]: Odds object.
        Returns:
            None
        """
        (odds1, odds2) = cls.order_odds((odds1, odds2))
        option, percentage, margin = arb.calculate_odds(odds1, odds2)
        if option in cls.OPTIONS.values() and margin > 0:
            a, _ = cls.objects.update_or_create(
                option=option,
                odds1=odds1,
                odds2=odds2,
                defaults={
                    'percentage': percentage,
                    'margin': margin,
                    'delta': odds2.bet_time - odds1.bet_time
                }
            )
            print 'Updated %s' % a
            return a

