import os
import shutil

import yaml
from logger import logger

BOOTCAMPS_FOLDER_LOCAL = 'bootcamps'


def boolify_key(data, key):
    """Convert string keys 'Yes' and 'No' to True and False."""
    if data.get(key) == 'Yes':
        return True
    return False


def convert_program_data(bootcamp_slug, program_slug):
    """Generate a dict of data for a bootcamp program.

    :param bootcamp_slug: ``str`` slug of the bootcamp
    :param program_slug: ``str`` slug of the program
    """
    program_folder = '{}/{}-legacy/programs/{}'.format(
        BOOTCAMPS_FOLDER_LOCAL, bootcamp_slug, program_slug)

    with open('{}/data.yml'.format(program_folder), 'r') as f:
        data = yaml.load(f.read())

    with open('{}/description.md'.format(program_folder), 'r') as f:
        description = f.read()

    data.update({'description': u'{}'.format(description.decode('utf-8'))})

    # Ensure program_slug is correct
    if data.get('program_slug') != program_slug:
        logger.warn(
            'Updating program slug for {} from {} to {}'.format(
                bootcamp_slug, program_slug, data.get('program_slug')))

    slug = data.pop('program_slug')

    # Rename/remove keys to fit new style
    data.pop('tution_units', None)
    data.pop('reviews', None)
    data.pop('promises_job', None)
    data['reports_outcomes'] = data.pop(
        'reports_graduation_and_placement_rates', False)

    # Boolean-ify keys that were 'Yes' and 'No' strings
    data['financing'] = boolify_key(data, 'financing')
    data['guarantee'] = boolify_key(data, 'guarantee')
    data['reports_outcomes'] = boolify_key(data, 'reports_outcomes')
    data['outcomes_verified'] = boolify_key(data, 'outcomes_verified')

    return slug, data


def convert_bootcamp_data(slug):
    """Convert a bootcamp's folder from the old format to the new."""
    success = True

    # Rename existing folder as `slug`-legacy
    legacy_folder = '{}/{}-legacy'.format(BOOTCAMPS_FOLDER_LOCAL, slug)
    shutil.move(
        '{}/{}/'.format(BOOTCAMPS_FOLDER_LOCAL, slug),
        legacy_folder)

    # Create new empty `slug` folder
    os.mkdir('{}/{}'.format(BOOTCAMPS_FOLDER_LOCAL, slug))

    # Copy logo over to new folder
    shutil.copy(
        '{}/logo.png'.format(legacy_folder),
        '{}/{}/logo.png'.format(BOOTCAMPS_FOLDER_LOCAL, slug))

    # Compile bootcamp's and its programs' data.yml and description.md files
    # into one and write back to single data.yml file in new folder
    with open('{}/data.yml'.format(legacy_folder), 'r') as f:
        data = yaml.load(f.read())

    with open(
            '{}/description.md'.format(legacy_folder), 'r') as f:
        description = f.read()

    data.update({'description': u'{}'.format(description.decode('utf-8'))})
    data.update({'programs': {}})

    all_programs = os.listdir('{}/programs'.format(legacy_folder))
    for program in all_programs:
        try:
            program_slug, program_dict = convert_program_data(slug, program)
            data['programs'][program_slug] = program_dict
        except AssertionError as exc:
            success = False
            logger.error(
                '[convert_bootcamp_data] Error in program {} for {}: '
                '{}'.format(slug, program, exc))

    with open('{}/{}/data.yml'.format(BOOTCAMPS_FOLDER_LOCAL, slug), 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

    # Remove legacy folder if successful
    if success:
        shutil.rmtree(legacy_folder)

    return success


def main():
    success = []
    failure = []
    all_bootcamps = os.listdir('./bootcamps/')
    for bootcamp_slug in all_bootcamps:
        succeeded = convert_bootcamp_data(bootcamp_slug)
        if succeeded:
            success.append(bootcamp_slug)
        else:
            failure.append(bootcamp_slug)

    logger.info(
        '[main] {} bootcamps successfully migrated. {} failures: {}'.format(
            len(success), len(failure), failure))


if __name__ == '__main__':
    main()
