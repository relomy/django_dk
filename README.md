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

#Contest Result URLs
```
11/6/2015
https://www.draftkings.com/contest/gamecenter/13772929 115k
https://www.draftkings.com/contest/gamecenter/13726144 47k
11/7/2015
https://www.draftkings.com/contest/gamecenter/13876064 96k
https://www.draftkings.com/contest/gamecenter/13847836 71k
11/8/2015
https://www.draftkings.com/contest/gamecenter/13986906 38k
https://www.draftkings.com/contest/gamecenter/13956848 19k
11/9/2015
https://www.draftkings.com/contest/gamecenter/14126210 96k
https://www.draftkings.com/contest/gamecenter/14116266 71k
11/10/2015
https://www.draftkings.com/contest/gamecenter/14199909 134k
https://www.draftkings.com/contest/gamecenter/14182584 71k
11/11/2015
https://www.draftkings.com/contest/gamecenter/14306948 115k
https://www.draftkings.com/contest/gamecenter/14272702 71k
11/12/2015
https://www.draftkings.com/contest/gamecenter/14407111 96k
https://www.draftkings.com/contest/gamecenter/14386861 47k
11/13/2015
https://www.draftkings.com/contest/gamecenter/14506050 115k
https://www.draftkings.com/contest/gamecenter/14463982 71k
11/14/2015
https://www.draftkings.com/contest/gamecenter/14588685 77k
https://www.draftkings.com/contest/gamecenter/14579894 47k
11/15/2015
https://www.draftkings.com/contest/gamecenter/14695491 48k
https://www.draftkings.com/contest/gamecenter/14672378 24k
11/16/2015
https://www.draftkings.com/contest/gamecenter/14817702 77k
https://www.draftkings.com/contest/gamecenter/14800700 71k
11/17/2015
https://www.draftkings.com/contest/gamecenter/14898424 134k
https://www.draftkings.com/contest/gamecenter/14881724 71k
11/18/2015
https://www.draftkings.com/contest/gamecenter/15000601 115k
https://www.draftkings.com/contest/gamecenter/14973664 71k
11/19/2015
https://www.draftkings.com/contest/gamecenter/15097932 96k
https://www.draftkings.com/contest/gamecenter/15073354 71k
11/20/2015
https://www.draftkings.com/contest/gamecenter/15187303 115k
https://www.draftkings.com/contest/gamecenter/15151314 94k
11/21/2015
https://www.draftkings.com/contest/gamecenter/15278337 77k
https://www.draftkings.com/contest/gamecenter/15278427 24k
11/22/2015
https://www.draftkings.com/contest/gamecenter/15381517 57k
https://www.draftkings.com/contest/gamecenter/15352657 24k
11/23/2015
https://www.draftkings.com/contest/gamecenter/15509296 96k
https://www.draftkings.com/contest/gamecenter/15505841 71k
11/24/2015
https://www.draftkings.com/contest/gamecenter/15588376 153k
https://www.draftkings.com/contest/gamecenter/15566839 94k
11/25/2015
https://www.draftkings.com/contest/gamecenter/15702613 96k
https://www.draftkings.com/contest/gamecenter/15687685 71k
11/26/2015
No data
11/27/2015
https://www.draftkings.com/contest/gamecenter/15810643 96k
https://www.draftkings.com/contest/gamecenter/15809391 71k
11/28/2015
https://www.draftkings.com/contest/gamecenter/15974387 77k
https://www.draftkings.com/contest/gamecenter/15953078 47k
11/29/2015
https://www.draftkings.com/contest/gamecenter/16079108 48k
https://www.draftkings.com/contest/gamecenter/16037585 19k
```
