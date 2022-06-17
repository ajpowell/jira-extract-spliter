import re
import logging
import sys
import os
import errno
from jira import JIRA

'''
extract_attachments.py

Python script to process an Atlassian Jira export - then uses the jira API to
download all the attachments on a jira into a directory for the jira ticket

The input file is in ./source; the files are created in ./attachment.

'''

#     Ver    Author          Date       Comments
#     ===    =============== ========== =======================================
ver = 0.1  # Adrian Powell   2022-06-17 Initial code


# Initialise logging module
logging.root.handlers = []
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
    # level=logging.DEBUG
    )


def main():
    username = ''
    password = ''
    jira = JIRA('https://jira.int.support.awsplatform.co.uk/jira',
                auth=(username, password))

    # Open file
    # TODO: Support arguments for source file
    # TODO: Add check that source file exists
    f = open(
             './source/B4CASM_20190502-20191231.htm',
             # './source/B4CASM_20200101-20201231.htm',
             # './source/B4CASM_20210101-20211231.htm',
             # './source/B4CASM_20220101-2020616.htm',
             mode="r",
             encoding="utf-8")
    # TODO: Support arguments for output directory
    # TODO: Add check that output directory exists
    # output_directory = './output'

    hr_term = '<hr class="fullcontent">'
    h3_term = '<h3 class="formtitle">'
    table_term = '<table class="tableBorder"'
    attach_term = 'https://jira.int.support.awsplatform.co.uk/jira/secure/attachment/'  # noqa E501

    line_number = 0
    document_count = 0
    attachment_count = 0
    name_flag = 0

    for line in f:
        line_number = line_number + 1

        if name_flag == 1:
            # This line will hold the ticket number and title
            # print('line: {}'.format(line))
            # Parse out the ticket number
            pattern = '\[([^\[]*)\]'  # noqa W605
            match = re.search(pattern, line)
            if match:
                # print(match.group()[1:-1:])
                ticket_number = match.group()[1:-1:]

            # Parse out the title
            pattern = '>(.*)<'
            match = re.search(pattern, line)
            if match:
                # print(match.group()[1:-1:])
                ticket_title_tmp = match.group()[1:-1:]
                if ticket_title_tmp != '':
                    ticket_title = ticket_title_tmp
            logging.info('Jira: {} - Title: {}'
                         .format(ticket_number, ticket_title))

            name_flag = 0

        if line.find(table_term) != -1:
            # Start of document..
            document_count = document_count + 1
            # Reset the current_document
            logging.debug('')
            logging.debug('..line {}; document {} => {}'
                          .format(line_number, document_count, table_term))

        if line.find(h3_term) != -1:
            name_flag = 1
            logging.debug('..line {}; document {} => {}'
                          .format(line_number, document_count, h3_term))

        if line.find(hr_term) != -1:
            # End of document
            issue = jira.issue(ticket_number)
            for attachment in issue.fields.attachment:
                # print("> Name: '{filename}', size: {size}".format(
                # filename=attachment.filename, size=attachment.size))
                # to read content use `get` method:
                attachment_filepath = './attachments/' + \
                                      ticket_number + '/' + \
                                      attachment.filename
                logging.info('Writing {}'.format(attachment_filepath))

                directories = os.path.dirname(attachment_filepath)

                # create directories if not present
                try:
                    os.makedirs(directories)
                except OSError as exc:
                    if exc.errno == errno.EEXIST \
                            and os.path.isdir(directories):
                        # Ignore the error if this is the directory
                        # already exists
                        pass

                f = open(attachment_filepath, 'wb')
                f.write(attachment.get())
                f.close()
                attachment_count = attachment_count + 1

    print('')
    logging.info('Parsed {} documents.'.format(document_count))
    logging.info('Downloaded {} attachments.'.format(attachment_count))
    print('')

    f.close()


if __name__ == "__main__":
    logging.info('{} v.{}'.format(sys.argv[0], ver))
    logging.info('')

    main()
