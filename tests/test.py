from models import Base, YouTubeVideo, HistoryEntry
import sa_dbmgt
from sa_dbmgt.models import TableDefinition
import json
from datetime import datetime
import os


def create_json():
    with sa_dbmgt.DatabaseHandler("sqlite:///tests/tmp/ytinfo_all.sqlite3", Base) as db:
        lis = []
        for res in YouTubeVideo.query.slice(0, 10):
            dic = res.to_dict()
            lis.append(dic)
    with open("tests/data.json", 'w') as f:
        f.write(json.dumps(lis, indent=4))


def load_json():
    dic = None
    with open("tests/data.json") as f:
        dic = json.load(f)
    return dic


def create_db(db_fn: str, seed_fn: str):
    db_fn = f"tests/tmp/{db_fn}"
    if os.path.exists(db_fn):
        print(f"Deleting {db_fn}")
        os.remove(db_fn)

    with open(seed_fn) as f:
        dic = json.load(f)

    print(f"Creating database {db_fn} from seed file {seed_fn}")
    with sa_dbmgt.DatabaseHandler(f"sqlite:///{db_fn}", Base) as db:
        for e in dic:
            record = YouTubeVideo(**e)
            db.session.add(record)
        db.session.commit()

    print(f"Checking record count")
    with sa_dbmgt.DatabaseHandler(f"sqlite:///{db_fn}", Base) as db:
        assert(len(YouTubeVideo.query.all()) == len(dic))


def update_db(db_fn: str):
    print(f"Updating records in {db_fn}")
    check = {}
    db_fn = f"tests/tmp/{db_fn}"
    with sa_dbmgt.DatabaseHandler(f"sqlite:///{db_fn}", Base) as db:
        i = 0
        timestamp = datetime.utcnow().isoformat()
        for res in YouTubeVideo.query.slice(0, 10):
            changes = res.update(dislikes=f"{i}", last_checked=timestamp, timestamp=timestamp)
            check[res.id] = str(i)
            changes.pop('last_checked')
            timestamps = changes.pop('timestamp')
            for k, v in changes.items():
                entry = HistoryEntry(id=res.id, column_name=k, info_old=v[0], info_new=v[1],
                                     timestamp_old=timestamps[0], timestamp_new=timestamps[1])
                db.session.add(entry)
            i += 1
        db.session.commit()

    print(f"Checking updated values")
    with sa_dbmgt.DatabaseHandler(f"sqlite:///{db_fn}", Base) as db:
        assert (len(HistoryEntry.query.all()) == 10)
        for res in YouTubeVideo.query.slice(0, 10):
            assert(res.dislikes == check[res.id])


def portable_test(models_db: str, db_name: str):
    print(f"Loading database {db_name} from models in {models_db}")

    tabledefs = sa_dbmgt.load_tabledefs(f"sqlite:///tests/tmp/{models_db}")
    models = sa_dbmgt.load_models(tabledefs)
    print(f"Got models: {models}")

    with sa_dbmgt.DatabaseHandler(f"sqlite:///tests/tmp/{db_name}", models['_Base']):
        YouTubeVideo = models['YouTubeVideo']
        assert(len(list(YouTubeVideo.query.slice(0, 10))) == 10)


def portable_tojson():
    j = TableDefinition.from_model(YouTubeVideo)
    td = TableDefinition(**j.to_dict())
    print(td)


# create_json()
# dic = load_json()
create_db("test.sqlite3", "tests/data.json")
update_db("test.sqlite3")
portable_test("dataman.sqlite3", "test.sqlite3")
portable_test("dataman.sqlite3", "ytinfo_all.sqlite3")
# portable_tojson()
