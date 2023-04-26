from bson import ObjectId
import datetime as dt

from .type import *
from src.utils.util_datetime import tzware_datetime


class BaseDAO(object):
    def __init__(self, collection):
        self.db = collection

    def insert(self, obj):
        if not isinstance(obj, dict):
            raise TypeError("obj must be dictionary!")

        obj["date_created"] = tzware_datetime()
        self.db.insert_one(obj)
        return obj

    def update(self, oid, obj, upsert=False):
        if ObjectId.is_valid(oid):
            oid = ObjectId(oid)

        if not isinstance(obj, dict):
            raise TypeError("obj must be dictionary!")

        obj["date_updated"] = tzware_datetime()
        return self.db.update_one({"_id": oid}, {"$set": obj}, upsert=upsert)

    def update_multiple_condition(self, oid, str_key_condition, str_value_condition, obj, upsert=False):
        if ObjectId.is_valid(oid):
            oid = ObjectId(oid)
        if not isinstance(obj, dict):
            raise TypeError("obj must be dictionary!")

        obj["date_updated"] = tzware_datetime()
        return self.db.update_one({"_id": oid, str_key_condition: str_value_condition}, {"$set": obj}, upsert=upsert)

    def update_raw(self, filter, raw_obj, upsert=False, multi=False):
        if not isinstance(raw_obj, dict):
            raise TypeError("obj must be dictionary!")

        if "$set" in raw_obj:
            raw_obj["$set"]["date_updated"] = tzware_datetime()
        else:
            raw_obj["$set"] = {"date_updated": tzware_datetime()}

        # print(filter, raw_obj)
        if multi:
            return self.db.update_many(filter, raw_obj, upsert=upsert)
        return self.db.update_one(filter, raw_obj, upsert=upsert)

    def update_by_filter(self, filter, obj, upsert=False, multi=False):
        obj["date_updated"] = tzware_datetime()
        if multi:
            self.db.update_many(filter, {"$set": obj}, upsert=upsert)
        return self.db.update_one(filter, {"$set": obj}, upsert=upsert)

    def delete(self, oid, force=False):
        if ObjectId.is_valid(oid):
            oid = ObjectId(oid)

        if force:
            return self.db.delete_one({"_id": oid})

        return self.db.update_one(
            {"_id": oid},
            {"$set": {"status": STATUS_INACTIVE, "date_deleted": tzware_datetime()}}
        )

    def get_item(self, oid):
        if ObjectId.is_valid(oid):
            oid = ObjectId(oid)

        return self.db.find_one({"_id": oid})

    def get_item_with(self, filter, projection={}):
        return self.db.find_one(filter, projection=projection)

    def get_last_item(self, filter={}, sort={}, page=1, page_size=1):
        if not page:
            page = 1

        if not page_size:
            page_size = 1

        if not sort:
            sort = [("_id", -1)]
        return self.db.find(filter).sort(sort).skip(int((page - 1) * page_size)).limit(page_size)

    def get_list_active(self):
        return self.get_list({"status": {"$ne": STATUS_INACTIVE}})

    def get_list(self, filter={}, sort={}, page=1, page_size=PAGE_SIZE_DEFAULT):
        if not page:
            page = 1
        if not page_size or page_size > PAGE_SIZE_MAX:
            page_size = PAGE_SIZE_DEFAULT

        if not sort:
            sort = [("_id", -1)]

        return self.db.find(filter).sort(sort).skip(int((page - 1) * page_size)).limit(page_size)

    def get_all(self, filter={}, sort={}):
        if not sort:
            sort = [("_id", -1)]

        return self.db.find(filter).sort(sort)

    def get_random_items(self, filter={}, sort={}, size=1):
        if sort:
            return self.db.aggregate([
                {"$match": filter},
                {"$sort": sort},
                {"$sample": {"size": size}}
            ])

        return self.db.aggregate([
            {"$match": filter},
            {"$sample": {"size": size}}
        ])

    def aggregate(self, pipelines):
        return self.db.aggregate(pipelines)

    # @Decorators.cache_filter(key_prefix=__name__, key_fields=['uid'])
    def c_get_item(self, uid):
        return self.get_item(uid)

    def c_get_list(self, filter={}, sort={}, page=1, page_size=PAGE_SIZE_DEFAULT):
        return self.get_list(filter={}, sort={}, page=1, page_size=PAGE_SIZE_DEFAULT)

    def get_count(self, filter={}):
        return self.db.count_documents(filter)

    def distinct(self, key, filter={}):
        return self.db.distinct(key, filter)
