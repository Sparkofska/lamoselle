import sys,os
# let me import from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))



from machinery import RankingTableManager
import pprint

tm = RankingTableManager.RankingTableManager()
rows = tm.read_all()

pp = pprint.PrettyPrinter()
pp.pprint(rows)
