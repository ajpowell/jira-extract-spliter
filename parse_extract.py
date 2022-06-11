import re
import logging
import sys

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

    <link rel='stylesheet' href='../jira.css'>
        </head>
        <body>"""  # noqa 501

    return html_header1 + html_header2 + html_header3


def html_page_footer():
    html_footer = """
        </body>
    </html>
    """
    return html_footer


def main():
    # Open file
    # TODO: Support arguments for source file
    # TODO: Add check that source file exists
    f = open('./source/B4CASMPI_AllQOZBTickets.htm',
             mode="r",
             encoding="utf-8")
    # TODO: Support arguments for output directory
    # TODO: Add check that output directory exists
    output_directory = './output'
    
    hr_term = '<hr class=\'fullcontent\'>'
    h3_term = '<h3 class="formtitle">'
    table_term = '<table class="tableBorder"'

    line_number = 0
    document_count = 0
    name_flag = 0
    current_document = ''

    for line in f:
        line_number = line_number + 1

        if name_flag == 1:
            # This line will hold the ticket number and title
            # print('{}'.format(line))
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
                ticket_title = match.group()[1:-1:]
            print('Jira: {} - Title: {}'.format(ticket_number, ticket_title))

            name_flag = 0

        if line.find(table_term) != -1:
            # Start of document..
            document_count = document_count + 1
            # Reset the current_document
            current_document = ''
            print('')
            print('..line {}; document {} => {}'.format(line_number,
                                                        document_count,
                                                        table_term))

        if line.find(h3_term) != -1:
            name_flag = 1
            print('..line {}; document {} => {}'.format(line_number,
                                                        document_count,
                                                        h3_term))

        if line.find(hr_term) != -1:
            # End of document
            # Write document to a new file using the number and title
            # that should have been parsed.
            # TODO: Add checks that we have ticket_number and
            # ticket_title...revert to document number if not!
            output_filename = output_directory + '/' + \
                              ticket_number + \
                              ' - ' + ticket_title + '.htm'
            with open(output_filename, 'w') as f_output:
                f_output.write(html_page_header(ticket_number))
                f_output.write(current_document)
                f_output.write(html_page_footer())
            
            # TODO: update stats for documents created

            print('..line {}; document {} => {}'.format(line_number,
                                                        document_count,
                                                        hr_term))
        # Add line to the current document
        current_document = current_document + '\n' + line

    f.close()


if __name__ == "__main__":
    logging.info('{} v.{}'.format(sys.argv[0], ver))
    main()
