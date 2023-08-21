import json
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
import random

def store_structure():
    # Set up database connection
    engine = create_engine('mysql+pymysql://root:@localhost/licenta-back')
    connection = engine.connect()
    meta = MetaData()

    # Load tables
    genders_table = Table('genders', meta, autoload_with=engine)
    categories_table = Table('categories', meta, autoload_with=engine)
    subcategories_table = Table('subcategories', meta, autoload_with=engine)
    articletypes_table = Table('articletypes', meta, autoload_with=engine)

    # Read structure from file
    with open('./resources/clean/structure.json', 'r') as f:
        structure = json.load(f)

    # Insert data from structure
    for gender_dict in structure['gender']:
        gender_name = list(gender_dict.keys())[0]
        gender_data = {'name': gender_name}
        result = connection.execute(genders_table.insert(), gender_data)
        gender_id = result.lastrowid

        for category in gender_dict[gender_name]['categories']:
            category_data = {'category_id': category['id'], 'name': category['name'], 'gender_id': gender_id}
            result = connection.execute(categories_table.insert(), category_data)
            category_id = result.lastrowid

            for subcategory in category['subCategories']:
                subcategory_data = {'subcategory_id': subcategory['id'],'name': subcategory['name'], 'category_id': category_id}
                result = connection.execute(subcategories_table.insert(), subcategory_data)
                subcategory_id = result.lastrowid

                for article_type in subcategory['articleTypes']:
                    article_type_data = {'articletype_id': article_type['id'],'name': article_type['name'], 'subcategory_id': subcategory_id}
                    connection.execute(articletypes_table.insert(), article_type_data)
    connection.commit()

def store_articles():
    # Set up database connection
    engine = create_engine('mysql+pymysql://root:@localhost/licenta-back')
    meta = MetaData()

    # Load tables
    articles_table = Table('articles', meta, autoload_with=engine)
    genders_table = Table('genders', meta, autoload_with=engine)
    categories_table = Table('categories', meta, autoload_with=engine)
    subcategories_table = Table('subcategories', meta, autoload_with=engine)
    articletypes_table = Table('articletypes', meta, autoload_with=engine)

    # Read structure from file
    with open('./resources/clean/articles.json', 'r') as f:
        articles = json.load(f)
    
    # Create a connection and initiate a transaction
    with engine.begin() as connection:
        # Insert each article into the 'articles' table
        for article in articles:
            # Fetch the gender_id from 'genders' table
            gender_name = article['gender']
            gender_query = select(genders_table.c.gender_id).where(genders_table.c.name == gender_name)
            gender_id = connection.execute(gender_query).scalar()

            # Fetch the category_id from 'categories' table
            master_category_id = article['masterCategoryId']
            category_query = select(categories_table.c.id).where(categories_table.c.category_id == master_category_id)
            category_id = connection.execute(category_query).scalar()

            # Fetch the subcategory_id from 'subcategories' table
            sub_category_id = article['subCategoryId']
            subcategory_query = select(subcategories_table.c.id).where(subcategories_table.c.subcategory_id == sub_category_id)
            subcategory_id = connection.execute(subcategory_query).scalar()

            # Fetch the articletype_id from 'articletypes' table
            article_type_id = article['articleTypeId']
            articletype_query = select(articletypes_table.c.id).where(articletypes_table.c.articletype_id == article_type_id)
            articletype_id = connection.execute(articletype_query).scalar()

            price = article['price'] // 7

            # Prepare data to be inserted
            article_data = {
                'article_id': article['id'],
                'size_0': article.get('size_0', "none"),
                'size_1': article.get('size_1', "none"),
                'size_2': article.get('size_2', "none"),
                'size_3': article.get('size_3', "none"),
                'size_4': article.get('size_4', "none"),
                'price': price,
                'discounted_price': article['discountedPrice'],
                'article_number': article['articleNumber'],
                'display_name': article['productDisplayName'],
                'brand_name': article['brandName'],
                'colour': article['baseColour'],
                'season': article['season'],
                'pattern': article.get('Pattern', "none") or "none",
                'usage': article['usage'],
                'default_image': article.get('defaultImageURL', '') or '',
                'first_image': article.get('backImageURL', '') or '',
                'second_image': article.get('frontImageURL', '') or '',
                'description': article.get('description') or '',
                'gender_id': gender_id,
                'category_id': category_id,
                'subcategory_id': subcategory_id,
                'articletype_id': articletype_id
            }

            for i in range(5):
                key_name = f"size_{i}_availability"
                size = f"size_{i}"
                if article_data[size] == "none":
                    article_data[key_name] = 0
                else:    
                    article_data[key_name] = random.randint(0,20)

            # Insert data
            connection.execute(articles_table.insert(), article_data)


