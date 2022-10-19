from __future__ import absolute_import, unicode_literals

from c8.connection import TenantConnection
from c8.tenant import Tenant
from c8.version import __version__
from c8 import constants

__all__ = ['C8Client']


class C8Client(object):
    """C8Db client.

    :param protocol: Internet transfer protocol (default: "http").
    :type protocol: str | unicode
    :param host: C8Db host (default: "127.0.0.1").
    :type host: str | unicode
    :param port: C8Db port (default: 8529).
    :type port: int
    :param http_client: User-defined HTTP client.
    :type http_client: c8.http.HTTPClient
    """

    def __init__(
            self,
            protocol="http",
            host='127.0.0.1',
            port=80,
            geofabric="_system",
            stream_port=constants.STREAM_PORT,
            email=None,
            password=None,
            http_client=None,
            token=None,
            apikey=None
    ):

        self._protocol = protocol.strip('/')
        self._host = host.strip('/')
        self._port = int(port)
        self._email = email
        self._password = password
        self._fabric_name = geofabric
        self._token = token
        self._apikey = apikey
        self._stream_port = int(stream_port)
        self.set_port()
        self.set_url()
        self._http_client = http_client
        self.get_tenant()

    def set_url(self):
        if "api-" in self.host:
            self._url = '{}://{}:{}'.format(self._protocol,
                                            self.host, self.port)
        else:
            self._url = '{}://api-{}:{}'.format(
                self._protocol, self.host, self.port)

    def set_port(self):
        if self._protocol == 'https':
            self._port = 443

    def get_tenant(self):
        if self._email and self._password:
            self._tenant = self.tenant(
                email=self._email, password=self._password)
            self._fabric = self._tenant.useFabric(self._fabric_name)
        if self._token:
            self._tenant = self.tenant(token=self._token)
            self._fabric = self._tenant.useFabric(self._fabric_name)
        if self._apikey:
            self._tenant = self.tenant(apikey=self._apikey)
            self._fabric = self._tenant.useFabric(self._fabric_name)
        if self._fabric:
            self._search = self._fabric.search()

    def __repr__(self):
        return '<C8Client {}>'.format(self._url)

    @property
    def version(self):
        """Return the client version.

        :returns: Client version.
        :rtype: str | unicode
        """
        return __version__

    @property
    def protocol(self):
        """Return the internet transfer protocol (e.g. "http").

        :returns: Internet transfer protocol.
        :rtype: str | unicode
        """
        return self._protocol

    @property
    def host(self):
        """Return the C8Db host.

        :returns: C8Db host.
        :rtype: str | unicode
        """
        return self._host

    @property
    def port(self):
        """Return the C8Db port.

        :returns: C8Db port.
        :rtype: int
        """
        return self._port

    @property
    def base_url(self):
        """Return the C8Db base URL.

        :returns: C8Db base URL.
        :rtype: str | unicode
        """
        return self._url

    def tenant(self, email='', password='', token=None, apikey=None):
        """Connect to a fabric and return the fabric API wrapper.

        :param email: Email for basic authentication
        :type email: str | unicode
        :param password: Password for basic authentication.
        :type password: str | unicode
        :param token: Bearer Token for authentication.
        :type token: str
        :param apikey: Api Key for authentication.
        :type apikey: str

        :returns: Standard fabric API wrapper.
        :type: c8.fabric.StandardFabric
        """
        connection = TenantConnection(
            url=self._url,
            email=email,
            password=password,
            token=token,
            apikey=apikey,
            http_client=self._http_client
        )
        tenant = Tenant(connection)

        return tenant

    # Reducing steps

    # client.get_fabric_details
    def get_fabric_details(self):
        return self._fabric.fabrics_detail()

    # client.collection

    def collection(self, collection_name):
        return self._fabric.collection(collection_name)

    # client.create_collection
    def create_collection(self,
                          name,
                          sync=False,
                          edge=False,
                          user_keys=True,
                          key_increment=None,
                          key_offset=None,
                          key_generator='traditional',
                          shard_fields=None,
                          index_bucket_count=None,
                          sync_replication=None,
                          enforce_replication_factor=None,
                          spot_collection=False,
                          local_collection=False,
                          is_system=False,
                          stream=False
                          ):
        """Create a new collection.

        :param name: Collection name.
        :type name: str | unicode
        :param sync: If set to True, document operations via the collection
            will block until synchronized to disk by default.
        :type sync: bool
        :param edge: If set to True, an edge collection is created.
        :type edge: bool
        :param key_generator: Used for generating document keys. Allowed values
            are "traditional" or "autoincrement".
        :type key_generator: str | unicode
        :param user_keys: If set to True, users are allowed to supply document
            keys. If set to False, the key generator is solely responsible for
            supplying the key values.
        :type user_keys: bool
        :param key_increment: Key increment value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_increment: int
        :param key_offset: Key offset value. Applies only when value of
            **key_generator** is set to "autoincrement".
        :type key_offset: int
        :param shard_fields: Field(s) used to determine the target shard.
        :type shard_fields: [str | unicode]
        :param index_bucket_count: Number of buckets into which indexes using
            hash tables are split. The default is 16, and this number has to be
            a power of 2 and less than or equal to 1024. For large collections,
            one should increase this to avoid long pauses when the hash table
            has to be initially built or re-sized, since buckets are re-sized
            individually and can be initially built in parallel. For instance,
            64 may be a sensible value for 100 million documents.
        :type index_bucket_count: int
        :param sync_replication: If set to True, server reports success only
            when collection is created in all replicas. You can set this to
            False for faster server response, and if full replication is not a
            concern.
        :type sync_replication: bool
        :param enforce_replication_factor: Check if there are enough replicas
            available at creation time, or halt the operation.
        :type enforce_replication_factor: bool
        :param spot_collection: If True, it is a spot collection
        :type spot_collection: bool
        :param is_system: If True, able to create system collections
        :type is_system: bool
        :param stream: If True, create a local stream for collection.
        :type stream: bool
        :returns: Standard collection API wrapper.
        :rtype: c8.collection.StandardCollection
        """
        resp = self._fabric.create_collection(
            name=name,
            sync=sync,
            edge=edge,
            user_keys=user_keys,
            key_increment=key_increment,
            key_offset=key_offset,
            key_generator=key_generator,
            shard_fields=shard_fields,
            index_bucket_count=index_bucket_count,
            sync_replication=sync_replication,
            enforce_replication_factor=enforce_replication_factor,
            spot_collection=spot_collection,
            local_collection=local_collection,
            is_system=is_system,
            stream=stream
        )
        return resp

    # client.list_collection_indexes
    def list_collection_indexes(self, collection_name):
        """Delete the collection.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :returns: List of indexes
        :rtype: bool
        """
        _collection = self.get_collection(collection_name)
        return _collection.indexes()

    # client.add_hash_index

    def add_hash_index(
            self,
            collection_name,
            fields,
            unique=None,
            sparse=None,
            deduplicate=None
    ):
        """Create a new hash index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: Document fields to index.
        :type fields: [str | unicode]
        :param unique: Whether the index is unique.
        :type unique: bool
        :param sparse: If set to True, documents with None in the field
            are also indexed. If set to False, they are skipped.
        :type sparse: bool
        :param deduplicate: If set to True, inserting duplicate index values
            from the same document triggers unique constraint errors.
        :type deduplicate: bool
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_hash_index(
            fields=fields,
            unique=unique,
            sparse=sparse,
            deduplicate=deduplicate
        )

    # client.add_geo_index

    def add_geo_index(self, collection_name, fields, ordered=None):
        """Create a new geo-spatial index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: A single document field or a list of document fields. If
            a single field is given, the field must have values that are lists
            with at least two floats. Documents with missing fields or invalid
            values are excluded.
        :type fields: str | unicode | list
        :param ordered: Whether the order is longitude, then latitude.
        :type ordered: bool
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_geo_index(
            fields=fields,
            ordered=ordered
        )

    # client.add_skiplist_index

    def add_skiplist_index(
            self,
            collection_name,
            fields,
            unique=None,
            sparse=None,
            deduplicate=None
    ):
        """Create a new skiplist index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: Document fields to index.
        :type fields: [str | unicode]
        :param unique: Whether the index is unique.
        :type unique: bool
        :param sparse: If set to True, documents with None in the field
            are also indexed. If set to False, they are skipped.
        :type sparse: bool
        :param deduplicate: If set to True, inserting duplicate index values
            from the same document triggers unique constraint errors.
        :type deduplicate: bool
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_skiplist_index(
            fields=fields,
            unique=unique,
            sparse=sparse,
            deduplicate=deduplicate
        )

    # client.add_persistent_index

    def add_persistent_index(
            self,
            collection_name,
            fields,
            unique=None,
            sparse=None,
            deduplicate=False
    ):
        """Create a new persistent index.

        Unique persistent indexes on non-sharded keys are not supported in a
        cluster.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: Document fields to index.
        :type fields: [str | unicode]
        :param unique: Whether the index is unique.
        :type unique: bool
        :param sparse: Exclude documents that do not contain at least one of
            the indexed fields, or documents that have a value of None in any
            of the indexed fields.
        :type sparse: bool
        :param deduplicate: If set to True, inserting duplicate index values
            from the same document triggers unique constraint errors.
        :type deduplicate: bool
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_persistent_index(
            fields=fields,
            unique=unique,
            sparse=sparse,
            deduplicate=deduplicate
        )

    # client.add_fulltext_index

    def add_fulltext_index(self, collection_name, fields, min_length=None):
        """Create a new fulltext index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: Document fields to index.
        :type fields: [str | unicode]
        :param min_length: Minimum number of characters to index.
        :type min_length: int
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_fulltext_index(fields=fields, min_length=min_length)

    # client.add_ttl_index

    def add_ttl_index(
            self,
            collection_name,
            fields,
            expire_after=0,
            in_background=False
    ):
        """Create a new ttl index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param fields: Document fields to index.
        :type fields: [str | unicode]
        :param expire_after:  The time (in seconds) after
         a document's creation after which the documents count as "expired".
        :type expire_after: int
        :param in_background: Expire Documents in Background.
        :type in_background: bool
        :returns: New index details.
        :rtype: dict
        :raise c8.exceptions.IndexCreateError: If create fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.add_ttl_index(
            fields=fields,
            expireAfter=expire_after,
            inBackground=in_background
        )

    # client.delete_index

    def delete_index(self, collection_name, index_name, ignore_missing=False):
        """Delete an index.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param index_name: Index name.
        :type index_name: str | unicode
        :param ignore_missing: Do not raise an exception on missing index.
        :type ignore_missing: bool
        :returns: True if index was deleted successfully, False if index was
            not found and **ignore_missing** was set to True.
        :rtype: bool
        :raise c8.exceptions.IndexDeleteError: If delete fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.delete_index(
            index_name=index_name,
            ignore_missing=ignore_missing
        )

    # client.get_index

    def get_index(self, collection_name, index_name):
        _collection = self.get_collection(collection_name)
        return _collection.get_index(index_name)

    # client.delete_collection

    def delete_collection(self, name, ignore_missing=False, system=None):
        """Delete the collection.

        :param name: Collection name.
        :type name: str | unicode
        :param ignore_missing: Do not raise an exception on missing collection.
        :type ignore_missing: bool
        :param system: Whether the collection is a system collection.
        :type system: bool
        :returns: True if collection was deleted successfully,
        False if collection was not found and **ignore_missing** was set to True.
        :rtype: bool
        """
        resp = self._fabric.delete_collection(
            name=name,
            ignore_missing=ignore_missing,
            system=system
        )
        return resp

    # client.import_bulk

    def import_bulk(
            self,
            collection_name,
            documents,
            details=True,
            primaryKey=None,
            replace=False
    ):
        """Insert multiple documents into the collection.

        This is faster than :func:`c8.collection.Collection.insert_many`
        but does not return as much information.

        :param collection_name: Collection name to import documents in.
        :type collection_name: str | unicode
        :param documents: List of new documents to insert. If they contain the
            "_key" or "_id" fields, the values are used as the keys of the new
            documents (auto-generated otherwise). Any "_rev" field is ignored.
        :type documents: [dict]
        :param details: If set to True, the returned result will include an
            additional list of detailed error messages.
        :type details: bool
        :param primaryKey: If not None then uses this field as the primary key for
            the documents to be inserted.
        :type primaryKey: str | unicode
        :param replace: Action to take on unique key constraint violations
            (for documents with "_key" fields). A bool "replace" if set to true replaces 
            the existing documents with new ones else it won't replace the documents and
            count it as "error".
        :type replace: bool
        :returns: Result of the bulk import.
        :rtype: dict
        :raise c8.exceptions.DocumentInsertError: If import fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.import_bulk(
            documents=documents,
            details=details,
            primaryKey=primaryKey,
            replace=replace
        )

    # client.export

    def export(
            self,
            collection_name,
            offset=None,
            limit=None,
            order=None
    ):
        """Export all documents in the collection.

        :param collection_name: Collection name to add index on.
        :type collection_name: str | unicode
        :param offset: This option can be used to simulate paging.
        :type offset: int
        :param limit: This option can be used to simulate paging. Limits the result.
        Maximum: 1000.
        :type limit: int
        :param order: Sorts the result in specified order. Allowed values are "asc" or
        "desc".
        :type order: str | unicode
        :returns: Documents in the collection.
        :rtype: dict
        :raise c8.exceptions.DocumentGetError: If export fails.
        """
        _collection = self.get_collection(collection_name)
        return _collection.export(offset=offset, limit=limit, order=order)

    # client.has_collection

    def has_collection(self, name):
        """Delete the collection.

        :param name: Collection name.
        :type name: str | unicode
        :returns: True if collection exists, False otherwise.
        :rtype: bool
        """
        resp = self._fabric.has_collection(name)
        return resp

    # client.get_collections
    def get_collections(self, collection_model=None):
        """Return the collections in the fabric.

        :param collection_model: Collection Model to get filter collections
        :returns: Collections in the fabric and their details.
        :rtype: [dict]
        :raise c8.exceptions.CollectionListError: If retrieval fails.
        """
        resp = self._fabric.collections(collection_model)
        return resp

    # client.get_collection

    def get_collection(self, name):
        """Return the standard collection API wrapper.

        :param name: Collection name.
        :type name: str | unicode
        :returns: Standard collection API wrapper.
        :rtype: c8.collection.StandardCollection
        """
        resp = self._fabric.collection(name)
        return resp

    # client.on_change

    def on_change(self, collection, callback, timeout=60):
        resp = self._fabric.on_change(collection, callback, timeout)
        return resp

    # client.get_document
    def get_document(self, collection, document, rev=None, check_rev=True):
        """Return a document.

        :param collection: Collection Name
        :type document: str 
        :param document: Document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type document: str | unicode | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | unicode
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :returns: Document, or None if not found.
        :rtype: dict | None
        :raise c8.exceptions.DocumentGetError: If retrieval fails.
        :raise c8.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        _collection = self.get_collection(collection)
        resp = _collection.get(document=document, rev=rev, check_rev=check_rev)
        return resp

    # client.insert_document

    def insert_document(
            self,
            collection_name="",
            return_new=False,
            silent=False,
            sync=None,
            document=None
    ):
        """Insert a new document.

        :param collection_name: Collection name.
        :type collection_name: str | unicode.
        :param document: Document to insert. If it contains the "_key" or "_id"
            field, the value is used as the key of the new document (otherwise
            it is auto-generated). Any "_rev" field is ignored.
        :type document: dict
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        """
        _collection = self.get_collection(collection_name)

        if isinstance(document, dict):
            response = _collection.insert(
                document=document,
                return_new=return_new,
                sync=sync,
                silent=silent
            )

        elif isinstance(document, list):
            response = _collection.insert_many(
                documents=document,
                return_new=return_new,
                sync=sync,
                silent=silent
            )

        return response

    # client.insert_document_from_file()
    def insert_document_from_file(
            self,
            collection_name,
            csv_filepath,
            return_new=False,
            sync=None,
            silent=False
    ):
        """Insert a documents from csv file.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param csv_filepath: CSV file path which contains documents
        :type csv_filepath: str
        :param return_new: Include body of the new document in the returned
            metadata. Ignored if parameter **silent** is set to True.
        :type return_new: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.insert_from_file(
            csv_filepath=csv_filepath,
            return_new=return_new,
            sync=sync,
            silent=silent
        )
        return resp

    # client.update_document

    def update_document(
            self,
            collection_name,
            document,
            check_rev=True,
            merge=True,
            keep_none=True,
            return_new=False,
            return_old=False,
            sync=None,
            silent=False
    ):
        """Update a document.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param document: Partial or full document with the updated values. It
            must contain the "_id" or "_key" field.
        :type document: dict
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new one overwriting the old one.
        :type merge: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool
        :param return_new: Include body of the new document in the result.
        :type return_new: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise c8.exceptions.DocumentUpdateError: If update fails.
        :raise c8.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.update(
            document=document,
            check_rev=check_rev,
            merge=merge,
            keep_none=keep_none,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.update_document_many

    def update_document_many(
            self,
            collection_name,
            documents,
            check_rev=True,
            merge=True,
            keep_none=True,
            return_new=False,
            return_old=False,
            sync=None,
            silent=False
    ):
        """Update multiple documents.

        If updating a document fails, the exception object is placed in the
        result list instead of document metadata.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param documents: Partial or full documents with the updated values.
            They must contain the "_id" or "_key" fields.
        :type documents: [dict]
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param merge: If set to True, sub-dictionaries are merged instead of
            the new ones overwriting the old ones.
        :type merge: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. Otherwise, they are removed completely.
        :type keep_none: bool
        :param return_new: Include bodies of the new documents in the result.
        :type return_new: bool
        :param return_old: Include bodies of the old documents in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | C8Error] | bool
        :raise c8.exceptions.DocumentUpdateError: If update fails.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.update_many(
            documents=documents,
            check_rev=check_rev,
            merge=merge,
            keep_none=keep_none,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.replace_document

    def replace_document(
            self,
            collection_name,
            document,
            check_rev=True,
            return_new=False,
            return_old=False,
            sync=None,
            silent=False
    ):
        """Replace multiple documents.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        If replacing a document fails, the exception object is placed in the
        result list instead of document metadata.

        :param document: New documents to replace the old ones with. They must
            contain the "_id" or "_key" fields. Edge documents must also have
            "_from" and "_to" fields.
        :type document: [dict]
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param return_new: Include bodies of the new documents in the result.
        :type return_new: bool
        :param return_old: Include bodies of the old documents in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | C8Error] | bool
        :raise c8.exceptions.DocumentReplaceError: If replace fails.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.replace(
            document=document,
            check_rev=check_rev,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.replace_document_many

    def replace_document_many(
            self,
            collection_name,
            documents,
            check_rev=True,
            return_new=False,
            return_old=False,
            sync=None,
            silent=False
    ):
        """Replace multiple documents.

        If replacing a document fails, the exception object is placed in the
        result list instead of document metadata.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param documents: New documents to replace the old ones with. They must
            contain the "_id" or "_key" fields. Edge documents must also have
            "_from" and "_to" fields.
        :type documents: [dict]
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param return_new: Include bodies of the new documents in the result.
        :type return_new: bool
        :param return_old: Include bodies of the old documents in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | C8Error] | bool
        :raise c8.exceptions.DocumentReplaceError: If replace fails.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.replace_many(
            documents=documents,
            check_rev=check_rev,
            return_new=return_new,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.delete_document

    def delete_document(
            self,
            collection_name,
            document,
            rev=None,
            check_rev=True,
            ignore_missing=False,
            return_old=False,
            sync=None,
            silent=False
    ):
        """Delete a document.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param document: Document ID, key or body. Document body must contain
            the "_id" or "_key" field.
        :type document: str | unicode | dict
        :param rev: Expected document revision. Overrides the value of "_rev"
            field in **document** if present.
        :type rev: str | unicode
        :param check_rev: If set to True, revision of **document** (if given)
            is compared against the revision of target document.
        :type check_rev: bool
        :param ignore_missing: Do not raise an exception on missing document.
            This parameter has no effect in transactions where an exception is
            always raised on failures.
        :type ignore_missing: bool
        :param return_old: Include body of the old document in the result.
        :type return_old: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision), or True if
            parameter **silent** was set to True, or False if document was not
            found and **ignore_missing** was set to True (does not apply in
            transactions).
        :rtype: bool | dict
        :raise c8.exceptions.DocumentDeleteError: If delete fails.
        :raise c8.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.delete(
            document=document,
            rev=rev,
            check_rev=check_rev,
            ignore_missing=ignore_missing,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.delete_document_many

    def delete_document_many(
            self,
            collection_name,
            documents,
            return_old=False,
            check_rev=True,
            sync=None,
            silent=False
    ):
        """Delete multiple documents.

        If deleting a document fails, the exception object is placed in the
        result list instead of document metadata.

        :param collection_name: Collection name.
        :type collection_name: str | unicode
        :param documents: Document IDs, keys or bodies. Document bodies must
            contain the "_id" or "_key" fields.
        :type documents: [str | unicode | dict]
        :param return_old: Include bodies of the old documents in the result.
        :type return_old: bool
        :param check_rev: If set to True, revisions of **documents** (if given)
            are compared against the revisions of target documents.
        :type check_rev: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: List of document metadata (e.g. document keys, revisions) and
            any exceptions, or True if parameter **silent** was set to True.
        :rtype: [dict | C8Error] | bool
        :raise c8.exceptions.DocumentDeleteError: If delete fails.
        """
        _collection = self.get_collection(collection_name)
        resp = _collection.delete_many(
            documents=documents,
            check_rev=check_rev,
            return_old=return_old,
            sync=sync,
            silent=silent
        )
        return resp

    # client.get_collection_indexes

    def get_collection_indexes(self, collection_name):
        """Return the collection indexes.

        :returns: Collection indexes.
        :rtype: [dict]
        :raise c8.exceptions.IndexListError: If retrieval fails.
        """
        _collection = self._fabric.collection(collection_name)
        resp = _collection.indexes()
        return resp

    # client.get_dc_list
    def get_dc_list(self, detail=False):
        """Return the list of names of Datacenters

        :param detail: detail list of DCs if set to true else only DC names
        :type: boolean
        :returns: DC List.
        :rtype: [str | unicode ]
        :raise c8.exceptions.TenantListError: If retrieval fails.
        """
        resp = self._fabric.dclist(detail=detail)
        return resp

    # client.get_local_dc

    def get_local_dc(self, detail=True):
        """Return the list of local Datacenters

        :param detail: detail list of DCs if set to true else only DC names
        :type: boolean
        :returns: DC List.
        :rtype: [str | dict ]
        :raise c8.exceptions.TenantListError: If retrieval fails.
        """
        resp = self._fabric.localdc(detail=detail)
        return resp

    # client.validate_query

    def validate_query(self, query):
        """Parse and validate the query without executing it.

        :param query: Query to validate.
        :type query: str | unicode
        :returns: Query details.
        :rtype: dict
        :raise c8.exceptions.C8QLQueryValidateError: If validation fails.
        """
        resp = self._fabric.c8ql.validate(query)
        return resp

    # client.explain_query
    def explain_query(self, query, all_plans=False, max_plans=None, opt_rules=None):
        """Inspect the query and return its metadata without executing it.

        :param query: Query to inspect.
        :type query: str | unicode
        :param all_plans: If set to True, all possible execution plans are
            returned in the result. If set to False, only the optimal plan
            is returned
        :type all_plans: bool
        :param max_plans: Total number of plans generated by the optimizer
        :type max_plans: int
        :param opt_rules: List of optimizer rules
        :type opt_rules: list
        :returns: Execution plan, or plans if **all_plans** was set to True.
        :rtype: dict | list
        :raise c8.exceptions.C8QLQueryExplainError: If explain fails.
        """
        resp = self._fabric.c8ql.explain(
            query,
            all_plans=all_plans,
            max_plans=max_plans,
            opt_rules=opt_rules
        )
        return resp

    # client.execute_query
    def execute_query(
            self,
            query,
            sql=False,
            count=False,
            bind_vars=None,
            profile=None,
    ):
        """Execute the query and return the result cursor.

        :param query: Query to execute.
        :type query: str | unicode
        :param sql: If set to True, the SQL query language is used.
        :type sql: bool
        :param count: If set to True, the total document count is included in
            the result cursor.
        :type count: bool
        :param bind_vars: Bind variables for the query.
        :type bind_vars: dict
        :param profile: Return additional profiling details in the cursor,
            unless the query cache is used.
        :type profile: bool
        :returns: Result cursor.
        :rtype: c8.cursor.Cursor
        :raise c8.exceptions.C8QLQueryExecuteError: If execute fails.
        """
        resp = self._fabric.c8ql.execute(
            query,
            sql=sql,
            count=count,
            bind_vars=bind_vars,
            profile=profile,
        )
        return resp

    # client.get_running_queries

    def get_running_queries(self):
        """Return the currently running C8QL queries.

        :returns: Running C8QL queries.
        :rtype: [dict]
        :raise c8.exceptions.C8QLQueryListError: If retrieval fails.
        """
        return self._fabric.c8ql.queries()

    # client.kill_query

    def kill_query(self, query_id):
        """Kill a running query.

        :param query_id: Query ID.
        :type query_id: str | unicode
        :returns: True if kill request was sent successfully.
        :rtype: bool
        :raise c8.exceptions.C8QLQueryKillError: If the send fails.
        """
        return self._fabric.c8ql.kill(query_id)

    # client.create_restql

    def create_restql(self, data):
        """Save restql by name.

        :param data: data to be used for restql POST API
        :type data: dict
        :returns: Results of restql API
        :rtype: dict
        :raise c8.exceptions.RestqlCreateError: if restql operation failed
        """
        return self._fabric.save_restql(data)

    # client.import_restql

    def import_restql(self, queries, details=False):
        """Import custom queries.

        :param queries: queries to be imported
        :type queries: [dict]
        :param details: Whether to include details
        :type details: bool
        :returns: Results of restql API
        :rtype: dict
        :raise c8.exceptions.RestqlImportError: if restql operation failed
        """
        return self._fabric.import_restql(queries=queries, details=details)

    # client.execute_restql

    def execute_restql(self, name, data=None):
        """Execute restql by name.

        :param name: restql name
        :type name: str | unicode
        :param data: restql data (optional)
        :type data: dict
        :returns: Results of execute restql
        :rtype: dict
        :raise c8.exceptions.RestqlExecuteError: if restql execution failed
        """
        return self._fabric.execute_restql(name, data=data)

    # client.read_next_batch_restql

    def read_next_batch_restql(self, id):
        """Read next batch from query worker cursor.

        :param id: the cursor-identifier
        :type id: int
        :returns: Results of execute restql
        :rtype: dict
        :raise c8.exceptions.RestqlCursorError: if fetch next batch failed
        """
        return self._fabric.read_next_batch_restql(id=id)

    # client.delete_restql

    def delete_restql(self, name):
        """Delete restql by name.

        :param name: restql name
        :type name: str | unicode
        :returns: True if restql is deleted
        :rtype: bool
        :raise c8.exceptions.RestqlDeleteError: if restql deletion failed
        """
        return self._fabric.delete_restql(name)

    # client.update_restql

    def update_restql(self, name, data):
        """Update restql by name.

        :param name: name of restql
        :type name: str | unicode
        :param data: restql data
        :type data: dict
        :returns: True if restql is updated
        :rtype: bool
        :raise c8.exceptions.RestqlUpdateError: if query update failed
        """
        return self._fabric.update_restql(name, data)

    # client.get_restqls

    def get_restqls(self):
        """Get all restql associated for user.

        :returns: Details of all restql
        :rtype: list
        :raise c8.exceptions.RestqlListError: if getting restql failed
        """
        return self._fabric.get_all_restql()

    # client.create_stream

    def create_stream(self, stream, local=False):
        """Create the stream under the given fabric

        :param stream: name of stream
        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamCreateError: If creating streams fails.
        """
        return self._fabric.create_stream(stream, local=local)

    # client.delete_stream

    def delete_stream(self, stream, force=False):
        """
        Delete the stream under the given fabric

        :param stream: name of stream
        :param force: whether to force the operation
        :return: 200, OK if operation successful
        :raise: c8.exceptions.StreamDeleteError: If creating streams fails.
        """
        return self._fabric.delete_stream(stream, force=force)

    # client.has_stream

    def has_stream(self, stream, isCollectionStream=False, local=False):
        """ Check if the list of streams has a stream with the given name.

        :param stream: The name of the stream for which to check in the list
                       of all streams.
        :type stream: str | unicode
        :returns: True=stream found; False=stream not found.
        :rtype: bool
        """
        return self._fabric.has_stream(
            stream=stream,
            isCollectionStream=isCollectionStream,
            local=local
        )

    # client.get_stream

    def get_stream(self, operation_timeout_seconds=30):
        """Return the stream collection API wrapper.

        :returns: stream collection API wrapper.
        :rtype: c8.stream_collection.StreamCollection
        """
        return self._fabric.stream(operation_timeout_seconds=operation_timeout_seconds)

    # client.get_streams

    def get_streams(self):
        """Get list of all streams under given fabric

        :returns: List of streams under given fabric.
        :rtype: json
        :raise c8.exceptions.StreamListError: If retrieving streams fails.
        """
        return self._fabric.streams()

    # client.get_stream_stats

    def get_stream_stats(self, stream, isCollectionStream=False, local=False):
        """Get the stats for the given stream

        :param stream: name of stream
        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.get_stream_stats(
            stream,
            isCollectionStream=isCollectionStream,
            local=local
        )

    # client.create_stream_producer

    def enum(**enums):
        return type('Enum', (), enums)

    COMPRESSION_TYPES = enum(LZ4="LZ4",
                             ZLIB="ZLib",
                             NONE=None)

    ROUTING_MODE = enum(
        SINGLE_PARTITION="SinglePartition",
        ROUND_ROBIN_PARTITION="RoundRobinPartition",  # noqa
        CUSTOM_PARTITION="CustomPartition"
    )

    def create_stream_producer(
            self,
            stream,
            isCollectionStream=False,
            local=False,
            producer_name=None,
            initial_sequence_id=None, send_timeout_millis=30000,
            compression_type=COMPRESSION_TYPES.NONE,
            max_pending_messages=1000,
            batching_enabled=False,
            batching_max_messages=1000,
            batching_max_publish_delay_ms=10,
            message_routing_mode=ROUTING_MODE.ROUND_ROBIN_PARTITION
    ):
        """Create a new producer on a given stream.

        **Args**

        * `stream`: The stream name

        **Options**

        * `persistent`: If the stream_stream is persistent or non-persistent
                        default its persitent
        * `local`: If the stream_stream is local or global default its global
        * `producer_name`: Specify a name for the producer. If not assigned,
                           the system will generate a globally unique name
                           which can be accessed with
                           `Producer.producer_name()`. When specifying a name,
                           it is app to the user to ensure that, for a given
                           topic, the producer name is unique across all
                           Pulsar's clusters.
        * `initial_sequence_id`: Set the baseline for the sequence ids for
                                 messages published by the producer. First
                                 message will be using
                                 `(initialSequenceId + 1)`` as its sequence id
                                 and subsequent messages will be assigned
                                 incremental sequence ids, if not otherwise
                                 specified.
        * `send_timeout_seconds`: If a message is not acknowledged by the
                                  server before the `send_timeout` expires, an
                                  error will be reported.
        * `compression_type`: Set the compression type for the producer. By
                              default, message payloads are not compressed.
                              Supported compression types are
                              `CompressionType.LZ4` and `CompressionType.ZLib`.
        * `max_pending_messages`: Set the max size of the queue holding the
                                  messages pending to receive
                                  an acknowledgment from the broker.
        * `block_if_queue_full`: Set whether `send_async` operations should
                                 block when the outgoing message queue is full.
        * `message_routing_mode`: Set the message routing mode for the
                                  partitioned producer. Default is
                                  `PartitionsRoutingMode.RoundRobinDistribution`,  # noqa
                                  other option is
                                  `PartitionsRoutingMode.UseSinglePartition`

        """
        _stream = self._fabric.stream()
        return _stream.create_producer(
            stream, isCollectionStream=isCollectionStream,
            local=local,
            producer_name=producer_name,
            initial_sequence_id=initial_sequence_id,
            send_timeout_millis=send_timeout_millis,
            compression_type=compression_type,
            max_pending_messages=max_pending_messages,
            batching_enabled=batching_enabled,
            batching_max_messages=batching_max_messages,
            batching_max_publish_delay_ms=batching_max_publish_delay_ms,
            message_routing_mode=message_routing_mode
        )

    # client.subscribe
    CONSUMER_TYPES = enum(EXCLUSIVE="Exclusive",
                          SHARED="Shared",
                          FAILOVER="Failover")

    def subscribe(
            self,
            stream,
            isCollectionStream=False,
            local=False,
            subscription_name=None,
            consumer_type=CONSUMER_TYPES.EXCLUSIVE,
            message_listener=None,
            receiver_queue_size=1000,
            consumer_name=None,
            unacked_messages_timeout_ms=None,
            broker_consumer_stats_cache_time_ms=30000,
            is_read_compacted=False,
    ):
        """
        Subscribe to the given topic and subscription combination.

        **Args**

        * `stream`: The name of the stream.
        * `subscription`: The name of the subscription.

        **Options**

        * `local`: If the stream_stream is local or global default its global
        * `consumer_type`: Select the subscription type to be used when
                           subscribing to the topic.
        * `message_listener`: Sets a message listener for the consumer. When
                              the listener is set, the application will receive
                              messages through it. Calls to
                              `consumer.receive()` will not be allowed. The
                              listener function needs to accept
                              (consumer, message)
        * `receiver_queue_size`:
            Sets the size of the consumer receive queue. The consumer receive
            queue controls how many messages can be accumulated by the consumer
            before the application calls `receive()`. Using a higher value
            could potentially increase the consumer throughput at the expense
            of higher memory utilization. Setting the consumer queue size to
            zero decreases the throughput of the consumer by disabling
            pre-fetching of messages. This approach improves the message
            distribution on shared subscription by pushing messages only to
            those consumers that are ready to process them. Neither receive
            with timeout nor partitioned topics can be used if the consumer
            queue size is zero. The `receive()` function call should not be
            interrupted when the consumer queue size is zero. The default value
            is 1000 messages and should work well for most use cases.
        * `consumer_name`: Sets the consumer name.
        * `unacked_messages_timeout_ms`:
            Sets the timeout in milliseconds for unacknowledged messages.
            The timeout needs to be greater than 10 seconds. An exception is
            thrown if the given value is less than 10 seconds. If a successful
            acknowledgement is not sent within the timeout, all the
            unacknowledged messages are redelivered.
        * `broker_consumer_stats_cache_time_ms`:
            Sets the time duration for which the broker-side consumer stats
            will be cached in the client.
        """
        _stream = self._fabric.stream()
        return _stream.subscribe(
            stream=stream,
            local=local,
            isCollectionStream=isCollectionStream,
            subscription_name=subscription_name,
            consumer_type=consumer_type,
            message_listener=message_listener,
            receiver_queue_size=receiver_queue_size,
            consumer_name=consumer_name,
            unacked_messages_timeout_ms=unacked_messages_timeout_ms,
            broker_consumer_stats_cache_time_ms=broker_consumer_stats_cache_time_ms,
            is_read_compacted=is_read_compacted
        )

    # client.create_stream_reader

    def create_stream_reader(
            self,
            stream,
            start_message_id="latest",
            local=False,
            isCollectionStream=False,
            receiver_queue_size=1000,
            reader_name=None
    ):
        """
        Create a reader on a particular topic

        **Args**

        * `stream`: The name of the stream.

        **Options**
        * `start_message_id`: The initial reader positioning is done by
                              specifying a message id. ("latest" or "earliest")
        * `local`: If the stream_stream is local or global default its global
        * `receiver_queue_size`:
            Sets the size of the reader receive queue. The reader receive
            queue controls how many messages can be accumulated by the reader
            before the application calls `read_next()`. Using a higher value
            could potentially increase the reader throughput at the expense of
            higher memory utilization.
        * `reader_name`: Sets the reader name.

        """
        _stream = self._fabric.stream()
        return _stream.create_reader(
            stream=stream,
            start_message_id=start_message_id,
            local=local,
            isCollectionStream=isCollectionStream,
            receiver_queue_size=receiver_queue_size,
            reader_name=reader_name
        )

    # client.unsubscribe
    def unsubscribe(self, subscription, local=False):
        """Unsubscribes the given subscription on all streams on a stream fabric

        :param subscription
        :param local, boolean indicating whether the stream is local or global
        :returns: 200, OK if operation successful
        raise c8.exceptions.StreamPermissionError: If unsubscribing fails.
        """
        _stream = self._fabric.stream()
        return _stream.unsubscribe(subscription=subscription, local=local)

    # client.delete_stream_subscription

    def delete_stream_subscription(self, stream, subscription, local=False):
        """Delete a subscription.

        :param stream: name of stream
        :param subscription: name of subscription
        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamDeleteError: If Subscription has active
                                                 consumers
        """
        _stream = self._fabric.stream()
        return _stream.delete_stream_subscription(stream, subscription, local=local)

    # client.get_stream_subscriptions

    def get_stream_subscriptions(self, stream, local=False):
        """Get the list of persistent subscriptions for a given stream.

        :param stream: name of stream
        :param local: Operate on a local stream instead of a global one.
        :returns: List of stream subscription, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.get_stream_subscriptions(stream=stream, local=local)

    # client.get_stream_backlog

    def get_stream_backlog(self, stream, local=False):
        """Get estimated backlog for offline stream.

        :param stream: name of stream
        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.get_stream_backlog(stream=stream, local=local)

    # client. clear_stream_backlog

    def clear_stream_backlog(self, subscription):
        """Clear backlog for the given stream on a stream fabric

        :param: name of subscription
        :returns: 200, OK if operation successful
        :raise c8.exceptions.StreamPermissionError: If clearing backlogs for
                                                    all streams fails.
        """
        _stream = self._fabric.stream()
        return _stream.clear_stream_backlog(subscription=subscription)

    # client.clear_streams_backlog

    def clear_streams_backlog(self):
        """Clear backlog for all streams on a stream fabric

        :returns: 200, OK if operation successful
        :raise c8.exceptions.StreamPermissionError: If clearing backlogs for
                                                    all streams fails.
        """
        _stream = self._fabric.stream()
        return _stream.clear_streams_backlog()

    # client.get_message_stream_ttl

    def get_message_stream_ttl(self, local=False):
        """Get the TTl for messages in stream

        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.get_message_stream_ttl(local=local)

    # client.publish_message_stream

    def publish_message_stream(self, stream, message):
        """Publish message in a stream

        :param stream: name of stream.
        :param message: Message to be published in the stream.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.publish_message_stream(stream=stream, message=message)

    # client.set_message_stream_ttl

    def set_message_stream_ttl(self, ttl, local=False):
        """Set the TTl for messages in stream

        :param ttl: Time to live for messages in all streams.
        :param local: Operate on a local stream instead of a global one.
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.set_message_stream_ttl(ttl=ttl, local=local)

    # client.set_message_expiry_stream

    def set_message_expiry_stream(self, stream, expiry):
        """Set the expiration time for all messages on the stream.

        :param stream: name of stream.
        :param expiry: expiration time for all messages in seconds
        :returns: 200, OK if operation successful
        :raise: c8.exceptions.StreamPermissionError: If getting subscriptions
                                                     for a stream fails.
        """
        _stream = self._fabric.stream()
        return _stream.set_message_expiry_stream(stream=stream, expiry=expiry)

    # client.create_stream_app

    def create_stream_app(self, data, dclist=[]):
        """Creates a stream application by given data
        :param data: stream app definition
        :param dclist: regions where stream app has to be deployed
        """
        return self._fabric.create_stream_app(data=data, dclist=dclist)

    # client.delete_stream_app

    def delete_stream_app(self, streamapp_name):
        """deletes the stream app by name

        :param streamapp_name: name of stream app
        :returns: True, OK if operation successful
        """
        _streamapp = self._fabric.stream_app(streamapp_name)
        return _streamapp.delete()

    # client.validate_stream_app

    def validate_stream_app(self, data):
        """validates the stream app definition

        :param data: definition of stream app
        :returns: True, OK if app definition is valid.
        """
        return self._fabric.validate_stream_app(data=data)

    # client.retrieve_stream_app

    def retrieve_stream_app(self):
        """retrieves stream apps in a fabric

        :returns: Object with list of stream Apps
        """
        return self._fabric.retrieve_stream_app()

    # client.get_stream_app

    def get_stream_app(self, streamapp_name):
        """returns info of a stream app 

        :param streamapp_name: name of stream app
        :returns: Information of a particular stream app
        """
        _streamapp = self._fabric.stream_app(streamapp_name)
        return _streamapp.get()

    # client.get_stream_app_samples

    def get_stream_app_samples(self):
        """gets samples for stream apps
        """
        return self._fabric.get_samples_stream_app()

    # client.activate_stream_app

    def activate_stream_app(self, streamapp_name, activate=True):
        """activates r deactivates a stream app

        :param streamapp_name: name of stream app
        :param activate:
        :returns: Object with list of properties
        """
        _streamapp = self._fabric.stream_app(streamapp_name)
        return _streamapp.change_state(active=activate)

    # client.publish_message_http_source

    def publish_message_http_source(self, streamapp_name, stream, message):
        """publish messages via HTTP source streams
        @stream: name of the http source stream
        @message: message to be published
        """
        _streamapp = self._fabric.stream_app(streamapp_name)
        return _streamapp.publish_message_http_source(stream=stream, message=message)

    # client.has_graph

    def has_graph(self, graph_name):
        """Check if a graph exists in the fabric.

        :param graph_name: Graph name.
        :type graph_name: str | unicode
        :returns: True if graph exists, False otherwise.
        :rtype: bool
        """
        return self._fabric.has_graph(name=graph_name)

    # client.get_graphs

    def get_graphs(self):
        """List all graphs in the fabric.

        :returns: Graphs in the fabric.
        :rtype: [dict]
        :raise c8.exceptions.GraphListError: If retrieval fails.
        """

        return self._fabric.graphs()

    # client.create_graph
    def create_graph(
            self,
            graph_name,
            edge_definitions=None,
            orphan_collections=None,
            shard_count=None
    ):
        """Create a new graph.

        :param graph_name: Graph name.
        :type graph_name: str | unicode
        :param edge_definitions: List of edge definitions, where each edge
            definition entry is a dictionary with fields "edge_collection",
            "from_vertex_collections" and "to_vertex_collections" (see below
            for example).
        :type edge_definitions: [dict]
        :param orphan_collections: Names of additional vertex collections that
            are not in edge definitions.
        :type orphan_collections: [str | unicode]
        :param shard_count: Number of shards used for every collection in the
            graph. To use this, parameter **smart** must be set to True and
            every vertex in the graph must have the smart field. This number
            cannot be modified later once set. Applies only to enterprise
            version of C8Db.
        :type shard_count: int
        :returns: Graph API wrapper.
        :rtype: c8.graph.Graph
        :raise c8.exceptions.GraphCreateError: If create fails.

        Here is an example entry for parameter **edge_definitions**:

        .. code-block:: python

            {
                'edge_collection': 'teach',
                'from_vertex_collections': ['teachers'],
                'to_vertex_collections': ['lectures']
            }
        """

        return self._fabric.create_graph(
            name=graph_name,
            edge_definitions=edge_definitions,
            orphan_collections=orphan_collections,
            shard_count=shard_count
        )

    # client.delete_graph

    def delete_graph(self, graph_name, ignore_missing=False, drop_collections=None):
        """Drop the graph of the given name from the fabric.

        :param graph_name: Graph name.
        :type graph_name: str | unicode
        :param ignore_missing: Do not raise an exception on missing graph.
        :type ignore_missing: bool
        :param drop_collections: Drop the collections of the graph also. This
            is only if they are not in use by other graphs.
        :type drop_collections: bool
        :returns: True if graph was deleted successfully, False if graph was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise c8.exceptions.GraphDeleteError: If delete fails.
        """
        return self._fabric.delete_graph(
            name=graph_name,
            ignore_missing=ignore_missing,
            drop_collections=drop_collections
        )

    # client.get_graph
    def get_graph(self, graph_name):
        """Return the graph API wrapper.

        :param graph_name: Graph name.
        :type graph_name: str | unicode
        :returns: Graph API wrapper.
        :rtype: c8.graph.Graph
        """
        return self._fabric.graph(graph_name)

    # client.insert_edge

    def insert_edge(
            self,
            graph_name,
            edge_collection,
            from_vertex_collections,
            to_vertex_collections
    ):
        """Create a new edge definition.

        An edge definition consists of an edge collection, "from" vertex
        collection(s) and "to" vertex collection(s). Here is an example entry:

        .. code-block:: python

            {
                'edge_collection': 'edge_collection_name',
                'from_vertex_collections': ['from_vertex_collection_name'],
                'to_vertex_collections': ['to_vertex_collection_name']
            }

        :param graph_name: Name of the Graph for which you want to create edge.
        :type graph_name: str | unicode
        :param edge_collection: Edge collection name.
        :type edge_collection: str | unicode
        :param from_vertex_collections: Names of "from" vertex collections.
        :type from_vertex_collections: [str | unicode]
        :param to_vertex_collections: Names of "to" vertex collections.
        :type to_vertex_collections: [str | unicode]
        :returns: Edge collection API wrapper.
        :rtype: c8.collection.EdgeCollection
        :raise c8.exceptions.EdgeDefinitionCreateError: If create fails.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.create_edge_definition(
            edge_collection=edge_collection,
            from_vertex_collections=from_vertex_collections,
            to_vertex_collections=to_vertex_collections
        )

    # client.replace_edge

    def replace_edge(
            self,
            graph_name,
            edge_collection,
            from_vertex_collections,
            to_vertex_collections
    ):
        """Replaces an edge definition.

        :param graph_name: Name of the Graph for which you want to create edge.
        :type graph_name: str | unicode
        :param edge_collection: Edge collection name.
        :type edge_collection: str | unicode
        :param from_vertex_collections: Names of "from" vertex collections.
        :type from_vertex_collections: [str | unicode]
        :param to_vertex_collections: Names of "to" vertex collections.
        :type to_vertex_collections: [str | unicode]
        :returns: Edge collection API wrapper.
        :rtype: c8.collection.EdgeCollection
        :raise c8.exceptions.EdgeDefinitionCreateError: If create fails.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.replace_edge_definition(
            edge_collection=edge_collection,
            from_vertex_collections=from_vertex_collections,
            to_vertex_collections=to_vertex_collections
        )

    # client.update_edge
    def update_edge(
            self,
            graph_name, edge,
            check_rev=True,
            keep_none=True,
            sync=None,
            silent=False
    ):
        """Update an edge document.

        :param graph_name: Name of the Graph for which you want to create edge.
        :type graph_name: str | unicode
        :param edge: Partial or full edge document with updated values. It must
            contain the "_id" field.
        :type edge: dict
        :param check_rev: If set to True, revision of **edge** (if given) is
            compared against the revision of target edge document.
        :type check_rev: bool
        :param keep_none: If set to True, fields with value None are retained
            in the document. If set to False, they are removed completely.
        :type keep_none: bool
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise c8.exceptions.DocumentUpdateError: If update fails.
        :raise c8.exceptions.DocumentRevisionError: If revisions mismatch.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.update_edge(
            edge=edge,
            check_rev=check_rev,
            keep_none=keep_none,
            sync=sync,
            silent=silent
        )

    # client.delete_edge
    def delete_edge(self, graph_name, edge_name, purge=False):
        """Delete an edge definition from the graph.

        :param graph_name: Name of the Graph for which you want to delete edge.
        :type graph_name: str | unicode
        :param edge_name: Edge collection name.
        :type edge_name: str | unicode
        :param purge: If set to True, the edge definition is not just removed
            from the graph but the edge collection is also deleted completely
            from the fabric.
        :type purge: bool
        :returns: True if edge definition was deleted successfully.
        :rtype: bool
        :raise c8.exceptions.EdgeDefinitionDeleteError: If delete fails.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.delete_edge_definition(name=edge_name, purge=purge)

    # client.get_edges

    def get_edges(self, graph_name):
        """Return the edge definitions of the graph.

        :param graph_name: Name of the Graph for which you want to get the edge.
        :type graph_name: str | unicode
        :returns: Edge definitions of the graph.
        :rtype: [dict]
        :raise c8.exceptions.EdgeDefinitionListError: If retrieval fails.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.edge_definitions()

    # client.link_edge

    def link_edge(
            self,
            graph_name,
            collection,
            from_vertex,
            to_vertex,
            data=None,
            sync=None,
            silent=False
    ):
        """Insert a new edge document linking the given vertices.

        :param graph_name: Name of the Graph.
        :type graph_name: str | unicode
        :param collection: Edge collection name.
        :type collection: str | unicode
        :param from_vertex: "From" vertex document ID or body with "_id" field.
        :type from_vertex: str | unicode | dict
        :param to_vertex: "To" vertex document ID or body with "_id" field.
        :type to_vertex: str | unicode | dict
        :param data: Any extra data for the new edge document. If it has "_key"
            or "_id" field, its value is used as key of the new edge document
            (otherwise it is auto-generated).
        :type data: dict
        :param sync: Block until operation is synchronized to disk.
        :type sync: bool
        :param silent: If set to True, no document metadata is returned. This
            can be used to save resources.
        :type silent: bool
        :returns: Document metadata (e.g. document key, revision) or True if
            parameter **silent** was set to True.
        :rtype: bool | dict
        :raise c8.exceptions.DocumentInsertError: If insert fails.
        """
        _graph = self._fabric.graph(graph_name)
        return _graph.link(collection=collection,
                           from_vertex=from_vertex,
                           to_vertex=to_vertex,
                           data=data,
                           sync=sync,
                           silent=silent)

    # client.has_user

    def has_user(self, username):
        """Check if user exists.

        :param username: Username.
        :type username: str | unicode
        :returns: True if user exists, False otherwise.
        :rtype: bool
        """
        return self._tenant.has_user(username)

    # client.get_users

    def get_users(self):
        """Return all user details.

        :returns: List of user details.
        :rtype: [dict]
        :raise c8.exceptions.UserListError: If retrieval fails.
        """
        return self._tenant.users()

    # client.get_user

    def get_user(self, username):
        """Return user details.

        :param username: Username.
        :type username: str | unicode
        :returns: User details.
        :rtype: dict
        :raise c8.exceptions.UserGetError: If retrieval fails.
        """
        return self._tenant.user(username)

    # client.create_user

    def create_user(self, email, password, display_name=None, active=True, extra=None):
        """Create a new user.

        :param email: Email address of the user.
        :type email: str | unicode
        :param password: Password to be set for the user.
        :type password: str | unicode
        :param display_name: Display name for the user.
        :type display_name: str | unicode
        :param active: True if user is active, False otherwise.
        :type active: bool
        :param extra: Additional data for the user.
        :type extra: dict
        :returns: New user details.
        :rtype: dict
        :raise c8.exceptions.UserCreateError: If create fails.
        """
        return self._tenant.create_user(
            email=email,
            password=password,
            display_name=display_name,
            active=active,
            extra=extra
        )

    # client.update_user

    def update_user(
            self,
            username,
            password=None,
            display_name=None,
            email=None,
            is_verified=None,
            active=None,
            extra=None
    ):
        """Update a user.

        :param username: Username.
        :type username: str | unicode
        :param password: New password.
        :type password: str | unicode
        :param display_name: New display name for the user.
        :type display_name: str | unicode
        :param email: New email for the user.
        :type email: str | unicode
        :param is_verified: Whether the email is verified or not.
        :type is_verified: bool
        :param active: Whether the user is active.
        :type active: bool
        :param extra: Additional data for the user.
        :type extra: dict
        :returns: New user details.
        :rtype: dict
        :raise c8.exceptions.UserUpdateError: If update fails.
        """
        return self._tenant.update_user(
            username=username,
            password=password,
            display_name=display_name,
            email=email,
            is_verified=is_verified,
            active=active,
            extra=extra
        )

    # client.delete_user

    def delete_user(self, username, ignore_missing=False):
        """Delete a user.

        :param username: Username.
        :type username: str | unicode
        :param ignore_missing: Do not raise an exception on missing user.
        :type ignore_missing: bool
        :returns: True if user was deleted successfully, False if user was not
            found and **ignore_missing** was set to True.
        :rtype: bool
        :raise c8.exceptions.UserDeleteError: If delete fails.
        """
        return self._tenant.delete_user(username=username,
                                        ignore_missing=ignore_missing)

    # client.list_accessible_databases_user

    def list_accessible_databases_user(self, username, full=False):
        """Lists accessible databases for a user.

        :param username: Username.
        :type username: str | unicode
        :param full: Return the full set of access levels for all databases 
                and all collections if set to true.
        :type full: bool
        :returns: Object containing database details
        :rtype: list | object
        :raise c8.exceptions.DataBaseError: If request fails.
        """
        return self._tenant.list_accessible_databases_user(username=username,
                                                           full=full)

    # client.get_database_access_level_user

    def get_database_access_level_user(self, username, databasename=""):
        """Fetch the access level for a specific database.

        :param username: Username.
        :type username: str | unicode
        :param databasename: Database name.
        :type databasename: str | unicode
        :returns: Access Details
        :rtype: string
        :raise c8.exceptions.GetDataBaseAccessLevel: If request fails.
        """
        return self._tenant.get_database_access_level_user(username=username,
                                                           databasename=databasename)

    # client.remove_database_access_level_user

    def remove_database_access_level_user(self, username, databasename=""):
        """Clear the access level for the specific database of user. 
        As consequence the default database access level is used.

        :param username: Username.
        :type username: str | unicode
        :param databasename: Database name.
        :type databasename: str | unicode
        :returns: Object containing database details
        :rtype: object
        :raise c8.exceptions.ClearDataBaseAccessLevel: If request fails.
        """
        return self._tenant.remove_database_access_level_user(
            username=username,
            databasename=databasename
        )

    # client.set_database_access_level_user

    def set_database_access_level_user(self, username, databasename="", grant='ro'):
        """Set the access levels for the specific database of user.

        :param username: Username.
        :type username: str | unicode
        :param databasename: Database name.
        :type databasename: str | unicode
        :param grant: Grant accesslevel.
                    Use "rw" to set the database access level to Administrate .
                    Use "ro" to set the database access level to Access.
                    Use "none" to set the database access level to No access.
        :type grant: string
        :returns: Object containing database details
        :rtype: object
        :raise c8.exceptions.SetDataBaseAccessLevel: If request fails.
        """
        return self._tenant.set_database_access_level_user(username=username,
                                                           databasename=databasename,
                                                           grant=grant)

    # client.list_accessible_collections_user

    def list_accessible_collections_user(self, username, databasename='_system',
                                         full=False):
        """Fetch the collection access level for a specific collection in a database.

        :param username: Name of the user
        :type username: string
        :param databasename: Name of the database
        :type databasename: string
        :param full: Return the full set of access levels for all collections.
        :type full: boolean
        :returns: Fetch the list of collections access level for a specific user.
        :rtype: string
        :raise c8.exceptions.CollectionAccessLevel: If request fails.
        """
        return self._tenant.list_accessible_collections_user(username=username,
                                                             databasename=databasename,
                                                             full=full)

    # client.get_collection_access_level_user

    def get_collection_access_level_user(
            self,
            username,
            collection_name,
            databasename='_system'
    ):
        """Fetch the collection access level for a specific collection in a database.

        :param collection_name: Name of the collection
        :type collection_name: string
        :param databasename: Name of the database
        :type databasename: string
        :returns: AccessLevel of a db.
        :rtype: string
        :raise c8.exceptions.CollectionAccessLevel: If request fails.
        """
        return self._tenant.get_collection_access_level_user(username=username,
                                                             collection_name=collection_name,
                                                             databasename=databasename)

    # client.set_collection_access_level_user

    def set_collection_access_level_user(
            self,
            username,
            collection_name,
            databasename='_system',
            grant='ro'
    ):

        """Set the collection access level for a specific collection in a database.

        :param collection_name: Name of the collection
        :type collection_name: string
        :param databasename: Name of the database
        :type databasename: string
        :param grant: Use "rw" to set the database access level to Administrate .
                      Use "ro" to set the database access level to Access.
                      Use "none" to set the database access level to No access.
        :type grant: string
        :returns: Accesslevel of a particular db.
        :rtype: Object
        :raise c8.exceptions.SetCollectionAccessLevel: If request fails.
        """
        return self._tenant.set_collection_access_level_user(
            username=username,
            collection_name=collection_name,
            databasename=databasename,
            grant=grant
        )

    # client.clear_collection_access_level_user

    def clear_collection_access_level_user(
            self,
            username,
            collection_name,
            databasename='_system'
    ):

        """Clear the collection access level for a specific collection in a database.

        :param collection_name: Name of the collection
        :type collection_name: string
        :param databasename: Name of the database
        :type databasename: string
        :returns: True if operation successful.
        :rtype: booleaan
        :raise c8.exceptions.ClearCollectionAccessLevel: If request fails.
        """
        return self._tenant.clear_collection_access_level_user(
            username=username,
            collection_name=collection_name,
            databasename=databasename
        )

    # client.list_accessible_streams_user

    def list_accessible_streams_user(
            self,
            username,
            databasename='_system',
            full=False
    ):
        """Fetch the list of streams available to the specified user.

        :param username: Name of the user
        :type username: string
        :param databasename: Name of the database
        :type databasename: string
        :param full: Return the full set of access levels for all streams.
        :type full: boolean
        :returns: List of available databases.
        :rtype: list
        :raise c8.exceptions.ListStreams: If request fails.
        """
        return self._tenant.list_accessible_streams_user(
            username=username,
            databasename=databasename,
            full=full
        )

    # client.get_stream_access_level_user

    def get_stream_access_level_user(
            self,
            username,
            streamname,
            databasename='_system'
    ):
        """Fetch the database access level for a specific stream.

        :param username: Name of the user
        :type username: string
        :param streamname: Name of the stream
        :type streamname: string
        :param databasename: Name of the database
        :type databasename: string
        :returns: AccessLevel of a db.
        :rtype: string
        :raise c8.exceptions.StreamAccessLevel: If request fails.
        """
        return self._tenant.get_stream_access_level_user(
            username=username,
            streamname=streamname,
            databasename=databasename
        )

    # client.set_stream_access_level_user

    def set_stream_access_level_user(
            self,
            username,
            streamname,
            databasename='_system',
            grant='ro'
    ):
        """Set the database access level for a specific stream.

        :param username: Name of the user
        :type username: string
        :param streamname: Name of the stream
        :type streamname: string
        :param databasename: Name of the database
        :type databasename: string
        :param grant: Use "rw" to set the database access level to Administrate .
                      Use "ro" to set the database access level to Access.
                      Use "none" to set the database access level to No access.
        :type grant: string
        :returns: Accesslevel of a particular db.
        :rtype: Object
        :raise c8.exceptions.SetStreamAccessLevel: If request fails.
        """
        return self._tenant.set_stream_access_level_user(
            username=username,
            streamname=streamname,
            databasename=databasename,
            grant=grant
        )

    # client.clear_stream_access_level_user

    def clear_stream_access_level_user(self, username, streamname,
                                       databasename='_system'):

        """Clear the database access level for a specific stream.

        :param username: Name of the user
        :type username: string
        :param streamname: Name of the stream
        :type streamname: string
        :param databasename: Name of the database
        :type databasename: string
        :returns: True if operation successful.
        :rtype: booleaan
        :raise c8.exceptions.ClearStreamAccessLevel: If request fails.
        """
        return self._tenant.clear_stream_access_level_user(username=username,
                                                           streamname=streamname,
                                                           databasename=databasename)

    # client.get_billing_access_level_user

    def get_billing_access_level_user(self, username):
        """Fetch the billing access level.

        :returns: AccessLevel of billing.
        :rtype: string
        :raise c8.exceptions.BillingAccessLevel: If request fails.
        """
        return self._tenant.get_billing_access_level_user(username=username)

    # client.set_billing_access_level

    def set_billing_access_level_user(self, username, grant='ro'):

        """Set the billing access level for user.

        :param username: Name of the user
        :type username: string
        :param grant: Use "rw" to set the database access level to Administrate .
                      Use "ro" to set the database access level to Access.
                      Use "none" to set the database access level to No access.
        :type grant: string
        :returns: Billing Accesslevel of a particular db.
        :rtype: Object
        :raise c8.exceptions.SetBillingAccessLevel: If request fails.
        """
        return self._tenant.set_billing_access_level_user(
            username=username,
            grant=grant
        )

    # client.clear_billing_access_level

    def clear_billing_access_level_user(self, username):

        """Clear the billing access level.

        :returns: True if operation successful.
        :rtype: booleaan
        :raise c8.exceptions.ClearBillingAccessLevel: If request fails.
        """
        return self._tenant.clear_billing_access_level_user(username=username)

    # client.get_attributes_user

    def get_attributes_user(self, username):

        """Fetch the list of attributes for the specified user.

        :returns: All attributes for the specified user.
        :rtype: dict
        :raise c8.exceptions.GetAttributes: If request fails.
        """
        return self._tenant.get_attributes_user(username=username)

    # client.update_attributes_user

    def update_attributes_user(self, username, attributes):

        """Update the list of attributes for the specified user.

        :param attributes: The key-value pairs of attributes with values that needs to be updated.
        :type attributes: dict
        :returns: The updated attributes.
        :rtype: Object
        :raise c8.exceptions.UpdateAttributes: If request fails.
        """
        return self._tenant.update_attributes_user(username=username,
                                                   attributes=attributes)

    # client.remove_all_attributes_user

    def remove_all_attributes_user(self, username):

        """Remove all attributes of the specified user.

        :returns: True if operation successful.
        :rtype: booleaan
        :raise c8.exceptions.RemoveAllAttributes: If request fails.
        """
        return self._tenant.remove_all_attributes_user(username=username)

    # client.remove_attribute_user

    def remove_attribute_user(self, username, attributeid):

        """Remove the specified attribute for the specified user.

        :param username: Name of the user
        :type username: string
        :param attributeid: Name of the attribute
        :type attributeid: string
        :returns: True if operation successful.
        :rtype: booleaan
        :raise c8.exceptions.RemoveAttribute: If request fails.
        """
        return self._tenant.remove_attribute_user(username=username,
                                                  attributeid=attributeid)

    # client.get_permissions

    def get_permissions(self, username):
        """Return user permissions for all fabrics and collections.

        :param username: Username.
        :type username: str | unicode
        :returns: User permissions for all fabrics and collections.
        :rtype: dict
        :raise: c8.exceptions.PermissionListError: If retrieval fails.
        """
        return self._tenant.permissions(username)

    # client.kv_get_collections

    def get_collections_kv(self):
        """Returns the list of collections using kv.
        :returns: Existing Collections.
        :rtype: list
        :raise c8.exceptions.ListCollections: If retrieval fails.
        """
        return self._fabric.key_value.get_collections()

    # client.create_collection_kv

    def create_collection_kv(self, name, expiration=False):
        """Creates Collection.

        :param name: Collection name.
        :type name: str | unicode
        :param expiration: if True then the namesapce supports TTL.
        :type expiration: boolean
        :returns: True if the request is successful.
        :rtype: boolean
        :raise c8.exceptions.CreateCollectionError: If creation fails.
        """
        return self._fabric.key_value.create_collection(name=name,
                                                        expiration=expiration)

    # client.delete_collection_kv

    def delete_collection_kv(self, name):
        """Deletes Collection.

        :param name: Collection name.
        :type name: str | unicode
        :returns: True if the request is successful.
        :rtype: boolean
        :raise c8.exceptions.DeleteCollectionError: If delete fails.
        """
        return self._fabric.key_value.delete_collection(name=name)

    # client.has_collection_kv

    def has_collection_kv(self, name):
        """Checks if a Collection exists.

        :param name: Collection name.
        :type name: str | unicode
        :returns: True if the collection exists.
        :rtype: boolean
        """
        return self._fabric.key_value.has_collection(name)

    # client.insert_key_value_pair

    def insert_key_value_pair(self, name, data=None):
        """Set a key value pair.

        :param name: Collection name.
        :type name: str | unicode
        :param data: objects to be inserted.
        :type data: list
        :returns: List of inserted objects.
        :rtype: list
        :raise c8.exceptions.InsertKVError: If insertion fails.
        """
        return self._fabric.key_value.insert_key_value_pair(name=name, data=data)

    # client.delete_entry_for_key

    def delete_entry_for_key(self, name, key):
        """Delete an entry for a key.

        :param name: Collection name.
        :type name: str | unicode
        :param key: The key for which the object is to be deleted.
        :type key: string
        :returns: True if successfully deleted.
        :rtype: boolean
        :raise c8.exceptions.DeleteEntryForKey: If deletion fails.
        """
        return self._fabric.key_value.delete_entry_for_key(name=name, key=key)

    # client.delete_entry_for_keys

    def delete_entry_for_keys(self, name, keys=[]):
        """Deletes entries for multiple keys.

        :param name: Collection name.
        :type name: str | unicode
        :param keys: The keys for which the object is to be deleted.
        :type keys: list
        :returns: List of deleted objects
        :rtype: List
        :raise c8.exceptions.DeleteEntryForKey: If deletion fails.
        """
        return self._fabric.key_value.delete_entry_for_keys(name=name, keys=keys)

    # client.get_value_for_key

    def get_value_for_key(self, name, key):
        """Get value for a key from key-value collection.

        :param name: Collection name.
        :type name: str | unicode
        :param key: The key for which the value is to be fetched.
        :type key: string
        :returns: The value object.
        :rtype: object
        :raise c8.exceptions.GetValueError: If request fails.
        """
        return self._fabric.key_value.get_value_for_key(name=name, key=key)

    # client.get_keys

    def get_keys(self, name, offset=None, limit=None, order=None):
        """gets keys of a collection.

        :param name: Collection name.
        :type name: str | unicode
        :param offset: Offset to simulate paging.
        :type offset: int
        :param limit: Limit to simulate paging.
        :type limit: int
        :param order: Order the results ascending (asc) or descending (desc).
        :type order: str | unicode
        :returns: List of Keys.
        :rtype: list
        :raise c8.exceptions.GetKeysError: If request fails.
        """
        return self._fabric.key_value.get_keys(name, offset=offset,
                                               limit=limit, order=order)

    # client.get_kv_count

    def get_kv_count(self, name):
        """gets the kv count of a collection.

        :param name: Collection name.
        :type name: str | unicode
        :returns: Number of kv entries.
        :rtype: int
        :raise c8.exceptions.GetCountError: If request fails.
        """
        return self._fabric.key_value.get_kv_count(name)

    # client.get_key_value_pairs

    def get_key_value_pairs(self, name, offset=None, limit=None):
        """Fetch key-value pairs from collection. Optional list of keys
        Note: Max limit is 100 keys per request.

        :param name: Collection name.
        :type name: str | unicode
        :param offset: Offset to simulate paging.
        :type offset: int
        :param limit: Limit to simulate paging.
        :type limit: int
        :return: The key value pairs from the collection.
        :rtype: object
        :raise c8.exceptions.GetKVError: If request fails.
        """
        return self._fabric.key_value.get_key_value_pairs(name=name,
                                                          offset=offset,
                                                          limit=limit)

    # client.remove_key_value_pairs

    def remove_key_value_pairs(self, name):
        """Remove all key-value pairs in a collection

        :param name: Collection name.
        :type name: str | unicode
        :return: True if removal succeeds
        :rtype: bool
        :raise c8.exceptions.RemoveKVError: If request fails.
        """
        return self._fabric.key_value.remove_key_value_pairs(name)

    # client.create_api_key

    def create_api_key(self, keyid):
        """Creates an api key.

        :returns: Creates an api key.
        :rtype: list
        :raise c8.exceptions.CreateAPIKey: If request fails.
        """
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.create_api_key()

    # client.list_all_api_keys

    def list_all_api_keys(self):
        return self._fabric.list_all_api_keys()

    # client.get_api_key

    def get_api_key(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_api_key()

    # client.remove_api_key

    def remove_api_key(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.remove_api_key()

    # client.list_accessible_databases

    def list_accessible_databases(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.list_accessible_databases()

    # client.get_database_access_level

    def get_database_access_level(self, keyid, databasename):
        """Fetch the database access level for a specific database.

        :param databasename: Name of the database
        :type databasename: string
        :returns: AccessLevel of a db.
        :rtype: string
        :raise c8.exceptions.DataBaseAccessLevel: If request fails.
        """
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_database_access_level(databasename)

    def set_database_access_level(self, keyid, databasename, grant='ro'):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.set_database_access_level(databasename, grant=grant)

    def clear_database_access_level(self, keyid, databasename):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.clear_database_access_level(databasename)

    def list_accessible_collections(self, keyid, databasename='_system', full=False):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.list_accessible_collections(databasename, full)

    def get_collection_access_level(self, keyid, collection_name,
                                    databasename='_system'):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_collection_access_level(collection_name, databasename)

    def set_collection_access_level(self, keyid, collection_name,
                                    databasename='_system',
                                    grant='ro'):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.set_collection_access_level(collection_name, databasename,
                                                    grant)

    def clear_collection_access_level(self, keyid, collection_name,
                                      databasename='_system'):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.clear_collection_access_level(collection_name, databasename)

    def list_accessible_streams(self, keyid, databasename='_system', full=False):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.list_accessible_streams(databasename, full)

    def get_stream_access_level(self, keyid, streamname, databasename='_system',
                                local=False):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_stream_access_level(streamname, databasename, local)

    def set_stream_access_level(self, keyid, streamname, databasename='_system',
                                grant='ro', local=False):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.set_stream_access_level(streamname, databasename, grant,
                                                local=local)

    def clear_stream_access_level(self, keyid, streamname, databasename='_system',
                                  local=False):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.clear_stream_access_level(streamname, databasename, local)

    def get_billing_access_level(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_billing_access_level()

    def set_billing_access_level(self, keyid, grant='ro'):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.set_billing_access_level(grant)

    def clear_billing_access_level(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.clear_billing_access_level()

    def get_attributes(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.get_attributes()

    def update_attributes(self, keyid, attributes):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.update_attributes(attributes)

    def remove_all_attributes(self, keyid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.remove_all_attributes()

    def remove_attribute(self, keyid, attributeid):
        _apiKeys = self._fabric.api_keys(keyid)
        return _apiKeys.remove_attribute(attributeid)

    def set_search(self, collection, enable, field):
        """Set search capability of a collection (enabling or disabling it). 
        If the collection does not exist, it will be created.

        :param collection: Collection name on which search capabilities has to be enabled/disabled
        :type collection: str | unicode
        :param enable: Whether to enable / disable search capabilities
        :type enable: string ("true" or "false")
        :param field: For which field to enable search capability.
        :type field: str | unicode
        :returns: True if set operation is successfull
        :rtype: bool
        """
        return self._search.set_search(collection, enable, field)

    def create_view(self, name, links={}, primary_sort=[]):
        """Creates a new view with a given name and properties if it does not
        already exist.
        
        :param name: The name of the view
        :type name: str | unicode
        :param links: Link properties related with the view
        :type links: dict
        :param primary_sort: Array of object containg the fields on which
        sorting needs to be done and whether the sort is asc or desc
        :type primary_sort: [dict]
        :return: object of new view
        :rtype: dict
        """
        return self._search.create_view(name, links, primary_sort)

    def list_all_views(self):
        """ List all views

        :returns: Returns an object containing an array of all view descriptions. 
        :rtype: [dict]
        """
        return self._search.list_all_views()

    def get_view_info(self, view):
        """Returns information about view

        :param view: name of the view
        :type view: str | unicode
        :returns: returns information about view
        :rtype: dict
        """
        return self._search.get_view_info(view)

    def rename_view(self, old_name, new_name):
        """Rename given view to new name

        :param old_name: Old view name
        :type old_name: str | unicode
        :param new_name: New view name
        :type new_name: str | unicode
        :returns: True if view name renamed
        :rtype: bool
        """
        return self._search.rename_view(old_name, new_name)

    def delete_view(self, view):
        """Deletes given view

        :param view: Name of the view to be deleted
        :type view: str | unicode
        :returns: True if view deleted successfully
        :rtype: bool
        """
        return self._search.delete_view(view)

    def get_view_properties(self, view):
        """Get view properties

        :param view: View name whos properties we need to get.
        :type view: str | unicode
        :returns: returns properties of given view
        :rtype: dict
        """
        return self._search.get_view_properties(view)

    def update_view_properties(self, view, properties):
        """Updates properties of given view

        :param view: Name of the view
        :type view: str | unicode
        :param properties: Properties to be updated in given view
        :type properties: dict
        :returns: True if properties updated successfully
        :rtype: bool
        """
        return self._search.update_view_properties(view, properties)

    def search_in_collection(self, collection, search, bindVars=None, ttl=60):
        """Search a collection for string matches.

        :param collection: Collection name on which search has to be performed 
        :type collection: str | unicode
        :param search: search string needs to be search in given collection
        :type search: str | unicode
        :param bindVars: if there is c8ql in search text, we can pass bindVars for
                         c8ql query using bindVars param
        :type bindVars: dict | None
        :param ttl: default ttl will be 60 seconds
        :type ttl: int
        :returns: The specified search query will be executed for the collection.
                  The results of the search will be in the response. If there are too 
                  many results, an "id" will be specified for the cursor that can be 
                  used to obtain the remaining results.
        :rtype: [dict]
        """
        return self._search.search_in_collection(collection, search, bindVars, ttl)

    def get_list_of_analyzer(self):
        """Get list of all available analyzers

        :returns: Returns list of all available analyzers
        :rtype: [dict]
        """
        return self._search.get_list_of_analyzer()

    def get_analyzer_definition(self, name):
        """Gets given analyzer definition

        :param name: Name of the view
        :type name: str | unicode
        :returns: Definition of the given analyzer
        :rtype: dict
        """
        return self._search.get_analyzer_definition(name)

    def redis_set(self, key, value, collection, options=[]):
        """
        Set key to hold the string value. If key already holds a value,
        it is overwritten, regardless of its type. Any previous time to live
        associated with the key is discarded on successful SET operation.
        More on https://redis.io/commands/set/

        :param key: Key of the data
        :type key: str
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: SET options [NX | XX] [GET] [EX seconds | PX milliseconds |
        EXAT unix-time-seconds | PXAT unix-time-milliseconds | KEEPTTL]
        :type options: list
        :returns:
        :rtype:
        """
        redis_command = "SET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            value,
            *options
        )

    def redis_append(self, key, value, collection):
        """
        If key already exists and is a string, this command appends the value at the
        end of the string. If key does not exist it is created and set as an empty
        string, so APPEND will be similar to SET in this special case.
        More on https://redis.io/commands/append/

        :param key: Key of the data
        :type key: str
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "APPEND"
        return self._fabric.redis.command_parser(redis_command, collection, key, value)

    def redis_decr(self, key, collection):
        """
        Decrements the number stored at key by one. If the key does not exist,
        it is set to 0 before performing the operation. An error is returned if the
        key contains a value of the wrong type or contains a string that can not be
        represented as integer. This operation is limited to 64 bit signed integers.
        More on https://redis.io/commands/decr/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "DECR"
        return self._fabric.redis.command_parser(redis_command, collection, key)

    def redis_decrby(self, key, decrement, collection):
        """
        Decrements the number stored at key by decrement. If the key does not exist,
        it is set to 0 before performing the operation. An error is returned if the
        key contains a value of the wrong type or contains a string that can not be
        represented as integer. This operation is limited to 64 bit signed integers.
        More on https://redis.io/commands/decrby/

        :param key: Key of the data
        :type key: str
        :param decrement: Decrement number
        :type decrement: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "DECRBY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            decrement
        )

    def redis_get(self, key, collection):
        """
        Get the value of key. If the key does not exist the special value nil is
        returned. An error is returned if the value stored at key is not a string,
        because GET only handles string values.
        More on https://redis.io/commands/get/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "GET"
        return self._fabric.redis.command_parser(redis_command, collection, key)

    def redis_getdel(self, key, collection):
        """
        Get the value of key and delete the key. This command is similar to GET,
        except for the fact that it also deletes the key on success (if and only if
        the key's value type is a string).
        More on https://redis.io/commands/getdel/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "GETDEL"
        return self._fabric.redis.command_parser(redis_command, collection, key)

    def redis_getex(self, key, collection, expiry_command=None, time=None):
        """
        Get the value of key and optionally set its expiration. GETEX is similar to
        GET, but is a write command with additional options.
        More on https://redis.io/commands/getex/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param expiry_command: Redis expiry command (ex. EX, PX, EXAT, PXAT)
        :type expiry_command: str
        :param time: Redis expiry time (ex. sec, ms, unix-time-seconds,
        unix-time-milliseconds)
        :type time: str
        :returns:
        :rtype:
        """
        redis_command = "GETEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            expiry_command,
            time
        )

    def redis_getrange(self, key, start, end, collection):
        """
        Returns the substring of the string value stored at key, determined by the
        offsets start and end (both are inclusive). Negative offsets can be used in
        order to provide an offset starting from the end of the string. So -1 means
        the last character, -2 the penultimate and so forth.
        The function handles out of range requests by limiting the resulting range to
        the actual length of the string.
        More on https://redis.io/commands/getrange/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param start: Start string offset
        :type start: int
        :param end: End string offset
        :type end: int
        :returns:
        :rtype:
        """
        redis_command = "GETRANGE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            end
        )

    def redis_getset(self, key, value, collection):
        """
        Atomically sets key to value and returns the old value stored at key. Returns
        an error when key exists but does not hold a string value. Any previous time
        to live associated with the key is discarded on successful SET operation.
        More on https://redis.io/commands/getset/

        :param key: Key of the data
        :type key: str
        :param value: Start string offset
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "GETSET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            value
        )

    def redis_incr(self, key, collection):
        """
        Increments the number stored at key by one. If the key does not exist,
        it is set to 0 before performing the operation. An error is returned if the
        key contains a value of the wrong type or contains a string that can not be
        represented as integer. This operation is limited to 64 bit signed integers.
        More on https://redis.io/commands/incr/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "INCR"
        return self._fabric.redis.command_parser(redis_command, collection, key)

    def redis_incrby(self, key, increment, collection):
        """
        Increments the number stored at key by increment. If the key does not exist,
        it is set to 0 before performing the operation. An error is returned if the
        key contains a value of the wrong type or contains a string that can not be
        represented as integer. This operation is limited to 64 bit signed integers.
        More on https://redis.io/commands/incrby/

        :param key: Key of the data
        :type key: str
        :param increment: Increment of the data
        :type increment: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "INCRBY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            increment
        )

    def redis_incrbyfloat(self, key, increment, collection):
        """
        Increment the string representing a floating point number stored at key by
        the specified increment. By using a negative increment value, the result is
        that the value stored at the key is decremented (by the obvious properties of
        addition). If the key does not exist, it is set to 0 before performing the
        operation. An error is returned if one of the following conditions occur:

        The key contains a value of the wrong type (not a string).

        The current key content or the specified increment are not parsable as a double
        precision floating point number.

        :param key: Key of the data
        :type key: str
        :param increment: Increment of the data
        :type increment: float
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "INCRBYFLOAT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            increment
        )

    def redis_mget(self, keys, collection):
        """
        Returns the values of all specified keys. For every key that does not hold a
        string value or does not exist, the special value nil is returned. Because of
        this, the operation never fails.
        More on https://redis.io/commands/mget/

        :param keys: Keys of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "MGET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys
        )

    def redis_mset(self, data, collection):
        """
        Sets the given keys to their respective values. MSET replaces existing values
        with new values, just as regular SET. See MSETNX if you don't want to
        overwrite existing values.
        More on https://redis.io/commands/mset/

        :param data: Dictionary of the data
        :type data: dict
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        data_list = []
        for key, value in data.items():
            data_list.append(key)
            data_list.append(value)

        redis_command = "MSET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *data_list
        )

    def redis_psetex(self, key, milliseconds, value, collection):
        """
        Sets the given keys to their respective values. MSET replaces existing values
        with new values, just as regular SET. See MSETNX if you don't want to
        overwrite existing values.
        More on https://redis.io/commands/mset/

        :param key: Key of the data
        :type key: str
        :param milliseconds: TTL (time to leave) time of the data
        :type milliseconds: int
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "PSETEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            milliseconds,
            value
        )

    def redis_setbit(self, key, offset, value, collection):
        """
        Sets or clears the bit at offset in the string value stored at key.
        The bit is either set or cleared depending on value, which can be either 0 or 1.
        More on https://redis.io/commands/setbit/

        :param key: Key of the data
        :type key: str
        :param offset: Offset number
        :type offset: int
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SETBIT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            offset,
            value
        )

    def redis_msetnx(self, data, collection):
        """
        Sets the given keys to their respective values. MSETNX will not perform any
        operation at all even if just a single key already exists.
        More on https://redis.io/commands/msetnx/

        :param data: Dictionary of the data
        :type data: dict
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        data_list = []
        for key, value in data.items():
            data_list.append(key)
            data_list.append(value)

        redis_command = "MSETNX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *data_list
        )

    def redis_setex(self, key, seconds, value, collection):
        """
        Set key to hold the string value and set key to timeout after a given number of
        seconds.
        More on https://redis.io/commands/setex/

        :param key: Key of the data
        :type key: str
        :param seconds: TTL (time to leave) time of the data
        :type seconds: int
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SETEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            seconds,
            value
        )

    def redis_setnx(self, key, value, collection):
        """
        Set key to hold string value if key does not exist. In that case, it is equal to
        SET. When key already holds a value, no operation is performed.
        SETNX is short for "SET if Not eXists".
        More on https://redis.io/commands/setnx/

        :param key: Key of the data
        :type key: str
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SETNX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            value
        )

    def redis_setrange(self, key, offset, value, collection):
        """
        Overwrites part of the string stored at key, starting at the specified
        offset, for the entire length of value. If the offset is larger than the
        current length of the string at key, the string is padded with zero-bytes to
        make offset fit. Non-existing keys are considered as empty strings, so this
        command will make sure it holds a string large enough to be able to set value
        at offset.
        More on https://redis.io/commands/setrange/

        :param key: Key of the data
        :type key: str
        :param offset: Offset of the data
        :type offset: int
        :param value: Value of the data
        :type value: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SETRANGE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            offset,
            value
        )

    def redis_strlen(self, key, collection):
        """
        Returns the length of the string value stored at key.
        An error is returned when key holds a non-string value.
        More on https://redis.io/commands/strlen/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "STRLEN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_bitcount(self, key, collection, start=None, end=None, data_format=None):
        """
        By default all the bytes contained in the string are examined. It is possible
        to specify the counting operation only in an interval passing the additional
        arguments start and end.
        More on https://redis.io/commands/bitcount/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param start: Count start
        :type start: int
        :param end: Count stop
        :type end: int
        :param data_format: Count format [BYTE | BIT]
        :type data_format: str
        :returns:
        :rtype:
        """
        redis_command = "BITCOUNT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            end,
            data_format
        )

    def redis_bitop(self, operation, deskey, keys, collection):
        """
        Perform a bitwise operation between multiple keys (containing string values) and
        store the result in the destination key.
        More on https://redis.io/commands/bitop/

        :param operation: Operation AND, OR, XOR and NOT
        :type operation: str
        :param deskey: Destination key where operation is stored
        :type deskey: str
        :param keys: List of keys to perform operation on
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "BITOP"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            operation,
            deskey,
            *keys
        )

    def redis_getbit(self, key, offset, collection):
        """
        Returns the bit value at offset in the string value stored at key.
        More on https://redis.io/commands/getbit/

        :param key: Key of the data
        :type key: str
        :param offset: Offset of the data
        :type offset: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "GETBIT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            offset,
        )

    def redis_bitpos(
            self,
            key,
            bit,
            collection,
            start=None,
            end=None,
            data_format=None
    ):
        """
        Return the position of the first bit set to 1 or 0 in a string.
        The position is returned, thinking of the string as an array of bits from left
        to right, where the first byte's most significant bit is at position 0, the
        second byte's most significant bit is at position 8, and so forth.
        More on https://redis.io/commands/bitpos/

        :param key: Key of the data
        :type key: str
        :param bit: Key of the data
        :type bit: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param start: Count start
        :type start: int
        :param end: Count stop
        :type end: int
        :param data_format: Count format [BYTE | BIT]
        :type data_format: str
        :returns:
        :rtype:
        """
        redis_command = "BITPOS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            bit,
            start,
            end,
            data_format
        )

    def redis_lpush(self, key, elements, collection):
        """
        Insert all the specified values at the head of the list stored at key. If key
        does not exist, it is created as empty list before performing the push
        operations. When key holds a value that is not a list, an error is returned.
        So for instance the command LPUSH mylist a b c will result into a list
        containing c as first element, b as second element and a as third element.
        More on https://redis.io/commands/lpush/

        :param key: Key of the data
        :type key: str
        :param elements: List of the data
        :type elements: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LPUSH"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *elements
        )

    def redis_lindex(self, key, index, collection):
        """
        Returns the element at index index in the list stored at key. The index is
        zero-based, so 0 means the first element, 1 the second element and so on.
        Negative indices can be used to designate elements starting at the tail of
        the list. Here, -1 means the last element, -2 means the penultimate and so
        forth.
        More on https://redis.io/commands/lindex/

        :param key: Key of the data
        :type key: str
        :param index: Index of data
        :type index: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LINDEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            index
        )

    def redis_linsert(self, key, modifier, pivot, element, collection):
        """
        Inserts element in the list stored at key either before or after the reference
        value pivot.
        More on https://redis.io/commands/linsert/

        :param key: Key of the data
        :type key: str
        :param modifier: It can be BEFORE | AFTER
        :type modifier: str
        :param pivot: Pivot is reference value
        :type pivot: str
        :param element: New element to be added
        :type element: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LINSERT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            modifier,
            pivot,
            element
        )

    def redis_llen(self, key, collection):
        """
        Returns the length of the list stored at key. If key does not exist,
        it is interpreted as an empty list and 0 is returned. An error is returned
        when the value stored at key is not a list.
        More on https://redis.io/commands/linsert/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LLEN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_lrange(self, key, start, stop, collection):
        """
        Insert all the specified values at the head of the list stored at key. If key
        does not exist, it is created as empty list before performing the push
        operations. When key holds a value that is not a list, an error is returned.
        It is possible to push multiple elements using a single command call just
        specifying multiple members of the list in elements parameter.
        More on https://redis.io/commands/lrange/

        :param key: Key of the data
        :type key: str
        :param start: Start of the data
        :type start: int
        :param stop: Stop of the data
        :type stop: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LRANGE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            stop
        )

    def redis_lmove(self, source, destination, where_from, where_to, collection):
        """
        Atomically returns and removes the first/last element (head/tail depending on
        the wherefrom argument) of the list stored at source, and pushes the element
        at the first/last element (head/tail depending on the whereto argument) of
        the list stored at destination.
        More on https://redis.io/commands/lmove/

        :param source: Source list
        :type source: str
        :param destination: Destination list
        :type destination: str
        :param where_from: From where to move <LEFT | RIGHT>
        :type where_from: str
        :param where_to: Position to move in <LEFT | RIGHT>
        :type where_to: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LMOVE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            source,
            destination,
            where_from,
            where_to
        )

    def redis_lpos(
            self,
            key,
            element,
            collection,
            rank=None,
            count=None,
            max_len=None
    ):
        """
        The command returns the index of matching elements inside a Redis list. By
        default, when no options are given, it will scan the list from head to tail,
        looking for the first match of "element". The optional arguments and options
        can modify the command's behavior. The RANK option specifies the "rank" of
        the first element to return, in case there are multiple matches. A rank of 1
        means to return the first match, 2 to return the second match, and so forth.
        Sometimes we want to return not just the Nth matching element, but the
        position of all the first N matching elements. This can be achieved using the
        COUNT option.
        Finally, the MAXLEN option tells the command to compare the provided element
        only with a given maximum number of list items
        More on https://redis.io/commands/scan/

        :param key: Key of the data
        :type key: str
        :param element: Element to match
        :type element: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param rank: A rank of 1 means to return the first match, 2 to return the second
        match, and so forth.
        :type rank: str
        :param count: count is the number of results
        :type count: int
        :param max_len: compare the provided element only with a given maximum number of
        list items
        :type max_len: int
        :returns:
        :rtype:
        """
        redis_command = "LPOS"
        rank_list = []
        if rank is not None:
            rank_list.append("RANK")
            rank_list.append(rank)

        count_list = []
        if count is not None:
            count_list.append("COUNT")
            count_list.append(count)

        max_len_list = []
        if max_len is not None:
            max_len_list.append("MAXLEN")
            max_len_list.append(max_len)

        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            element,
            *rank_list,
            *count_list,
            *max_len_list
        )

    def redis_rpush(self, key, elements, collection):
        """
        Insert all the specified values at the tail of the list stored at key. If key
        does not exist, it is created as empty list before performing the push
        operation. When key holds a value that is not a list, an error is returned.
        So for instance the command RPUSH mylist a b c will result into a list
        containing a as first element, b as second element and c as third element.
        More on https://redis.io/commands/rpush/

        :param key: Key of the data
        :type key: str
        :param elements: List of the data
        :type elements: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RPUSH"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *elements
        )

    def redis_lpop(self, key, collection, count=None, ):
        """
        Removes and returns the first elements of the list stored at key. By default,
        the command pops a single element from the beginning of the list. When
        provided with the optional count argument, the reply will consist of up to
        count elements, depending on the list's length.
        More on https://redis.io/commands/lpop/

        :param key: Key of the list
        :type key: str
        :param count: Count number of elements to pop
        :type count: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LPOP"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count,
        )

    def redis_lpushx(self, key, elements, collection):
        """
        Inserts specified values at the head of the list stored at key, only if key
        already exists and holds a list. In contrary to LPUSH, no operation will be
        performed when key does not yet exist.
        More on https://redis.io/commands/lpushx/

        :param key: Key of the data
        :type key: str
        :param elements: List of the data
        :type elements: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LPUSHX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *elements
        )

    def redis_rpushx(self, key, elements, collection):
        """
        Inserts specified values at the tail of the list stored at key, only if key
        already exists and holds a list. In contrary to RPUSH, no operation will be
        performed when key does not yet exist.
        More on https://redis.io/commands/rpushx/

        :param key: Key of the data
        :type key: str
        :param elements: List of the data
        :type elements: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RPUSHX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *elements
        )

    def redis_lrem(self, key, count, element, collection):
        """
        Removes the first count occurrences of elements equal to element from the list
        stored at key. The count argument influences the operation in the following
        ways:
        count > 0: Remove elements equal to element moving from head to tail.
        count < 0: Remove elements equal to element moving from tail to head.
        count = 0: Remove all elements equal to element.
        More on https://redis.io/commands/lrem/

        :param key: Key of the data
        :type key: str
        :param count: Number of elements to be removed
        :type count: int
        :param element: List element
        :type element: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LREM"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count,
            element
        )

    def redis_lset(self, key, index, element, collection):
        """
        Sets the list element at index to element. For more information on the index
        argument, see LINDEX.
        More on https://redis.io/commands/lset/

        :param key: Key of the data
        :type key: str
        :param index: Index of element
        :type index: int
        :param element: List element
        :type element: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LSET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            index,
            element
        )

    def redis_ltrim(self, key, start, stop, collection):
        """
        Trim an existing list so that it will contain only the specified range of
        elements specified. Both start and stop are zero-based indexes, where 0 is
        the first element of the list (the head), 1 the next element and so on.
        More on https://redis.io/commands/ltrim/

        :param key: Key of the data
        :type key: str
        :param start: Start index of element
        :type start: int
        :param stop: Stop index of element
        :type stop: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "LTRIM"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            stop
        )

    def redis_rpop(self, key, collection, count=None, ):
        """
        Removes and returns the last elements of the list stored at key.
        By default, the command pops a single element from the end of the list. When
        provided with the optional count argument, the reply will consist of up to count
        elements, depending on the list's length.
        More on https://redis.io/commands/rpop/

        :param key: Key of the list
        :type key: str
        :param count: Count number of elements to pop
        :type count: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RPOP"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count,
        )

    def redis_rpoplpush(self, source, destination, collection):
        """
        Atomically returns and removes the first/last element (head/tail depending on
        the wherefrom argument) of the list stored at source, and pushes the element
        at the first/last element (head/tail depending on the whereto argument) of
        the list stored at destination.
        More on https://redis.io/commands/lmove/

        :param source: Source list
        :type source: str
        :param destination: Destination list
        :type destination: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RPOPLPUSH"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            source,
            destination,
        )

    def redis_hset(self, key, data, collection):
        """
        Sets field in the hash stored at key to value. If key does not exist,
        a new key holding a hash is created. If field already exists in the hash,
        it is overwritten.
        More on https://redis.io/commands/hset/

        :param key: Key of the data
        :type key: str
        :param data:  Dictionary of the data
        :type data: dict
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        data_list = []
        for dict_key, dict_value in data.items():
            data_list.append(dict_key)
            data_list.append(dict_value)

        redis_command = "HSET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *data_list
        )

    def redis_hget(self, key, field, collection):
        """
        Returns the value associated with field in the hash stored at key.
        More on https://redis.io/commands/hget/

        :param key: Key of the data
        :type key: str
        :param field: Value of the data
        :type field: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HGET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            field
        )

    def redis_hdel(self, key, fields, collection):
        """
        Removes the specified fields from the hash stored at key. Specified fields
        that do not exist within this hash are ignored. If key does not exist,
        it is treated as an empty hash and this command returns 0
        More on https://redis.io/commands/hdel/

        :param key: Key of the data
        :type key: str
        :param fields: Fields of the data
        :type fields: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HDEL"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *fields
        )

    def redis_hexists(self, key, field, collection):
        """
        Returns if field is an existing field in the hash stored at key.
        More on https://redis.io/commands/hexists/

        :param key: Key of the data
        :type key: str
        :param field: Field of the data
        :type field: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HEXISTS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            field
        )

    def redis_hgetall(self, key, collection):
        """
        Returns all fields and values of the hash stored at key. In the returned
        value, every field name is followed by its value, so the length of the reply
        is twice the size of the hash.
        More on https://redis.io/commands/hgetall/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HGETALL"
        return self._fabric.redis.command_parser(redis_command, collection, key)

    def redis_hincrby(self, key, field, increment, collection):
        """
        Increments the number stored at field in the hash stored at key by increment.
        If key does not exist, a new key holding a hash is created. If field does not
        exist the value is set to 0 before the operation is performed.
        More on https://redis.io/commands/hincrby/

        :param key: Key of the data
        :type key: str
        :param field: Field of the data
        :type field: str
        :param increment: Increment number
        :type increment: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HINCRBY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            field,
            increment
        )

    def redis_hincrbyfloat(self, key, field, increment, collection):
        """
        Increment the specified field of a hash stored at key, and representing a
        floating point number, by the specified increment. If the increment value is
        negative, the result is to have the hash field value decremented instead of
        incremented. If the field does not exist, it is set to 0 before performing
        the operation. An error is returned if one of the following conditions occur:

        The field contains a value of the wrong type (not a string).
        The current field content or the specified increment are not parsable as a
        double precision floating point number.
        More on https://redis.io/commands/hincrbyfloat/

        :param key: Key of the data
        :type key: str
        :param field: Field of the data
        :type field: str
        :param increment: Increment number
        :type increment: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HINCRBYFLOAT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            field,
            increment
        )

    def redis_hkeys(self, key, collection):
        """
        Returns all field names in the hash stored at key.
        More on https://redis.io/commands/hkeys/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HKEYS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_hlen(self, key, collection):
        """
        Returns the number of fields contained in the hash stored at key.
        More on https://redis.io/commands/hlen/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HLEN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_hmget(self, key, fields, collection):
        """
        Returns the values associated with the specified fields in the hash stored at
        key. For every field that does not exist in the hash, a nil value is returned.
        Because non-existing keys are treated as empty hashes, running HMGET against a
        non-existing key will return a list of nil values.
        More on https://redis.io/commands/hmget/

        :param key: Key of the data
        :type key: str
        :param fields: Fields of the data
        :type fields: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HMGET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *fields
        )

    def redis_hmset(self, key, data, collection):
        """
        Sets the specified fields to their respective values in the hash stored at
        key. This command overwrites any specified fields already existing in the
        hash. If key does not exist, a new key holding a hash is created. More on
        More on https://redis.io/commands/hmset/

        :param key: Key of the data
        :type key: str
        :param data: Dictionary of the data
        :type data: dict
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        data_list = []
        for dict_key, dict_value in data.items():
            data_list.append(dict_key)
            data_list.append(dict_value)

        redis_command = "HMSET"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *data_list
        )

    def redis_hscan(self, key, cursor, collection, pattern=None, count=None):
        """
        The SCAN command and the closely related commands SSCAN, HSCAN and ZSCAN are
        used in order to incrementally iterate over a collection of elements.
        More on https://redis.io/commands/scan/

        :param key: Key of the data
        :type key: str
        :param cursor: Cursor value (start with 0)
        :type cursor: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param pattern: It is possible to only iterate elements matching a given
        glob-style pattern
        :type pattern: str
        :param count: COUNT the user specified the amount of work that should be done at
        every call in order to retrieve elements from the collection
        :type count: int
        :returns:
        :rtype:
        """
        redis_command = "HSCAN"
        pattern_list = []
        if pattern is not None:
            pattern_list.append("MATCH")
            pattern_list.append(pattern)

        count_list = []
        if count is not None:
            count_list.append("COUNT")
            count_list.append(count)

        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            cursor,
            *pattern_list,
            *count_list
        )

    def redis_hstrlen(self, key, field, collection):
        """
        Returns the string length of the value associated with field in the hash stored
        at key. If the key or the field do not exist, 0 is returned.
        More on https://redis.io/commands/hstrlen/

        :param key: Key of the data
        :type key: str
        :param field: Field of the data
        :type field: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HSTRLEN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            field,
        )

    def redis_hrandfield(self, key, collection, count=None, modifier=None):
        """
        When called with just the key argument, return a random field from the hash
        value stored at key. f the provided count argument is positive, return an
        array of distinct fields. The array's length is either count or the hash's
        number of fields (HLEN), whichever is lower.
        The optional WITHVALUES modifier changes the reply so it includes the respective
        values of the randomly selected hash fields.
        More on https://redis.io/commands/hrandfield/

        :param key: Key of the data
        :type key: str
        :param count: Count of the data
        :type count: int
        :param modifier: The optional WITHVALUES modifier
        :type modifier: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HRANDFIELD"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count,
            modifier,
        )

    def redis_hvals(self, key, collection):
        """
        Returns all values in the hash stored at key.
        More on https://redis.io/commands/hvals/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "HVALS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_sadd(self, key, members, collection):
        """
        Add the specified members to the set stored at key. Specified members that
        are already a member of this set are ignored. If key does not exist,
        a new set is created before adding the specified members.
        More on https://redis.io/commands/sadd/

        :param key: Key of the data
        :type key: str
        :param members: list of members
        :type members: List
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SADD"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *members
        )

    def redis_scard(self, key, collection):
        """
        Returns the set cardinality (number of elements) of the set stored at key.
        More on https://redis.io/commands/scard/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SCARD"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_sdiff(self, keys, collection):
        """
        Returns the members of the set resulting from the difference between the first
        set and all the successive sets.
        More on https://redis.io/commands/sdiff/

        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SDIFF"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys,
        )

    def redis_sdiffstore(self, destination, keys, collection):
        """
        This command is equal to SDIFF, but instead of returning the resulting set, it
        is stored in destination.
        More on https://redis.io/commands/sdiffstore/

        :param destination: Key of the destination location
        :type destination: string
        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SDIFFSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            *keys,
        )

    def redis_sinter(self, keys, collection):
        """
        Returns the members of the set resulting from the intersection of all the given
        sets.
        More on https://redis.io/commands/sinter/

        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SINTER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys,
        )

    def redis_sinterstore(self, destination, keys, collection):
        """
        This command is equal to SINTER, but instead of returning the resulting set, it
        is stored in destination.
        More on https://redis.io/commands/sinterstore/

        :param destination: Key of the destination location
        :type destination: string
        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SINTERSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            *keys,
        )

    def redis_sismember(self, key, member, collection):
        """
        Returns if member is a member of the set stored at key.
        More on https://redis.io/commands/sismember/

        :param key: Key of the data
        :type key: str
        :param member: list of members
        :type member: string
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SISMEMBER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            member
        )

    def redis_smembers(self, key, collection):
        """
        Returns all the members of the set value stored at key.
        More on https://redis.io/commands/smembers/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SMEMBERS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_smismember(self, key, members, collection):
        """
        Returns whether each member is a member of the set stored at key.
        For every member, 1 is returned if the value is a member of the set, or 0 if the
        element is not a member of the set or if key does not exist.
        More on https://redis.io/commands/smismember/

        :param key: Key of the data
        :type key: str
        :param members: list of members
        :type members: List
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SMISMEMBER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *members
        )

    def redis_smove(self, source, destination, member, collection):
        """
        Move member from the set at source to the set at destination. This operation is
        atomic. In every given moment the element will appear to be a member of source
        or destination for other clients.
        More on https://redis.io/commands/smove/

        :param source: Source set
        :type source: str
        :param destination: Destination set
        :type destination: str
        :param member: Member of the set to be moved
        :type member: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SMOVE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            source,
            destination,
            member
        )

    def redis_spop(self, key, count, collection):
        """
        Removes and returns one or more random members from the set value store at key.
        This operation is similar to SRANDMEMBER, that returns one or more random
        elements from a set but does not remove it.
        More on https://redis.io/commands/spop/

        :param key: Key of the data
        :type key: str
        :param count: Count of the data
        :type count: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SPOP"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count
        )

    def redis_srandmember(self, key, collection, count=None):
        """
        When called with just the key argument, return a random element from the set
        value stored at key. If the provided count argument is positive, return an array
        of distinct elements. The array's length is either count or the set's
        cardinality (SCARD), whichever is lower.
        More on https://redis.io/commands/srandmember/

        :param key: Key of the data
        :type key: str
        :param count: Count of the data
        :type count: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SRANDMEMBER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count
        )

    def redis_srem(self, key, members, collection):
        """
        Remove the specified members from the set stored at key. Specified members that
        are not a member of this set are ignored. If key does not exist, it is treated
        as an empty set and this command returns 0.
        More on https://redis.io/commands/srem/

        :param key: Key of the data
        :type key: str
        :param members: list of members
        :type members: List
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SREM"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *members
        )

    def redis_sscan(self, key, cursor, collection, pattern=None, count=None):
        """
        The SCAN command and the closely related commands SSCAN, HSCAN and ZSCAN are
        used in order to incrementally iterate over a collection of elements.
        More on https://redis.io/commands/scan/

        :param key: Key of the data
        :type key: str
        :param cursor: Cursor value (start with 0)
        :type cursor: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param pattern: It is possible to only iterate elements matching a given
        glob-style pattern
        :type pattern: str
        :param count: COUNT the user specified the amount of work that should be done at
        every call in order to retrieve elements from the collection
        :type count: int
        :returns:
        :rtype:
        """
        redis_command = "SSCAN"
        pattern_list = []
        if pattern is not None:
            pattern_list.append("MATCH")
            pattern_list.append(pattern)

        count_list = []
        if count is not None:
            count_list.append("COUNT")
            count_list.append(count)

        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            cursor,
            *pattern_list,
            *count_list
        )

    def redis_sunion(self, keys, collection):
        """
        Returns the members of the set resulting from the union of all the given sets.
        More on https://redis.io/commands/sunion/

        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SUNION"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys,
        )

    def redis_sunionstore(self, destination, keys, collection):
        """
        This command is equal to SUNION, but instead of returning the resulting set, it
        is stored in destination.
        More on https://redis.io/commands/sunionstore/

        :param destination: Key of the destination location
        :type destination: string
        :param keys: Key of the data
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "SUNIONSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            *keys,
        )

    def redis_zadd(
            self,
            key,
            data,
            collection,
            options=[]
    ):
        """
        Adds all the specified members with the specified scores to the sorted set
        stored at key. It is possible to specify multiple score / member pairs. If a
        specified member is already a member of the sorted set, the score is updated
        and the element reinserted at the right position to ensure the correct
        ordering.
        More on https://redis.io/commands/zadd/

        :param key: Key of the sorted set
        :type key: str
        :param data: List of score member data ex. [0, "test0", 1, "test1"]
        :type data: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZADD options [NX | XX] [GT | LT] [CH] [INCR]
        :type options: list
        :returns:
        :rtype:
        """
        redis_command = "ZADD"

        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *options,
            *data
        )

    def redis_zcard(self, key, collection):
        """
        Returns the sorted set cardinality (number of elements) of the sorted set stored
        at key.
        More on https://redis.io/commands/zcard/

        :param key: Key of the sorted set
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZCARD"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_zcount(self, key, minimum, maximum, collection):
        """
        Returns the number of elements in the sorted set at key with a score between min
        and max.
        The min and max arguments have the same semantic as described for ZRANGEBYSCORE.
        More on https://redis.io/commands/zcount/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: int
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZCOUNT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum
        )

    def redis_zdiff(self, num_keys, keys, collection, with_scores=False):
        """
        This command is similar to ZDIFFSTORE, but instead of storing the resulting
        sorted set, it is returned to the client.
        More on https://redis.io/commands/zdiff/

        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """

        if with_scores is True:
            with_scores_command = "WITHSCORES"
        else:
            with_scores_command = None

        redis_command = "ZDIFF"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            num_keys,
            *keys,
            with_scores_command
        )

    def redis_zdiffstore(self, destination, num_keys, keys, collection):
        """
        Computes the difference between the first and all successive input sorted
        sets and stores the result in destination. The total number of input keys is
        specified by numkeys.
        More on https://redis.io/commands/zdiffstore/

        :param destination: Destination key to store result
        :type destination: str
        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """

        redis_command = "ZDIFFSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            num_keys,
            *keys,
        )

    def redis_zincrby(self, key, increment, member, collection):
        """
        Increments the score of member in the sorted set stored at key by increment.
        If member does not exist in the sorted set, it is added with increment as its
        score (as if its previous score was 0.0). If key does not exist, a new sorted
        set with the specified member as its sole member is created.
        More on https://redis.io/commands/zincrby/

        :param key: Key of the sorted set
        :type key: str
        :param increment: Value that increments score of the member
        :type increment: float
        :param member: Member to be incremented
        :type member: string
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZINCRBY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            increment,
            member
        )

    def redis_zinter(
            self,
            num_keys,
            keys,
            collection,
            options=None,
            with_scores=False
    ):
        """
        This command is similar to ZINTERSTORE, but instead of storing the resulting
        sorted set, it is returned to the client.
        For a description of the WEIGHTS and AGGREGATE options, see ZUNIONSTORE.
        More on https://redis.io/commands/zinter/

        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZINTER options [WEIGHTS weight [weight ...]]
        [AGGREGATE <SUM | MIN | MAX>]
        :type options: list
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """

        options_command = []
        if options is not None:
            options_command = list(options)

        if with_scores is True:
            options_command.append("WITHSCORES")

        redis_command = "ZINTER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            num_keys,
            *keys,
            *options_command,
        )

    def redis_zinterstore(
            self,
            destination,
            num_keys,
            keys,
            collection,
            options=[]
    ):
        """
        Computes the intersection of numkeys sorted sets given by the specified keys,
        and stores the result in destination. It is mandatory to provide the number
        of input keys (numkeys) before passing the input keys and the other (
        optional) arguments. For a description of the WEIGHTS and AGGREGATE options,
        see ZUNIONSTORE.
        More on https://redis.io/commands/zinterstore/

        :param destination: Destination key to store result
        :type destination: str
        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZINTER options [WEIGHTS weight [weight ...]]
        [AGGREGATE <SUM | MIN | MAX>]
        :type options: list
        :returns:
        :rtype:
        """
        redis_command = "ZINTERSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            num_keys,
            *keys,
            *options,
        )

    def redis_zlexcount(self, key, minimum, maximum, collection):
        """
        When all the elements in a sorted set are inserted with the same score,
        in order to force lexicographical ordering, this command returns the number
        of elements in the sorted set at key with a value between min and max.
        The min and max arguments have the same meaning as described for ZRANGEBYLEX.
        More on https://redis.io/commands/zlexcount/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: str
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZLEXCOUNT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum
        )

    def redis_zmscore(self, key, members, collection):
        """
        Returns the scores associated with the specified members in the sorted set
        stored at key.
        More on https://redis.io/commands/zmscore/

        :param key: Key of the sorted set
        :type key: str
        :param members: Members list of the sorted set
        :type members: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZMSCORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *members
        )

    def redis_zpopmax(self, key, collection, count=None):
        """
        Removes and returns up to count members with the highest scores in the sorted
        set stored at key. When left unspecified, the default value for count is 1.
        More on https://redis.io/commands/zpopmax/

        :param key: Key of the sorted set
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param count: Number of elements to be removed
        :type count: int
        :returns:
        :rtype:
        """
        redis_command = "ZPOPMAX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count
        )

    def redis_zpopmin(self, key, collection, count=None):
        """
        Removes and returns up to count members with the lowest scores in the sorted set
        stored at key.
        When left unspecified, the default value for count is 1
        More on https://redis.io/commands/zpopmin/

        :param key: Key of the sorted set
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param count: Number of elements to be removed
        :type count: int
        :returns:
        :rtype:
        """
        redis_command = "ZPOPMIN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count
        )

    def redis_zrandmember(self, key, collection, count=None, with_scores=False):
        """
        When called with just the key argument, return a random element from the
        sorted set value stored at key. If the provided count argument is positive,
        return an array of distinct elements. The array's length is either count or
        the sorted set's cardinality (ZCARD), whichever is lower.
        More on https://redis.io/commands/zrandmember/

        :param key: Key of the sorted set
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param count: Number of elements to be removed
        :type count: int
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """
        if with_scores is True:
            with_scores_command = "WITHSCORES"
        else:
            with_scores_command = None

        redis_command = "ZRANDMEMBER"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            count,
            with_scores_command
        )

    def redis_zrange(self, key, start, stop, collection, options=[]):
        """
        Returns the specified range of elements in the sorted set stored at <key>.
        ZRANGE can perform different types of range queries: by index (rank), by the
        score, or by lexicographical order.
        More on https://redis.io/commands/zrange/

        :param key: Key of the sorted set
        :type key: str
        :param start: Start of the data
        :type start: int
        :param stop: Stop of the data
        :type stop: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZRANGE options [BYSCORE | BYLEX] [REV]
        [LIMIT offset count] [WITHSCORES]
        :type options: list
        :returns:
        :rtype:
        """
        redis_command = "ZRANGE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            stop,
            *options
        )

    def redis_zrangebylex(
            self,
            key,
            minimum,
            maximum,
            collection,
            offset=None,
            count=None
    ):
        """When all the elements in a sorted set are inserted with the same score,
        in order to force lexicographical ordering, this command returns all the
        elements in the sorted set at key with a value between min and max.
        If the elements in the sorted set have different scores, the returned elements
        are unspecified.
        The optional LIMIT argument can be used to only get a range of the matching
        elements (similar to SELECT LIMIT offset, count in SQL)
        More on https://redis.io/commands/zrangebylex/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: str
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param offset: Offset of the limit parameter
        :type offset: str
        :param count: Count of the limit parameter
        :type count: int
        :returns:
        :rtype:
        """
        limit_list = []
        if offset and count is not None:
            limit_list.append("LIMIT")
            limit_list.append(offset)
            limit_list.append(count)

        redis_command = "ZRANGEBYLEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum,
            *limit_list
        )

    def redis_zrangebyscore(
            self,
            key,
            minimum,
            maximum,
            collection,
            with_scores=None,
            offset=None,
            count=None
    ):
        """When all the elements in a sorted set are inserted with the same score,
        in order to force lexicographical ordering, this command returns all the
        elements in the sorted set at key with a value between min and max.
        If the elements in the sorted set have different scores, the returned elements
        are unspecified.
        The optional LIMIT argument can be used to only get a range of the matching
        elements (similar to SELECT LIMIT offset, count in SQL)
        More on https://redis.io/commands/zrangebyscore/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: str
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param with_scores: Return score of member
        :type with_scores: bool
        :param offset: Offset of the limit parameter
        :type offset: str
        :param count: Count of the limit parameter
        :type count: int
        :returns:
        :rtype:
        """
        if with_scores is True:
            with_scores_command = "WITHSCORES"
        else:
            with_scores_command = None

        limit_list = []
        if offset and count is not None:
            limit_list.append("LIMIT")
            limit_list.append(offset)
            limit_list.append(count)

        redis_command = "ZRANGEBYSCORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum,
            with_scores_command,
            *limit_list
        )

    def redis_zrangestore(self, dst, key, minimum, maximum, collection, options=None):
        """
        This command is like ZRANGE, but stores the result in the <dst> destination key.
        More on https://redis.io/commands/zrange/

        :param dst: Key of the destination location
        :type dst: string
        :param key: Key of the sorted set
        :type key: str
        :param minimum: Start of the data
        :type minimum: str
        :param maximum: Stop of the data
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZRANGE options [BYSCORE | BYLEX] [REV]
        [LIMIT offset count] [WITHSCORES]
        :type options: list
        :returns:
        :rtype:
        """
        redis_command = "ZRANGESTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            dst,
            key,
            minimum,
            maximum,
            *options
        )

    def redis_zrank(self, key, member, collection):
        """
        Returns the rank of member in the sorted set stored at key, with the scores
        ordered from low to high. The rank (or index) is 0-based, which means that
        the member with the lowest score has rank 0.
        More on https://redis.io/commands/zrank/

        :param key: Key of the sorted set
        :type key: str
        :param member: Member of the sorted set
        :type member: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZRANK"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            member
        )

    def redis_zrem(self, key, members, collection):
        """
        Removes the specified members from the sorted set stored at key. Non existing
        members are ignored.
        An error is returned when key exists and does not hold a sorted set.
        More on https://redis.io/commands/zrem/

        :param key: Key of the sorted set
        :type key: str
        :param members: List of members of the sorted set to be removed
        :type members: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZREM"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            *members
        )

    def redis_zremrangebylex(
            self,
            key,
            minimum,
            maximum,
            collection,
    ):
        """
        When all the elements in a sorted set are inserted with the same score,
        in order to force lexicographical ordering, this command removes all elements
        in the sorted set stored at key between the lexicographical range specified
        by min and max.
        The meaning of min and max are the same of the ZRANGEBYLEX command.
        More on https://redis.io/commands/zremrangebylex/

        :param key: Key of the sorted set
        :type key: str
        :param minimum: Minimum parameter of the data
        :type minimum: str
        :param maximum: Maximum parameter of the data
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZREMRANGEBYLEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum
        )

    def redis_zremrangebyrank(
            self,
            key,
            start,
            stop,
            collection,
    ):
        """
        Removes all elements in the sorted set stored at key with rank between start
        and stop. Both start and stop are 0 -based indexes with 0 being the element
        with the lowest score. These indexes can be negative numbers, where they
        indicate offsets starting at the element with the highest score. For example:
        -1 is the element with the highest score, -2 the element with the second
        highest score and so forth.
        More on https://redis.io/commands/zremrangebyrank/

        :param key: Key of the sorted set
        :type key: str
        :param start: Start of the data
        :type start: str
        :param stop: Stop of the data
        :type stop: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZREMRANGEBYRANK"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            stop
        )

    def redis_zremrangebyscore(
            self,
            key,
            minimum,
            maximum,
            collection,
    ):
        """
        Removes all elements in the sorted set stored at key with a score between min
        and max (inclusive).
        More on https://redis.io/commands/zremrangebyscore/

        :param key: Key of the sorted set
        :type key: str
        :param minimum: Minimum parameter of the data
        :type minimum: str
        :param maximum: Maximum parameter of the data
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZREMRANGEBYSCORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum
        )

    def redis_zrevrange(self, key, start, stop, collection, with_scores=False):
        """
        Returns the specified range of elements in the sorted set stored at key. The
        elements are considered to be ordered from the highest to the lowest score.
        Descending lexicographical order is used for elements with equal score.
        Apart from the reversed ordering, ZREVRANGE is similar to ZRANGE.
        More on https://redis.io/commands/zrevrange/

        :param key: Key of the sorted set
        :type key: str
        :param start: Start of the data
        :type start: int
        :param stop: Stop of the data
        :type stop: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """
        if with_scores is True:
            with_scores_command = "WITHSCORES"
        else:
            with_scores_command = None

        redis_command = "ZREVRANGE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            start,
            stop,
            with_scores_command
        )

    def redis_zrevrangebylex(
            self,
            key,
            minimum,
            maximum,
            collection,
            offset=None,
            count=None
    ):
        """When all the elements in a sorted set are inserted with the same score,
        in order to force lexicographical ordering, this command returns all the
        elements in the sorted set at key with a value between max and min.
        Apart from the reversed ordering, ZREVRANGEBYLEX is similar to ZRANGEBYLEX.
        The optional LIMIT argument can be used to only get a range of the matching
        elements (similar to SELECT LIMIT offset, count in SQL) More on
        https://redis.io/commands/zrevrangebylex/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: str
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param offset: Offset of the limit parameter
        :type offset: str
        :param count: Count of the limit parameter
        :type count: int
        :returns:
        :rtype:
        """
        limit_list = []
        if offset and count is not None:
            limit_list.append("LIMIT")
            limit_list.append(offset)
            limit_list.append(count)

        redis_command = "ZREVRANGEBYLEX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum,
            *limit_list
        )

    def redis_zrevrangebyscore(
            self,
            key,
            minimum,
            maximum,
            collection,
            with_scores=None,
            offset=None,
            count=None
    ):
        """Returns all the elements in the sorted set at key with a score between max
        and min (including elements with score equal to max or min). In contrary to
        the default ordering of sorted sets, for this command the elements are
        considered to be ordered from high to low scores.
        Apart from the reversed ordering, ZREVRANGEBYSCORE is similar to ZRANGEBYSCORE.
        The optional LIMIT argument can be used to only get a range of the matching
        elements (similar to SELECT LIMIT offset, count in SQL)
        More on https://redis.io/commands/zrevrangebyscore/

        :param key: Key of the data
        :type key: str
        :param minimum: Minimum score
        :type minimum: str
        :param maximum: Maximum score
        :type maximum: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param with_scores: Return score of member
        :type with_scores: bool
        :param offset: Offset of the limit parameter
        :type offset: str
        :param count: Count of the limit parameter
        :type count: int
        :returns:
        :rtype:
        """
        if with_scores is True:
            with_scores_command = "WITHSCORES"
        else:
            with_scores_command = None

        limit_list = []
        if offset and count is not None:
            limit_list.append("LIMIT")
            limit_list.append(offset)
            limit_list.append(count)

        redis_command = "ZREVRANGEBYSCORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            minimum,
            maximum,
            with_scores_command,
            *limit_list
        )

    def redis_zrevrank(self, key, member, collection):
        """
        Returns the rank of member in the sorted set stored at key, with the scores
        ordered from high to low. The rank (or index) is 0-based, which means that
        the member with the highest score has rank 0.
        More on https://redis.io/commands/zrevrank/

        :param key: Key of the sorted set
        :type key: str
        :param member: Member of the sorted set
        :type member: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZREVRANK"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            member
        )

    def redis_zscan(self, key, cursor, collection, pattern=None, count=None):
        """
        The SCAN command and the closely related commands SSCAN, HSCAN and ZSCAN are
        used in order to incrementally iterate over a collection of elements.
        More on https://redis.io/commands/scan/

        :param key: Key of the data
        :type key: str
        :param cursor: Cursor value (start with 0)
        :type cursor: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param pattern: It is possible to only iterate elements matching a given
        glob-style pattern
        :type pattern: str
        :param count: COUNT the user specified the amount of work that should be done at
        every call in order to retrieve elements from the collection
        :type count: int
        :returns:
        :rtype:
        """
        redis_command = "ZSCAN"
        pattern_list = []
        if pattern is not None:
            pattern_list.append("MATCH")
            pattern_list.append(pattern)

        count_list = []
        if count is not None:
            count_list.append("COUNT")
            count_list.append(count)

        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            cursor,
            *pattern_list,
            *count_list
        )

    def redis_zscore(self, key, member, collection):
        """
        Returns the sorted set cardinality (number of elements) of the sorted set stored
        at key.
        More on https://redis.io/commands/zscore/

        :param key: Key of the sorted set
        :type key: str
        :param member: Member of the sorted set
        :type member: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "ZSCORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            member
        )

    def redis_zunion(
            self,
            num_keys,
            keys,
            collection,
            options=None,
            with_scores=False
    ):
        """
        This command is similar to ZUNIONSTORE, but instead of storing the resulting
        sorted set, it is returned to the client. For a description of the WEIGHTS
        and AGGREGATE options, see ZUNIONSTORE.
        More on https://redis.io/commands/zunion/

        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZUNION options [WEIGHTS weight [weight ...]]
        [AGGREGATE <SUM | MIN | MAX>]
        :type options: list
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """
        options_command = []
        if options is not None:
            options_command = list(options)

        if with_scores is True:
            options_command.append("WITHSCORES")

        redis_command = "ZUNION"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            num_keys,
            *keys,
            *options_command,
        )

    def redis_zunionstore(
            self,
            destination,
            num_keys,
            keys,
            collection,
            options=None,
            with_scores=False
    ):
        """
        Computes the union of numkeys sorted sets given by the specified keys,
        and stores the result in destination. It is mandatory to provide the number
        of input keys (numkeys) before passing the input keys and the other (
        optional) arguments.
        By default, the resulting score of an element is the sum of its scores in the
        sorted sets where it exists.
        More on https://redis.io/commands/zunionstore/

        :param destination: Destination sorted set
        :type destination: str
        :param num_keys: Total number of input keys
        :type num_keys: int
        :param keys: List of keys of the sorted set
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Additional ZUNIONSTORE options [WEIGHTS weight [weight ...]]
        [AGGREGATE <SUM | MIN | MAX>]
        :type options: list
        :param with_scores: Return score of member
        :type with_scores: bool
        :returns:
        :rtype:
        """
        options_command = []
        if options is not None:
            options_command = list(options)

        if with_scores is True:
            options_command.append("WITHSCORES")

        redis_command = "ZUNIONSTORE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            destination,
            num_keys,
            *keys,
            *options_command,
        )

    def redis_copy(
            self,
            source,
            destination,
            collection,
            destination_database=None,
            replace=False
    ):
        """
        This command copies the value stored at the source key to the destination
        key. By default, the destination key is created in the logical database used
        by the connection. The DB option allows specifying an alternative logical
        database index for the destination key.
        More on https://redis.io/commands/copy/

        :param source: Source key to be copied
        :type source: str
        :param destination: Destination key to be copied
        :type destination: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param destination_database: DB location where data will be copied
        :type destination_database: str
        :param replace: Replace removes destination key before copying value to it
        :type replace: str
        :returns:
        :rtype:
        """
        options_command = []
        if destination_database is not None:
            options_command.append("DB")
            options_command.append(destination_database)

        if replace is True:
            options_command.append("WITHSCORES")

        redis_command = "COPY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            source,
            destination,
            *options_command
        )

    def redis_del(
            self,
            keys,
            collection,
    ):
        """
        Removes the specified keys. A key is ignored if it does not exist.
        More on https://redis.io/commands/del/

        :param keys: List of keys to be deleted
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "DEL"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys
        )

    def redis_exists(
            self,
            keys,
            collection,
    ):
        """
        Returns if key exists.
        More on https://redis.io/commands/exists/

        :param keys: List of keys to be checked
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "EXISTS"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys
        )

    def redis_expire(
            self,
            key,
            seconds,
            collection,
            options=None,
    ):
        """
        Set a timeout on key. After the timeout has expired, the key will
        automatically be deleted. A key with an associated timeout is often said to
        be volatile in Redis terminology.
        More on https://redis.io/commands/expire/

        :param key: Key of the data
        :type key: str
        :param seconds: Time until key expires
        :type seconds: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Options of expire command [NX | XX | GT | LT]
        :type options: str
        :returns:
        :rtype:
        """
        redis_command = "EXPIRE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            seconds,
            options
        )

    def redis_expireat(
            self,
            key,
            unix_time_seconds,
            collection,
            options=None,
    ):
        """
        EXPIREAT has the same effect and semantic as EXPIRE, but instead of
        specifying the number of seconds representing the TTL (time to live),
        it takes an absolute Unix timestamp (seconds since January 1, 1970). A
        timestamp in the past will delete the key immediately.
        More on https://redis.io/commands/expireat/

        :param key: Key of the data
        :type key: str
        :param unix_time_seconds: Time until key expires
        :type unix_time_seconds: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Options of expire command [NX | XX | GT | LT]
        :type options: str
        :returns:
        :rtype:
        """
        redis_command = "EXPIREAT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            unix_time_seconds,
            options
        )

    def redis_persist(
            self,
            key,
            collection
    ):
        """
        Remove the existing timeout on key, turning the key from volatile (a key with
        an expire set) to persistent (a key that will never expire as no timeout is
        associated).
        More on https://redis.io/commands/persist/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "PERSIST"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_pexpire(
            self,
            key,
            milliseconds,
            collection,
            options=None,
    ):
        """
        EXPIREAT has the same effect and semantic as EXPIRE, but instead of
        specifying the number of seconds representing the TTL (time to live),
        it takes an absolute Unix timestamp (seconds since January 1, 1970). A
        timestamp in the past will delete the key immediately.
        More on https://redis.io/commands/pexpire/

        :param key: Key of the data
        :type key: str
        :param milliseconds: Time until key expires
        :type milliseconds: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Options of expire command [NX | XX | GT | LT]
        :type options: str
        :returns:
        :rtype:
        """
        redis_command = "PEXPIRE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            milliseconds,
            options
        )

    def redis_pexpireat(
            self,
            key,
            unix_time_milliseconds,
            collection,
            options=None,
    ):
        """
        PEXPIREAT has the same effect and semantic as EXPIREAT, but the Unix time at
        which the key will expire is specified in milliseconds instead of seconds.
        More on https://redis.io/commands/pexpireat/

        :param key: Key of the data
        :type key: str
        :param unix_time_milliseconds: Time until key expires
        :type unix_time_milliseconds: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param options: Options of expire command [NX | XX | GT | LT]
        :type options: str
        :returns:
        :rtype:
        """
        redis_command = "PEXPIREAT"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            unix_time_milliseconds,
            options
        )

    def redis_pttl(
            self,
            key,
            collection,
    ):
        """
        Like TTL this command returns the remaining time to live of a key that has an
        expire set, with the sole difference that TTL returns the amount of remaining
        time in seconds while PTTL returns it in milliseconds.
        More on https://redis.io/commands/pttl/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "PTTL"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_randomkey(
            self,
            collection,
    ):
        """
        Return a random key from the currently selected database.
        More on https://redis.io/commands/randomkey/

        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RANDOMKEY"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
        )

    def redis_rename(
            self,
            key,
            new_key,
            collection
    ):
        """
        Renames key to newkey. It returns an error when key does not exist. If newkey
        already exists it is overwritten, when this happens RENAME executes an
        implicit DEL operation, so if the deleted key contains a very big value it
        may cause high latency even if RENAME itself is usually a constant-time
        operation.
        More on https://redis.io/commands/rename/

        :param key: Key to rename
        :type key: str
        :param new_key: New key name
        :type new_key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RENAME"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            new_key
        )

    def redis_renamenx(
            self,
            key,
            new_key,
            collection
    ):
        """
        Renames key to newkey if newkey does not yet exist. It returns an error when
        key does not exist. In Cluster mode, both key and newkey must be in the same
        hash slot, meaning that in practice only keys that have the same hash tag can
        be reliably renamed in cluster.
        More on https://redis.io/commands/renamenx/

        :param key: Key to rename
        :type key: str
        :param new_key: New key name
        :type new_key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "RENAMENX"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
            new_key
        )

    def redis_scan(
            self,
            cursor,
            collection,
            pattern=None,
            count=None,
            data_type=None
    ):
        """
        The SCAN command and the closely related commands SSCAN, HSCAN and ZSCAN are
        used in order to incrementally iterate over a collection of elements.
        More on https://redis.io/commands/scan/

        :param cursor: Cursor value (start with 0)
        :type cursor: int
        :param collection: Name of the collection that we set values to
        :type collection: str
        :param pattern: It is possible to only iterate elements matching a given
        glob-style pattern
        :type pattern: str
        :param count: COUNT the user specified the amount of work that should be done at
        every call in order to retrieve elements from the collection
        :type count: int
        :param data_type: You can use the TYPE option to ask SCAN to only return objects that
        match a given type, llowing you to iterate through the database looking for keys
        of a specific type ex. zset
        :type data_type: int
        :returns:
        :rtype:
        """
        pattern_list = []
        if pattern is not None:
            pattern_list.append("MATCH")
            pattern_list.append(pattern)

        count_list = []
        if count is not None:
            count_list.append("COUNT")
            count_list.append(count)

        type_list = []
        if data_type is not None:
            type_list.append("TYPE")
            type_list.append(data_type)

        redis_command = "SCAN"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            cursor,
            *pattern_list,
            *count_list,
            *type_list
        )

    def redis_ttl(
            self,
            key,
            collection,
    ):
        """
        Returns the remaining time to live of a key that has a timeout. This
        introspection capability allows a Redis client to check how many seconds a
        given key will continue to be part of the dataset.
        More on https://redis.io/commands/ttl/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "TTL"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_type(
            self,
            key,
            collection,
    ):
        """
        Returns the string representation of the type of the value stored at key. The
        different types that can be returned are: string, list, set, zset, hash and
        stream.
        More on https://redis.io/commands/type/

        :param key: Key of the data
        :type key: str
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "TYPE"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            key,
        )

    def redis_unlink(
            self,
            keys,
            collection,
    ):
        """
        This command is very similar to DEL: it removes the specified keys. Just like
        DEL a key is ignored if it does not exist. However the command performs the
        actual memory reclaiming in a different thread, so it is not blocking,
        while DEL is. This is where the command name comes from: the command just
        unlinks the keys from the keyspace. The actual removal will happen later
        asynchronously.
        More on https://redis.io/commands/unlink/

        :param keys: List of keys to be deleted
        :type keys: list
        :param collection: Name of the collection that we set values to
        :type collection: str
        :returns:
        :rtype:
        """
        redis_command = "UNLINK"
        return self._fabric.redis.command_parser(
            redis_command,
            collection,
            *keys
        )



