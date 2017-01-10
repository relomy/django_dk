import datetime
from django.db import models
import nba.models as nba_models
from sportsbook.algs import arb

class Odds(models.Model):
    site = models.CharField(max_length=20)
    # 'MONEYLINE', 'POINT TOTAL', etc.
    type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    # TODO: Using the get_gamestr() method for now, but this should be a
    #       foreign key that references the nba_game table.
    game = models.CharField(max_length=100)
    team1 = models.ForeignKey(nba_models.Team, related_name='odds1')
    # Odds are in European (decimal) format
    odds1 = models.FloatField()
    team2 = models.ForeignKey(nba_models.Team, related_name='odds2')
    odds2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('site', 'type', 'timestamp', 'game')

    def __unicode__(self):
        return ('%s %s @ %s: %s (%.2f) v %s (%.2f)'
                % (self.site, self.type, self.timestamp, self.team1,
                   self.odds1, self.team2, self.odds2))

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
    def match_odds(cls, timestamp, type, delta=60):
        """
        Args:
            cls [Odds]: Odds class.
            timestamp [datetime]: Timestamp we are querying for.
            type [list]: Type of bet (e.g. MONEYLINE).
            delta [int]: Margin of error, in seconds. Defaults to 1 minute.
        Returns:
            [list]: List of odds objects that match the criteria. Limits to one
                    per site.
        """
        min_timestamp = timestamp - datetime.timedelta(seconds=delta)
        max_timestamp = timestamp + datetime.timedelta(seconds=delta)
        return Odds.objects.filter(timestamp__gte=min_timestamp,
                                   timestamp__lte=max_timestamp,
                                   type=type).distinct('site')

    def match_odds(self, delta=60):
        """
        Get closest odds to the current odds object.

        Args:
            self [Odds]: Odds instance.
            timestamp [datetime]: Timestamp we are querying for.
            delta [int]: Max margin of error, in seconds. Defaults to 1 minute.
        Returns:
            [list]: List of odds objects that match the criteria. Limits to one
                    per site.
        """
        results = []
        min_timestamp = self.timestamp - datetime.timedelta(seconds=delta)
        max_timestamp = self.timestamp + datetime.timedelta(seconds=delta)
        odds = (Odds.objects.filter(timestamp__gte=min_timestamp,
                                    timestamp__lte=max_timestamp,
                                    type=self.type,
                                    game=self.game)
                            .exclude(site=self.site)
                            .order_by('timestamp'))
        for site in set([o.site for o in odds]):
            closest = sorted([o for o in odds if o.site == site],
                             key=lambda x: abs(o.timestamp - self.timestamp))[0]
            results.append(closest)
        return results

    def arb(self, delta=60):
        """
        Calculate the arb opportunities within the specified timeframe.

        Args:
            self [Odds]: Odds instance.
            delta [int]: Max timeframe to query, in seconds.
        Returns
            [list]: List of arb opportunities in the format: [
                {
                    'site1': (site, team, odds, percentage),
                    'site2': (site, team, odds, percentage),
                    'margin': margin
                }
            ]
            Where:
                site: Name of the website
                team: Team object to bet on
                odds: Odds given for the team on the site
                percentage: Percentage allocation to the bet for the team on
                            the site
                margin: Margin of return of the bet
            E.g.: {
                'site1': ('BOOKMAKER', <Team: Miami Heat>, 1.4, 0.736)
                'site2': ('BETONLINE', <Team: Houston Rockets>, 3.9, 0.264),
                'margin': 0.03
            }
        """
        results = []
        closest_odds = self.match_odds(delta)
        for other in closest_odds:
            opt, percentage, margin = arb.calculate_odds(self, other)
            if opt == 1:
                print ('[%s] %s, %s: %.2f @ %.2f'
                       % (self.timestamp, self.site, self.team1, percentage,
                          self.odds1))
                print ('[%s] %s, %s: %.2f @ %.2f'
                       % (other.timestamp, other.site, other.team2,
                          1-percentage, other.odds2))
                print 'Margin: %2f' % margin
                results.append({
                    'site1': (self.site, self.team1, self.odds1, percentage),
                    'site2': (other.site, other.team2, other.odds2, 1-percentage),
                    'margin': margin
                })
            elif opt == 2:
                print ('[%s] %s, %s: %.2f @ %.2f'
                       % (self.timestamp, self.site, self.team2, percentage,
                          self.odds2))
                print ('[%s] %s, %s: %.2f @ %.2f'
                       % (other.timestamp, other.site, other.team1,
                          1-percentage, other.odds1))
                print 'Margin: %2f' % margin
                results.append({
                    'site1': (self.site, self.team2, self.odds2, percentage),
                    'site2': (other.site, other.team1, other.odds1, 1-percentage),
                    'margin': margin
                })
        return results
