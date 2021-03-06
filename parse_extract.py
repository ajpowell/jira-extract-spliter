import re
import logging
import sys
import html
import shutil
import os
import requests
import errno

'''
parse_extract.py

Python script to split out a Atlassian Jira export - file was exported as
a doc file, but is really just an html file. This script will split out the
file into individual pages for each Jira ticket - note that any attachments
(images, files etc) are lost (a limitation of the export process).

The input file is in ./source; the files are created in ./output.

'''

#     Ver    Author          Date       Comments
#     ===    =============== ========== =======================================
ver = 0.1  # Adrian Powell   2022-06-11 Initial code
ver = 0.2  # Adrian Powell   2022-06-13 Updated to exclude invalid chars from
#                                       filename
ver = 0.3  # Adrian Powell   2022-06-16 Download attachments

# Initialise logging module
logging.root.handlers = []
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
    # level=logging.DEBUG
    )


def html_page_header(ticket_number):
    html_header1 = """
    <!DOCTYPE html>
        <html>
        <head>"""
    html_header2 = '<title>{}</title>'.format(ticket_number)
    html_header3 = """<meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <!-- Bootstrap CSS -->
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css' rel='stylesheet' crossorigin='anonymous'>

    <link rel='stylesheet' href='./jira.css'>
        </head>
        <body>"""  # noqa 501

    return html_header1 + html_header2 + html_header3


def html_page_footer():
    html_footer = """
        </body>
    </html>
    """
    return html_footer


def download_attachment(source_url, target_filepath):
    # Download the file into memory
    response = requests.get(source_url, stream=True)
    logging.info('status: {}; size: {}'.format(response.status_code, response.headers))

    filename = os.path.basename(target_filepath)
    directories = os.path.dirname(target_filepath)

    logging.info('directories:{}'.format(directories))
    # Create the sub directories
    try:
        os.makedirs(directories)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(directories):
            # Ignore the error if this is the directory already exists
            pass

    logging.info('filepath:{}: filename:{}'.format(target_filepath, filename))
    # Write out the file
    with open(target_filepath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def main():
    # Open file
    # TODO: Support arguments for source file
    # TODO: Add check that source file exists
    f = open('./source/ASMCurrentIssues.htm',
             mode="r",
             encoding="utf-8")
    # TODO: Support arguments for output directory
    # TODO: Add check that output directory exists
    output_directory = './output'

    hr_term = '<hr class="fullcontent">'
    h3_term = '<h3 class="formtitle">'
    table_term = '<table class="tableBorder"'
    attach_term = 'https://jira.int.support.awsplatform.co.uk/jira/secure/attachment/'  # noqa E501

    line_number = 0
    document_count = 0
    name_flag = 0
    current_document = ''

    for line in f:
        line_number = line_number + 1

        if name_flag == 1:
            # This line will hold the ticket number and title
            print('line: {}'.format(line))
            # Parse out the ticket number
            pattern = '\[(.*)\]'  # noqa W605
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
                print(match.group())
                if ticket_title_tmp != '':
                    ticket_title = ticket_title_tmp
            logging.info('Jira: {} - Title: {}'
                          .format(ticket_number, ticket_title))

            name_flag = 0

        if line.find(table_term) != -1:
            # Start of document..
            document_count = document_count + 1
            # Reset the current_document
            current_document = ''
            logging.debug('')
            logging.debug('..line {}; document {} => {}'
                          .format(line_number, document_count, table_term))

        if line.find(h3_term) != -1:
            name_flag = 1
            logging.debug('..line {}; document {} => {}'
                          .format(line_number, document_count, h3_term))

        if line.find(attach_term) != -1:
            name_flag = 1
            logging.debug('..line {}; document {} => {}'
                          .format(line_number, document_count, line))
            # Parse out the link
            attachment_url = ''
            pattern = 'href=\"' + attach_term + '[^"]*\" '
            match = re.search(pattern, line)
            if match:
                # print(match.group()[1:-1:])
                attachment_url = match.group()[6:-2:]
                attachment_path_start = attachment_url.find('/attachment/')
                new_attachment_url = './output' + attachment_url[attachment_path_start:]

                # download_attachment(attachment_url, new_attachment_url)

                # TODO: Fix url in the current line to match the new_attachment_url
                # logging.info('>> {}'.format(line))
                line = line.replace(attach_term, './attachment/')
                # logging.info('>> {}'.format(line))

            logging.info('>> {}'.format(attachment_url))
            logging.info('>> {}'.format(new_attachment_url))

        if line.find(hr_term) != -1:
            # End of document
            # Write document to a new file using the number and title
            # that should have been parsed.
            # TODO: Add checks that we have ticket_number and
            # ticket_title...revert to document number if not!

            # Convert utf-8 string to ascii for filename
            # tmp_data=ticket_title.decode("utf-8")
            ticket_title_bytes = bytes(ticket_title, 'utf-8')
            ticket_title_ascii = ticket_title_bytes.decode("ascii", "ignore")

            # Unescape htm sequences (like '&amp;' => '&')
            ticket_title_ascii_unescaped = html.unescape(ticket_title_ascii)

            # Handle characters that are no valid in filenames
            character_list = ['*', '.', '"', '/', '\\', '[', ']', ':', ';',
                              '|', ',', '>', '<', '?', '!', '&', '#']
            for char in character_list:
                ticket_title_ascii_unescaped = \
                    ticket_title_ascii_unescaped.replace(char, '_')

            output_filename = output_directory + '/' + \
                ticket_number + \
                ' - ' + ticket_title_ascii_unescaped + '.htm'
            logging.info('{} - Writing \"{}\"...'
                         .format(document_count, output_filename))
            with open(output_filename, mode='w', encoding="utf-8") as f_output:
                f_output.write(html_page_header(ticket_number))
                f_output.write(current_document)
                f_output.write(html_page_footer())

            # TODO: update stats for documents created

            logging.debug('..line {}; document {} => {}'.format(line_number,
                                                                document_count,
                                                                hr_term))
        # Add line to the current document
        current_document = current_document + '\n' + line

    print('')
    logging.info('Created {} documents.'.format(document_count))
    print('')

    f.close()


if __name__ == "__main__":
    logging.info('{} v.{}'.format(sys.argv[0], ver))
    logging.info('')

    main()
