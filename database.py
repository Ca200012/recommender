import json
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
import random

def store_structure():
    engine = create_engine('mysql+pymysql://root:@localhost/licenta-back')
    connection = engine.connect()
    meta = MetaData()

    genders_table = Table('genders', meta, autoload_with=engine)
    categories_table = Table('categories', meta, autoload_with=engine)
    subcategories_table = Table('subcategories', meta, autoload_with=engine)
    articletypes_table = Table('articletypes', meta, autoload_with=engine)

    with open('./resources/clean/structure.json', 'r') as f:
        structure = json.load(f)

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
    engine = create_engine('mysql+pymysql://root:@localhost/licenta-back')
    meta = MetaData()

    articles_table = Table('articles', meta, autoload_with=engine)
    genders_table = Table('genders', meta, autoload_with=engine)
    categories_table = Table('categories', meta, autoload_with=engine)
    subcategories_table = Table('subcategories', meta, autoload_with=engine)
    articletypes_table = Table('articletypes', meta, autoload_with=engine)

    with open('./resources/clean/articles.json', 'r') as f:
        articles = json.load(f)
    
    with engine.begin() as connection:
        for article in articles:
            gender_name = article['gender']
            gender_query = select(genders_table.c.gender_id).where(genders_table.c.name == gender_name)
            gender_id = connection.execute(gender_query).scalar()

            master_category_id = article['masterCategoryId']
            category_query = select(categories_table.c.id).where(
                (categories_table.c.category_id == master_category_id) &
                (categories_table.c.gender_id == gender_id)
            )
            category_id = connection.execute(category_query).scalar()

            sub_category_id = article['subCategoryId']
            subcategory_query = select(subcategories_table.c.id).where(
                (subcategories_table.c.subcategory_id == sub_category_id) &
                (subcategories_table.c.category_id == category_id)
            )
            subcategory_id = connection.execute(subcategory_query).scalar()

            article_type_id = article['articleTypeId']
            articletype_query = select(articletypes_table.c.id).where(
                (articletypes_table.c.articletype_id == article_type_id) &
                (articletypes_table.c.subcategory_id == subcategory_id)
            )
            articletype_id = connection.execute(articletype_query).scalar()

            price = article['price'] // 7

            size_mapping = {
                'S': 'size_S',
                'M': 'size_M',
                'L': 'size_L',
                'XL': 'size_XL',
                'XXL': 'size_XXL'
            }

            article_data = {
                'article_id': article['id'],
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

            for standard_size, key_name in size_mapping.items():
                article_data[key_name] = article.get(key_name, "none")
                if standard_size in [article.get(f'size_{i}') for i in range(5)]:
                    article_data[key_name] = standard_size
                else:
                    article_data[key_name] = "none"


            for standard_size, key_name in size_mapping.items():
                size_availability_key = f"{key_name}_availability"
                if article_data[key_name] == "none":
                    article_data[size_availability_key] = 0
                else:
                    article_data[size_availability_key] = random.randint(0,20)

            connection.execute(articles_table.insert(), article_data)
