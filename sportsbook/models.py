import datetime
from django.db import models
import nba.models as nba_models

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
