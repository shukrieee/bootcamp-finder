import sys

import yaml
from logger import logger


CITY_REQUIRED_KEYS = {
    'display_name': {str},
    'slug': {str},
    'state': {str},
}

CITY_OPTIONAL_KEYS = {
    'description': {str},
    'featured': {bool},
    'meta_description': {str},
}

TOPIC_REQUIRED_KEYS = {
    'description': {str},
    'display_name': {str},
    'meta_description': {str},
    'slug': {str},
}

TOPIC_OPTIONAL_KEYS = {
    'featured': {bool},
}


def main():
    errors = []
    cities = yaml.load(open('cities.yml', 'r'))
    for city in cities:
        missing_keys = set.difference(set(CITY_REQUIRED_KEYS), set(city))
        if missing_keys:
            errors.append(
                '[cities.yml] {} missing required key(s): {}'.format(
                    city.get('display_name') or city.get('slug'),
                    missing_keys))
        optional_present = set.intersection(set(CITY_OPTIONAL_KEYS), set(city))
        if optional_present:
            invalid_keys = [
                key for key in optional_present if type(city.get(key)) not in
                CITY_OPTIONAL_KEYS.get(key)]
            if invalid_keys:
                errors.append(
                    '[cities.yml] Invalid values for key(s): {} ({})'.format(
                        invalid_keys, city.get('display_name')))

    topics = yaml.load(open('topics.yml', 'r'))
    for topic in topics:
        missing_keys = set.difference(set(TOPIC_REQUIRED_KEYS), set(topic))
        if missing_keys:
            errors.append(
                '[topics.yml] {} missing required key(s): {}'.format(
                    topic.get('display_name') or topic.get('slug'),
                    missing_keys))
        optional_present = set.intersection(
            set(TOPIC_OPTIONAL_KEYS), set(topic))
        if optional_present:
            invalid_keys = [
                key for key in optional_present if type(topic.get(key)) not in
                TOPIC_OPTIONAL_KEYS.get(key)]
            if invalid_keys:
                errors.append(
                    '[topics.yml] Invalid values for key(s): {} ({})'.format(
                        invalid_keys, topic.get('display_name')))

    return errors


if __name__ == '__main__':
    errors = main()
    if errors:
        logger.error('\n{}\n'.format('\n'.join(errors)))
        sys.exit(1)

    sys.exit(0)
