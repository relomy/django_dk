#NBA Stats

#Queries

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
SELECT p.first_name, p.last_name, i.status, i.date, i.comment
FROM nba_player AS p JOIN nba_injury AS i ON p.id=i.player_id
WHERE date='today' OR date='yesterday'
ORDER BY p.first_name, p.last_name, i.date DESC;
```
