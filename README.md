#Arb Setup

* Update players and teams in the database:
```
$ python manage.py fetch -p curr
```
* Run the periodic tasks to update the database with odds data:
```
# In three separate processes:
$ rabbitmq-server
$ celery -A fantasia beat -l info
$ celery -A fantasia worker -l info --without-mingle
```
* Or, run a one-off task to update the database with odds data:
```
$ python manage.py sportsbook_tasks -n write_moneylines -p bookmaker
$ python manage.py sportsbook_tasks -n write_moneylines -p betonline
```
* Test bets
```
# Local
$ python manage.py bet -s betonline -p 1 -a 0.01
# Remote
$ heroku run python manage.py bet --site betonline --position 1 --amount 0.01
```

#Queries
```
SELECT o.site, o.bet_type, o.bet_time, t1.name, o.odds1, o.pos1, t2.name,
    o.odds2, o.pos2, o.game_id, o.prop_id
    FROM sportsbook_odds o JOIN nba_team t1 on o.team1_id=t1.id
    JOIN nba_team t2 on o.team2_id=t2.id
ORDER BY bet_time;
```

#NBA Stats

#Queries

* Contests + result counts
```
SELECT c.*, COUNT(p.payout) AS payouts, rcount.count AS contestants
FROM nba_dkcontest AS c JOIN
    (
    SELECT c.id AS cid, COUNT(r.id) AS count
    FROM nba_dkcontest AS c LEFT JOIN nba_dkresult AS r ON c.id=r.contest_id
    GROUP BY c.id
    ) AS rcount
    ON c.id=rcount.cid
LEFT JOIN nba_dkcontestpayout AS p ON c.id=p.contest_id
GROUP BY c.id, rcount.count
ORDER BY c.date DESC;
```

* Stats

```
SELECT p.first_name, p.last_name, g.date, gs.*
FROM nba_player AS p JOIN nba_gamestats AS gs ON p.id=gs.player_id
    JOIN nba_game AS g ON g.id=gs.game_id
WHERE p.first_name='<FIRST>' AND p.last_name='<LAST>'
ORDER BY g.date DESC;
```

* Injuries

```
SELECT p.first_name, p.last_name, t.name, i.status, i.date, i.comment
FROM nba_player AS p JOIN nba_injury AS i ON p.id=i.player_id
    JOIN nba_team AS t ON p.team_id=t.id
WHERE date='today' OR date='yesterday'
ORDER BY p.first_name, p.last_name, i.date DESC;
```

#Contest Result URLs
```
Moved to the database
```
