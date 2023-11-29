import pymongo
from dotenv import load_dotenv
import re
from Config.config import DatabaseConfig
from Config.logs_config import setup_logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

# Load environment variables from .env file
load_dotenv()

# Set up logging to a file
logger = setup_logging('database', DatabaseConfig.DATABASE_LOG_PATH)


def connect_db(database_name, collection_name):
    """Function to connect to a MongoDB database and return the collection object

    Args:
        database_name (string): The name of the database
        collection_name (string): The name of the collection

    Returns:
        pymongo.collection.Collection: The MongoDB collection object
    """
    try:
        # Connect to the MongoDB cluster
        client = MongoClient(DatabaseConfig.CONNECTION_STRING, maxPoolSize=5)
        db = client[database_name]
        collection = db[collection_name]
        return collection
    except ConnectionFailure as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


def connect_collection_db():
    """Function to connect to the MongoDB collection and return the collection object

    Returns:
        pymongo.collection.Collection: The MongoDB collection object
    """
    # Connect to the "Manga" database and "Collection" collection
    return connect_db("Anime", "Collection")


def create_index(collection):
    """Function to create an index on the 'title' field for better performance


    Args:
        collection (pymongo.collection.Collection): The MongoDB collection
    """
    # Create an index on the 'title' field
    collection.create_index([('title', pymongo.ASCENDING)])


def insert_to_db(collection, data):
    """Function to insert data into a MongoDB collection

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection
        data (list): The data to insert
    """
    try:
        if data:
            # Insert the data into the MongoDB collection
            collection.insert_many(data)
        else:
            logger.info("No data to insert")
    except pymongo.errors.DuplicateKeyError as e:
        logger.error(f"Error inserting data to MongoDB: {e}")
        raise  # Re-raise the exception to stop further execution
    except pymongo.errors.BulkWriteError as bwe:
        # Handle specific MongoDB write errors
        logger.error(f"MongoDB Bulk Write Error: {bwe.details}")
        raise
    except Exception as e:
        logger.error(f"Error inserting data into MongoDB collection: {e}")
        raise


def insert_anime_to_db(data):
    """Function to insert manga data such as the title, description and link into the MongoDB collection, using the insert_to_db function defined above

    Args:
        data (list): The manga's information to insert
    """
    if data:
        # Connect to the "Manga" database and "Collection" collection and insert the data
        insert_to_db(connect_collection_db(), data)
    else:
        logger.info("No data to insert")


def delete_duplicates(collection, duplicates_cursor):
    """
    Deletes extra occurrences of duplicate documents in a MongoDB collection.

    Args:
        collection (pymongo.collection.Collection): The MongoDB collection to remove duplicates from.
        duplicates_cursor (pymongo.command_cursor.CommandCursor): The cursor containing the duplicate documents.

    Returns:
        None
    """
    try:
        # Iterate over the duplicate documents and remove extra occurrences
        for duplicate_group in duplicates_cursor:
            # Get the extra occurrences
            extra_occurrences = duplicate_group['ids'][1:]
            # Delete the extra occurrences
            collection.delete_many({'_id': {'$in': extra_occurrences}})
    except Exception as e:
        logger.error(f"Error deleting duplicates: {e}")
        raise


def detect_duplicates():
    """
    Detect and remove duplicate documents in the MongoDB collection.

    This function connects to the "Manga" database and "Collection" collection,
    creates an index on the 'title' field for better performance, and uses a
    MongoDB aggregation pipeline to find and remove duplicates.

    Returns:
        None.

    Raises:
        pymongo.errors.PyMongoError: If there is an error while connecting to
            the database or executing the aggregation pipeline.
    """
    try:
        # Connect to the "Manga" database and "Collection" collection
        collection = connect_collection_db()

        # Create an index on the 'title' field for better performance
        create_index(collection)

        # MongoDB aggregation pipeline to find and remove duplicates
        duplicates_pipeline = [
            {
                '$group': {
                    '_id': '$title',
                    'count': {
                        '$sum': 1
                    },
                    'ids': {'$push': '$_id'}
                }
            }, {
                '$match': {
                    'count': {
                        '$gt': 1
                    }
                }
            }
        ]

        # Find all the duplicate documents
        duplicates_cursor = collection.aggregate(duplicates_pipeline)
        # Remove the duplicate documents
        delete_duplicates(collection, duplicates_cursor)
        print('Duplicates are now removed :)')
    except PyMongoError as e:
        logger.error(f"Error detecting duplicates: {e}")
        raise


def create_regex_pattern(input):
    """
    Create a regular expression pattern that matches any string containing the given input.

    Args:
        input (str): The input string to be escaped and used in the pattern.

    Returns:
        re.Pattern: A compiled regular expression pattern that matches any string containing the input.

    """
    return re.compile(f".*{re.escape(input)}.*", re.IGNORECASE)


def find_anime(input):
    """
    Find anime titles that match the given input.

    Args:
        input (str): The input string to search for.

    Returns:
        list: A list of dictionaries representing the matching anime titles, links, and statuses.
              Each dictionary contains the following fields: 'title', 'link', 'status'.

    Raises:
        Exception: If there is an error in the database connection or query execution.
    """
    try:
        # Connect to the "Manga" database and "Collection" collection
        collection = connect_collection_db()

        # Create a regex pattern for matching substrings of the input
        pattern = create_regex_pattern(input)

        # Use the regex pattern in the query to find matching documents and return only the title and link fields
        anime_cursor = collection.find(
            {'title': {'$regex': pattern}},
            {'_id': 0, 'title': 1, 'link': 1}
        )

        # Convert the cursor to a list
        animes = list(anime_cursor)
        # If there are matching documents
        if animes:
            # Prioritize titles that start with the input and sort the rest alphabetically
            animes.sort(key=lambda x: (
                not x['title'].lower().startswith(input.lower()), x['title']))
            return animes  # Return the list of matching documents
        else:
            # If there are no matching documents
            logger.info(f"No anime titles found matching '{input}'")

    except Exception as e:
        logger.error(f"Error in find_anime: {e}")
        return None
